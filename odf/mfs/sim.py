import logging
import logging as log
import os
import threading
import time
from bisect import bisect_left
from typing import List, NamedTuple, Tuple

from odf.components import Data, Device, Mode, State
from odf.events import Event_RT_REC_DATA, Event_RT_TRS_CMD, Event_WORD_REC
from odf.sabotage import *
from odf.sys import System
from odf.config import config
from odf.utils import load_class
from odf.ids.defines import IDS
import cv2
import pandas as pd
import json
from time import sleep


class Feed:
    def __init__(self, sources, descriptions, data=None) -> None:
        # list of data source:str
        self.sources = sources
        # descriptions of the source
        self.descriptions = descriptions
        self.data = data
        # data format: [(milisecond, s0, s1, ...., sn),...]
        # different readings of different timestamp

    def retrieve(self, clock):
        # bisect search for the current
        # clock (offset: current_time - start_time in milisecond)
        idx = bisect_left(self.data, (clock, ))
        if idx < len(self.data):
            return self.data[idx][1:]
        return self.data[-1][1:]

    def get_dword_count(self):
        if self.data:
            assert len(self.data[0]) == len(self.sources) + 1
            return (len(self.data[0]) - 1) * 2
        return 0


class Gadget:

    def __init__(self, name, feed: Feed, system: System) -> None:
        # each gadget is associated with a RT.
        self.rt = system.add_device(state=State.OFF)
        self.name = name
        self.feed = feed

    def reading(self):
        pass

    def to_dict(self,):
        return {
            'd_type': self.__class__.__name__,
            'name': self.name,
            'sources': self.feed.sources,
            'descriptions': self.feed.descriptions,
        }


class Sensor(Gadget):
    def __init__(self, name, feed: Feed, system: System) -> None:
        super().__init__(name, feed, system)
        self.rt.on(Event_RT_TRS_CMD, self.on_Event_RT_TRS_CMD)
        self.rt.on(Event_RT_REC_DATA, self.on_Event_RT_REC_DATA)

    def on_Event_RT_TRS_CMD(self, event: Event_RT_TRS_CMD):
        # values is the list of numbers (sensor reading)
        values = self.feed.retrieve(event.source.clock())
        # pack values into bytes using f32 encoding
        words = Data.pack(values, is_float=True)
        event.words = words
        val_str = ', '.join(["{:5.2f}".format(v) for v in values])
        log.info(f'{self.name} send {val_str}')
        event()

    def on_Event_RT_REC_DATA(self, event: Event_RT_REC_DATA):
        if event.source.in_brdcst:
            log.info(f'{self.name} recv boardcast message')
        event()


class Gauge(Gadget):
    def __init__(self, name, feed: Feed, system: System, is_map=False) -> None:
        super().__init__(name, feed, system)
        self.is_map = is_map
        self.memory = []
        self.rt.on(Event_RT_REC_DATA, self.on_Event_RT_REC_DATA)

    def on_Event_RT_REC_DATA(self, event: Event_RT_REC_DATA):
        if event.source.in_brdcst:
            log.info(f'{self.name} recv boardcast message')
            event()
        else:
            event()
            w: Data
            w = event.word
            self.memory.append(w.get_data())
            if self.rt.dword_count == self.rt.dword_expected and self.rt.dword_count == len(self.memory):
                # unpack byte sequences into list of floats
                # a single float requires two words (two Data object)
                values = Data.unpack(
                    self.memory, is_float=True)
                val_str = ', '.join(["{:5.2f}".format(v) for v in values])
                log.info(f'{self.name} recv {val_str}')
                self.memory.clear()
                # self.rt.mem_reset()
                self.rt.store_set(values)

    def get_data(self):
        return self.rt.store_get()


class Monitor():
    def __init__(self, system: System, name='monitor', ids: IDS = None) -> None:
        self.rt = system.add_device(state=State.OFF, mode=Mode.BM)
        self.name = name
        self.data = None
        self.ids = ids
        self.rt.on(Event_WORD_REC, self.on_Event_WORD_REC)

    def on_Event_WORD_REC(self, event: Event_WORD_REC):
        t = self.rt.clock()
        w = event.word
        self.rt.store_append([t, w])
        if self.ids:
            # ids
            if not self.ids.prepared:
                self.ids.prepare()
            res = self.ids.monitor(t, w)
            self.rt.store_set(res, key='ids')
        # also trigger the default event handler below:
        event()

    def get_data(self):
        return self.rt.store_get()

    def get_ids(self):
        vals = self.rt.store_get('ids')
        return vals

    def log_data(self):
        for d in self.get_data():
            log.info(d)


