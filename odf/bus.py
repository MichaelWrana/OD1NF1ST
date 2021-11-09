from odf.components import BusABC, Device, Word
from multiprocessing.managers import SyncManager, NamespaceProxy
from queue import Queue
from typing import List
import types


class QueueBus(BusABC):
    def __init__(self, devices) -> None:
        self.devices = devices

    def write(self, device: Device, words: List[Word]):
        if not isinstance(words, list):
            words = [words]
        for d in self.devices.values():
            for word in words:
                d.queue.put(word)

    def recv(self, device: Device) -> Word:
        return self.devices[device.id].queue.get()


class QueueBusProxy(NamespaceProxy):
    _exposed_ = tuple(dir(QueueBus))

    def __getattr__(self, name):
        result = super().__getattr__(name)
        if isinstance(result, types.MethodType):
            def wrapper(*args, **kwargs):
                return self._callmethod(name, args)
            return wrapper
        return result


SyncManager.register('QueueBus', QueueBus, QueueBusProxy)
