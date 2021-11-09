import logging as log
from multiprocessing import Event
import socket
from odf.config import config
import time
import uuid
from enum import Enum
from typing import ClassVar, Generator, List
from collections import defaultdict
from odf.utils import delay
import struct
from datetime import datetime, timedelta

import jsonpickle

# class that represents a word which can be sent over the bus


class Word():
    fake = False
    # check the parity bit at the end
    # currently always true

    def check_parity(self):
        return True

    def __str__(self) -> str:
        prefix = '{:<7} '.format(
            self.__class__.__name__,
        )
        return prefix

    def to_bytes(self):
        # if isinstance(self, Data):
        #     return self.data
        return jsonpickle.encode(self).encode('utf8')

    @classmethod
    def from_bytes(cls, bytes):
        # if len(bytes) == 2:
        #     return Data(bytes)
        return jsonpickle.decode(bytes.decode('utf8'))

# The contents of a status word which can be sent over the bus


class Status(Word):
    def __init__(
        self,
        # Addres of the RT issueing the status word
        address='0',
        # set to 1 if there was an error in processing one or more of the data words sent
        message_error_bit='0',
        # optional and should always be set to 0
        # used to distinguish between a command word and status word
        instrumentation_bit='0',
        # set if there is need for a data tramsfer operation that is non-periodic
        service_request_bit='0',
        # 'reserved for future use' - always set to 0
        reserved_bits='000',
        # set if the preceeding command word was a broadcast message
        brdcst_received_bit='0',
        # set if the subsystem cannot move data where its needed
        # when set in response to transmit command, RT only sends status word
        busy_bit='0',
        # set if an RT subsystem has problems and cannot correctly process the data being sent
        subsystem_flag_bit='0',
        # set for the acceptance of dynamic bus control (RT taking over as BC)
        dynamic_bus_control_accpt_bit='0',
        # set if there is an RT fautl condition
        terminal_flag_bit='1',
        # used for parity
        parity_bit='1',
    ) -> None:
        super().__init__()
        self.address = address
        self.message_error_bit = message_error_bit
        self.instrumentation_bit = instrumentation_bit
        self.service_request_bit = service_request_bit
        self.reserved_bits = reserved_bits
        self.brdcst_received_bit = brdcst_received_bit
        self.busy_bit = busy_bit
        self.subsystem_flag_bit = subsystem_flag_bit
        self.dynamic_bus_control_accpt_bit = dynamic_bus_control_accpt_bit
        self.terminal_flag_bit = terminal_flag_bit
        self.parity_bit = parity_bit

    def __str__(self) -> str:
        attrs = sorted(vars(self).items(), key=lambda x: x[0])
        prefix = super().__str__()
        return prefix + '('+', '.join([k[:2]+'-'+str(v) for k, v in attrs])+')'

# the content of a data word