class Sim(threading.Thread):
    def __init__(self, name='', max_device=64, recording_file=None) -> None:
        threading.Thread.__init__(self)
        self.system = System(
            name+'::1553', max_devices=max_device, with_bc=True)
        self.gadgets: List[Gadget] = []
        self.monitors: List[Monitor] = []
        self.map: List[Tuple[Gadget, Gadget, int]] = []
        self.attacks: List[Sabotage] = []
        self.running = False
        self.start_time = None
        bc_health = ['err_boardcast_timeout', 'err_rt2rt_timeout']
        self.bus_gauge = Gauge('gauge_bc', Feed(
            sources=bc_health, descriptions=bc_health
        ), self.system)
        self.gadgets.append(self.bus_gauge)
        self.vidcap = None
        self.recording_file = recording_file

    def clock_ms(self):
        return 0 if not self.start_time else (datetime.now() - self.start_time)/timedelta(milliseconds=1)

    def clock_s(self):
        return 0 if not self.start_time else (datetime.now() - self.start_time).total_seconds()

    def add_feed(self, name, feed: Feed, is_map=False):
        sensor = Sensor('sensor_'+name, feed, self.system)
        gague = Gauge('gauge_'+name, feed, self.system, is_map=is_map)
        self.gadgets.append(sensor)
        self.gadgets.append(gague)
        self.map.append((sensor, gague, feed.get_dword_count()))

    def read(self):
        return [g.get_data() for g in self.gadgets if isinstance(g, Gauge)]

    def get_guages(self):
        return [g.to_dict() for g in self.gadgets if isinstance(g, Gauge)]

    def sabotage(self, attack_class=None, attack_arguments={}, random_delay=-1):
        if random_delay > 0:
            sleep(random_delay)
        if attack_class is None:
            attack_class = random.choice(all_attacks)
            log.info(f'Randomly picked one attack: {attack_class}')
        if isinstance(attack_class, str):
            attack = [a for a in all_attacks if a.__name__ == attack_class.strip()
                      ][0](**attack_arguments)
        else:
            attack = attack_class(**attack_arguments)
        attack: Sabotage
        self.attacks.append(attack)
        attack.go(self.system, starting_time=self.monitors[0].rt.clock_start)

    def dump_monitor(self, saved=False):
        data = self.monitors[0].get_data()
        attack_time = [a.rt.store_get('attack_time') for a in self.attacks]
        attack_tpyes = [a.__class__.__name__ for a in self.attacks]
        json_str = jsonpickle.encode(
            {
                'data': data,
                'attack_times': attack_time,
                'attack_types': attack_tpyes,
                'attack_outcome': [a.rt.success for a in self.attacks]
            }
        )
        if not saved:
            return json_str
        else:
            data_file = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.json')
            with open(os.path.join(config.DATA_PATH, 'dump', data_file), 'w') as wf:
                wf.write(json_str)

    def get_ids(self,):
        # intrusion detection result from monitor
        return self.monitors[0].get_ids()

    def add_monitor(self, name='monitor', ids=None):
        m = Monitor(self.system, name, ids=ids)
        self.monitors.append(m)
        return m

    def shutdown(self):
        if self.vidcap:
            self.vidcap.release()
        self.running = False
        self.system.shutdown()

    def run(self):
        if self.running:
            return
        self.running = True
        self.start_time = datetime.now()
        for g in self.gadgets:
            g.rt.set_state(State.IDLE)
        err_bc_timeout = 0
        err_rt2rt_timeout = 0
        while self.running:
            if self.system.bc.state == State.IDLE:

                # major event
                self.system.bc.act_bc2rt(31, [Data(0xffff)])
                timeout = 0
                while self.running and self.system.bc.state != State.IDLE:
                    timeout += 0.001
                    if timeout > 1:
                        log.error(
                            f'bc timeout while handling boardcast')
                        err_bc_timeout += 1
                        self.system.bc.state = State.IDLE
                    time.sleep(0.01)

                # sensor reading
                for s, g, d in self.map:
                    self.system.bc.act_rt2rt(
                        s.rt.address, g.rt.address, d)
                    timeout = 0
                    while self.running and self.system.bc.state != State.IDLE:
                        timeout += 0.001
                        if timeout > 1:
                            log.error(
                                f'bc timeout while handling {s.name} {g.name}')
                            err_rt2rt_timeout += 1
                            self.system.bc.state = State.IDLE
                        time.sleep(0.01)
                        pass

                # bc status
                self.system.bc.act_bc2rt(
                    self.bus_gauge.rt.address,
                    Data.pack([err_bc_timeout, err_rt2rt_timeout], is_float=True))
                while self.running and self.system.bc.state != State.IDLE:
                    timeout += 0.001
                    if timeout > 1:
                        log.error(
                            f'bc timeout while handling {self.bus_gauge.name}')
                        err_rt2rt_timeout += 1
                        self.system.bc.state = State.IDLE
                    time.sleep(0.01)
                    pass

        log.info('stopping bc loop')

    def to_dict(self):
        nodes = [{'id': 'bus', 'data': {'label': 'data-bus'}}]
        edges = []

        for sensor, gauge, word_count in self.map:
            nodes.append({'id': sensor.name, 'data': {
                         'label': sensor.name, 'sources': sensor.feed.sources}, 'type': 'gadget'})
            nodes.append({'id': gauge.name, 'data': {
                         'label': gauge.name, 'sources': sensor.feed.sources}, 'type': 'gadget'})

            sensor_rt_name = sensor.rt.name(with_state=False)
            gauge_rt_name = gauge.rt.name(with_state=False)
            edges.append({
                'id': len(edges), 'source': sensor.name,
                'target': gauge.name,  'animated': True,
                'label': f'send {word_count} words',
                'style': {'stroke': 'red', 'strokeWidth': '2px'}, })

            nodes.append({'id': sensor_rt_name, 'data': {
                         'label': sensor_rt_name, 'state': str(sensor.rt.state),
                         'address': sensor.rt.address,
                          'mode': str(sensor.rt.mode)},  'type': 'device'})

            edges.append({
                'id': len(edges), 'source': sensor.name, 'target': sensor_rt_name,
                'type': 'smoothstep',  'animated': True,
                'style': {'strokeWidth': '2px'}
            })
            edges.append({
                'id': len(edges), 'target': 'bus', 'source': sensor_rt_name,
                'type': 'smoothstep',  'animated': True,
                'style': {'strokeWidth': '2px'}
            })

            nodes.append({'id': gauge_rt_name, 'data': {
                         'label': gauge_rt_name, 'state': str(gauge.rt.state),
                         'address': gauge.rt.address,
                         'mode': str(gauge.rt.mode)},  'type': 'device'})

            edges.append({
                'id': len(edges), 'target': gauge.name, 'source': gauge_rt_name,
                'type': 'smoothstep',  'animated': True,
                'style': {'strokeWidth': '2px'}
            })
            edges.append({
                'id': len(edges), 'source': 'bus', 'target': gauge_rt_name,
                'type': 'smoothstep',  'animated': True,
                'style': {'strokeWidth': '2px'}
            })

        for i, a in enumerate(self.attacks):
            if a.rt:
                a_name = 'attack_'+str(i)
                nodes.append(
                    {'id': a_name, 'data': {
                        'label': a.name, 'target': a.target}, 'type': 'gadget'})
                a_rt_name = a.rt.name(with_state=False)
                nodes.append({'id': a_rt_name, 'data': {
                    'label': a_rt_name, 'state': str(a.rt.state),
                    'address': a.rt.address,
                    'mode': str(a.rt.mode)},  'type': 'device'})

                edges.append({
                    'id': len(edges), 'target': a_rt_name, 'source': a_name,
                    'type': 'smoothstep',  'animated': True,
                    'style': {'strokeWidth': '2px'}
                })
                edges.append({
                    'id': len(edges), 'source': a_rt_name, 'target': 'bus',
                    'type': 'smoothstep',  'animated': True,
                    'style': {'strokeWidth': '2px'}
                })

        bc_name = self.system.bc.name(with_state=False)
        nodes.append({'id': bc_name, 'data': {
            'label': bc_name, 'state': str(self.system.bc.state),
            'mode': str(self.system.bc.mode)},  'type': 'device'})

        edges.append({
            'id': len(edges), 'source': bc_name, 'target': 'bus',
            'type': 'smoothstep',  'animated': True,
        })
        return {'running': self.running, 'flow': [*nodes, *edges]}


