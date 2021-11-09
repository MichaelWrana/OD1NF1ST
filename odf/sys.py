import queue
import types
from multiprocessing import Manager, Pool, Process, managers
from multiprocessing.managers import BaseManager, NamespaceProxy, SyncManager

from odf.components import *
from odf.events import *
from odf.bus import *
from odf.proxy import *
from odf.config import config
from jsonpickle import dumps
import traceback


def run_device(device: Device):
    sock = None
    sock_trans = None
    handlers = {}

    try:
        @delay
        def write(word: Word):
            """
            process local writer vs device.write which is proxy manager's writer
            """
            if not isinstance(word, list):
                word = [word]
            for w in word:
                w: Word
                w.fake = device.fake
                for d in device.bus.values():
                    if d.port > 0 and d.port != device.port:
                        sock_trans.sendto(w.to_bytes(), ('127.0.0.1', d.port))

        log.info('listening at ' + device.name())

        sock_trans = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_trans.bind(('', 0))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        device.port = sock.getsockname()[1]

        def event_loop():
            while True:
                data, _ = sock.recvfrom(512)
                word = Word.from_bytes(data)
                yield Event_WORD_REC(device, word)
                '''
                if not word.check_parity():
                    yield Event_ERR_PARITY(device, word)
                '''
                yield from route_Event(device, word)
                # add other routes here
        while True:
            for e in event_loop():
                e_class = e.__class__.__name__
                if not isinstance(e, Event_WORD_REC) or config.SYS_LOG_EVENT_WORD_REC:
                    if config.SYS_LOG_EVENT:
                        e.log('{}', e.word)
                try:
                    e.write = write
                    if e_class in handlers:
                        handlers[e_class](e)
                    elif e_class in device.event_handlers:
                        handler = device.event_handlers[e_class]
                        # cache
                        handlers[e_class] = handler
                        handler(e)
                    else:
                        e()
                except Exception as e:
                    log.error(traceback.format_exc())
                    pass
    except Exception as e:
        if sock:
            sock.close()
        if sock_trans:
            sock_trans.close()
        log.error(traceback.format_exc())
        # raise e


class DeviceProxy(NamespaceProxy):
    _exposed_ = tuple(dir(Device))

    def __getattr__(self, name):
        result = super().__getattr__(name)
        if isinstance(result, types.MethodType):
            def wrapper(*args, **kwargs):
                return self._callmethod(name, args, kwargs)
            return wrapper
        return result

    def set_state(self, state):
        '''
        this is to avoid too many processes locking in the __getattr__ method
        I think each method of the proxy has its own lock
        If we just use __getattr__ for all the methods, all methods will share
        the same lock, which causing a lot of timeout and connection refuse
        '''
        self._callmethod('set_state', [state])


SyncManager.register('Device', Device, DeviceProxy)


class System():
    def __init__(self, name, port=8559, max_devices=64, with_bc=False) -> None:
        self.manager = SyncManager()
        self.manager.start()
        self.port = port
        self.max_devices = max_devices
        self.devices = self.manager.dict()
        self.async_results = []
        self.pool = Pool(self.max_devices)
        self.name = name
        self.bc = None

        if with_bc:
            self.bc = self.add_device(mode=Mode.BC)

    def add_device(
            self, mode=Mode.RT, address=-1, state=State.IDLE,
            **other_attributes) -> Device:
        if address < 0:
            address = len(self.devices.keys())
        if len(self.devices.keys()) > self.max_devices:
            raise ValueError(
                'System already maxed out all devices. {}'.format(
                    self.max_devices))

        device = self.manager.Device(
            bus=self.devices,
            mode=mode,
            address=address,
            state=state,
            queue=self.manager.Queue(),
            system=self.name,
            ** other_attributes
        )
        self.devices[device.id] = device
        res = self.pool.apply_async(func=run_device, args=(device,))
        self.async_results.append(res)
        return device

    def join(self):
        return [r.wait() for r in self.async_results]

    def shutdown(self):
        self.pool.terminate()
        self.pool.close()
        self.manager.shutdown()