class Data(Word):
    def __init__(self, data=0xffff) -> None:
        super().__init__()
        # the only thing here is sixteen bits of data followed by a parity bit
        # if isinstance(data, float):
        #     data = struct.pack('f', data)
        # elif isinstance(data, int):
        #     data = struct.pack('i', data)
        if not isinstance(data, bytes):
            data = data.to_bytes(2, byteorder='big')
        self.data = data

    def __str__(self) -> str:
        prefix = super().__str__()
        return f'{prefix}(0x{self.data.hex()})'

    def get_data(self):
        return self.data

    @classmethod
    def pack(cls, data: List, is_float=False):
        if len(data) < 1:
            return []
        if is_float:
            d_bytes = struct.pack('%sf' % len(data), *data)
        else:
            d_bytes = struct.pack('%si' % len(data), *data)
        if len(d_bytes) % 2 != 0:
            raise ValueError(f'len {len(d_bytes)} is not even')
        return [Data(data=d_bytes[w*2:(w+1)*2]) for w in range(len(d_bytes)//2)]

    @classmethod
    def unpack(cls, data: List, is_float=False):
        data: List[Data]
        d_bytes = b''.join(
            [w.data if isinstance(w, Data) else w for w in data])
        if len(d_bytes) % 4 != 0:
            raise ValueError(f'len {len(d_bytes)} is not a multiplier of 4')
        # each word is 16 bits (two bytes) and each number is 32 bits
        # so 2 words per number
        if is_float:
            fmt = "<%df" % (len(d_bytes) // 4)
        else:
            fmt = "<%di" % (len(d_bytes) // 4)
        return struct.unpack(fmt, d_bytes)


class Command(Word):
    def __init__(
        self,
        # the RT address which is five bits long
        # address 11111 (31) is reserved for broadcast protocol
        address=0,
        # 0: recieve data
        # 1: transmit data
        tr=0,
        # 5 bits used to indicate an RT subaddress
        # 00000 and 11111 (31) are reserved
        sub_address=2,
        # the quantity of data that will follow after the command
        # 00000 means 32 ??? and 11111 means 31
        dword_count=0,
        # parity bit over last 16 bits
        parity=0,
    ) -> None:
        super().__init__()
        self.address = address
        self.tr = tr
        self.sub_address = sub_address
        self.dword_count = dword_count
        self.parity = parity

    def __str__(self) -> str:
        attrs = sorted(vars(self).items(), key=lambda x: x[0])
        prefix = super().__str__()
        return prefix + '('+', '.join([k[:2]+'-'+str(v) for k, v in attrs])+')'

# used to indicate which type of terminal this device should be


class Mode(Enum):
    RT = 1
    BC = 2
    BM = 3

# use to indicate the type of communication that is happening for each device


class State(Enum):
    IDLE = 0
    TRANSMIT = 1
    RECEIVE = 2
    OFF = 3
    WAIT = 4
    TRANSMIT_CMD = 5


class BusABC():
    def write(self, device, words: List[Word]):
        pass

    def recv(self, device) -> Word:
        pass


'''
mode: type of this device: BC, RT or BM
state: way this device interprets the commands being sent over the bus
bus: ???
address: address of this device on the network between 0 and 31
queue: list of all messages this device recieved over the network it must process
event_handlers: ???
uuid: unique ID for this device
system: system this device is connected to
'''


class Device():

    def __init__(
            self, bus: BusABC, mode=Mode.RT, address=-1, state=State.IDLE,
            id=None, system='', dword_count=0, **other_attributes) -> None:
        self.fake: bool = False
        # allows to determine whether the current command was cancelled during idel mode
        self.rt_cmd_cancelled = False
        # allows to count the nuber of commands pending on RT at a given time
        self.number_of_current_cmd = 0
        # current local clock of the RT
        self.lclock: int = 0
        # current CMD 0 for T/R and 1 for MC
        self.ccmd: int = 0
        self.in_brdcst = False

        self.mode: Mode = mode
        self.state: State = state
        self.bus: BusABC = bus
        self.address = address
        self.port = -1
        self.event_handlers = {}
        self.id = uuid.uuid4().hex if not id else id
        self.system = system
        self.dword_count = dword_count
        for k, v in other_attributes.items():
            setattr(self, k, v)

        # memory/storage for the device
        # if we directly use these objects from the other classes,
        # it means the whole object needed to be copied over different processes
        # so we have to keep the memory/storage within this class (maybe large)
        # and provide interfaces to slice them
        # -- memory: linear layout of words (two-bytes)
        self.memory: List[bytes] = []
        # -- storage: key-(multi-val) object storage
        self.storage = defaultdict(list)
        self.clock_start = datetime.now()

    def on(self, event_name, handler):
        if not isinstance(event_name, str):
            event_name = event_name.__name__
        self.event_handlers[event_name] = handler

    @ delay
    def write(self, word: Word):
        if not isinstance(word, list):
            word = [word]
        if not hasattr(self, 'sock_trans'):
            self.sock_trans = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock_trans.bind(('', 0))
        for w in word:
            w.fake = self.fake
            for d in self.bus.values():
                if d.port > 0:
                    self.sock_trans.sendto(w.to_bytes(), ('127.0.0.1', d.port))

    def clock(self):
        if self.state == State.OFF and self.mode != Mode.BM:
            return 0
        return (datetime.now() - self.clock_start) // timedelta(milliseconds=1)

    def set_state(self, new_state):
        if config.SYS_LOG_EVENT:
            log.info('\033[32m{}{}{} changed from {} to {}\033[39m'.format(
                str(self.mode)[5], str(self.mode)[6], self.address, self.state, new_state))

        # added clocking when turning on:
        if self.state == State.OFF and new_state != State.OFF:
            self.clock_start = datetime.now()

        self.state = new_state
        # use to be:
        # log.info('{} change from {} to {}'.format(
        #    self.name(), self.state, new_state))
        # self.state = new_state
        # Now easier to backtrack the RTs

    def mem_put(self, words: List[bytearray], addr=None):
        if not isinstance(words, List):
            words = [words]
        if addr is None:
            self.memory.extend(words)
        else:
            for i in range(len(words)):
                self.memory[i+addr] = words[i]
        return len(self.memory)

    def mem_get(self, start=0, end=None):
        if end:
            return self.memory[start:]
        else:
            return self.memory[start:end]

    def mem_unpack(self, is_float=False):
        return Data.unpack(self.memory, is_float=is_float)

    def mem_reset(self):
        self.memory = []

    def store_get(self, key=None):
        return self.storage[key]

    def store_append(self, data, key=None):
        self.storage[key].append(data)

    def store_set(self, data, key=None):
        self.storage[key] = data

    '''
    target: ID of target RT to send data to
    words: set of data to send to target RT
    '''

    def act_bc2rt(self, target, words: List[Word], ignore_limit=False):
        nwords = len(words)
        if not ignore_limit:
            if nwords > 31:
                raise Exception("Max number is 31 (2^5=32)")
        # first, send 'receive' command word with the target RT ID & amount of data
        cmd = Command(address=target, dword_count=nwords, tr=0)
        # set the state of this device to be transmitting data
        # self.state = State.TRANSMIT  # this is BC state
        self.set_state(State.TRANSMIT_CMD)
        # write the command word first, to notify the target device to receive data
        self.write(cmd)
        # send the data
        self.set_state(State.TRANSMIT)
        for w in words:
            self.write(w)
        if target == 31:
            self.set_state(State.IDLE)

    '''
    target: ID of target RT to send data to
    nwords: number of words to recieve from the RT
    '''

    def act_rt2bc(self, target, nwords):
        # first send "transmit" command word with target RT ID & amount of data
        cmd = Command(address=target, dword_count=nwords, tr=1)
        # set the state of this device to be recieving data
        self.dword_count = 0
        self.dword_expected = nwords
        self.start_rec = False
        # write the command word
        self.set_state(State.TRANSMIT_CMD)
        self.write(cmd)
        self.set_state(State.RECEIVE)

    '''
    source: ID of source RT to transmit data
    target: ID of target RT to receive data
    nwords: number of words to recieve from the RT
    '''

    def act_rt2rt(self, source, target, nwords):
        self.set_state(State.TRANSMIT_CMD)
        cmd0 = Command(address=target, dword_count=nwords, tr=0)
        cmd1 = Command(address=source, dword_count=nwords, tr=1)
        self.write([cmd0, cmd1])

    def name(self, with_state=True) -> str:
        if with_state:
            return '{}:{}{}-{}-{}'.format(self.system, self.mode.name, self.address, self.id[-4:], self.state.name)
        else:
            return '{}:{}{}-{}'.format(self.system, self.mode.name, self.address, self.id[-4:])