def generate_frames(sim: Sim):
    vidcap = cv2.VideoCapture(sim.recording_file)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    while True:
        frame_idx = int(sim.clock_s() * fps)
        if sim.running == False:
            frame_idx = 0
        vidcap.set(1, frame_idx)
        ret, frame = vidcap.read()
        if ret:
            ret, buffer = cv2.imencode('.jpg', frame)
            yield buffer.tobytes()
        else:
            break
    vidcap.release()


def serve_data(folder, ids=None):
    if not os.path.isabs(folder):
        folder = os.path.join(config.DATA_PATH, folder)
    csv_file = os.path.join(folder, 'msf.csv')
    key_file = os.path.join(folder, 'keys.json')
    cap_file = os.path.join(folder, 'video.mp4')
    df = pd.read_csv(csv_file)
    with open(key_file, 'r') as rf:
        sensors = json.load(rf)

    feeds = {}
    for k in sensors:
        columns = ['_t', *sensors[k]]
        # select column
        selected = df[columns].values.tolist()
        start = datetime.strptime(selected[0][0], '%Y-%m-%d %H:%M:%S.%f')
        for s in selected:
            s[0] = (datetime.strptime(s[0], '%Y-%m-%d %H:%M:%S.%f') -
                    start) / timedelta(milliseconds=1)
        feed = Feed(
            sources=columns[1:],
            descriptions=columns[1:],
            data=[tuple(s) for s in selected],
        )
        feeds[k.lower()] = feed

    simulation = Sim('sim0', recording_file=cap_file)
    simulation.add_monitor(ids=ids)
    for k, v in feeds.items():
        simulation.add_feed(k, v)
    return simulation
