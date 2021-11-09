import logging as log
from odf.config import config
from odf.components import Word, Device, Command, Status, Data, State, Mode
from odf.utils import delay
import time
import datetime
'''
Generic event parent class for all the possible things that can happen on a device
source: device that the event is associated with
word: the data word being passed through the bus
'''


class Event(object):

    def __init__(self, source: Device, word: Word) -> None:
        super().__init__()
        self.source: Device = source
        self.word: Word = word

    def default_handler(self):
        pass

    def write(self, words):
        self.source.write(words)

    def __call__(self):
        return self.default_handler()

    def log(self, msg, *args):
        prefix = '{: <25} {: <20}'.format(
            self.__class__.__name__, self.source.name())
        log.info(prefix + msg.format(*args))


'''
When a device in RECEIVE state gets a data word throught the bus
'''


class Event_WORD_REC(Event):

    def default_handler(self):
        # do nothing on word recipt for now
        pass


'''
Fires when there is a problem with the parity bit in a word (should never happen in current system)
'''


class Event_ERR_PARITY(Event):

    def default_handler(self):
        log.error('Word parity check failed on {} for {}'.format(
            self.source, self.word))


'''
This happens when an RT reads a command word to RECIEVE DATA
Occurs during 3 different protocols:
BC-RT, RT-RT, Broadcast
'''


class Event_RT_REC_CMD(Event):
    def default_handler(self):
        self.source.number_of_current_cmd += 1
        if self.source.number_of_current_cmd > 1:
            self.source.rt_cmd_cancelled = True
        if self.source.address == self.word.address or self.word.address == 31:  # if broadcast message address = 11111b
            self.source.set_state(State.RECEIVE)
            self.source.dword_expected = self.word.dword_count
            self.source.dword_count = 0
        if self.word.address == 31:
            self.source.in_brdcst = True


'''
This happens when an RT reads a command word to TRANSMIT DATA
Occurs during 2 different protocols:
RT-BC, RT-RT
'''


class Event_RT_TRS_CMD(Event):

    @delay
    def reponse_data(self):
        # If another command arrived, then the previous one is cancelled
        if not self.source.rt_cmd_cancelled:
            self.source.set_state(State.TRANSMIT)
            status = Status(address=self.source.address)
            if not hasattr(self, 'words'):
                self.words = [Data(0xa0a0)] * self.word.dword_count
            self.write([status, *self.words])
            self.source.number_of_current_cmd = 0
            self.source.rt_cmd_cancelled = False
            self.source.set_state(State.IDLE)
        else:
            pass

    def default_handler(self):
        if self.source.address == self.word.address:
            self.source.number_of_current_cmd += 1
            if self.source.number_of_current_cmd > 1:
                self.source.rt_cmd_cancelled = True
            self.source.set_state(State.WAIT)
            if config.SYS_LOG_EVENT:
                print('                                             \033[1;44;40mRT{} idling for {} seconds\033[0m'.format(
                    self.source.address, config.DEFAULT_RT_DELAY))
            # time.sleep(2)
            self.reponse_data(delay=config.DEFAULT_RT_DELAY)


'''
This happens after an RT has recieved data and is ready for the next command
Occurs during 
'''


class Event_BC_REC_CMD(Event):
    def default_handler(self):
        # reset state to idle
        self.source.set_state(State.IDLE)


'''
This happens when a BC is transmitting data over the network
'''


class Event_BC_TRS_CMD(Event):

    def default_handler(self):
        self.source.set_state(State.RECEIVE)


'''
This happens when an RT recieves a mode code command for TX shutdown
Occurs BC2RT and BC2RTs (Broadcast)
'''


class Event_RT_MC_CMD(Event):
    def default_handler(self):
        self.source.number_of_current_cmd += 1
        if self.source.number_of_current_cmd > 1:
            self.source.rt_cmd_cancelled = True
            self.source.number_of_current_cmd = 1
        if self.word.dword_count == 0:
            # Mode code command for
            pass
        elif self.word.dword_count == 1:
            # Mode code command for
            pass
        elif self.word.dword_count == 3:
            # Mode code command for
            pass
        elif self.word.dword_count == 4:
            # Mode code command for TX shutdown
            if self.source.fake == False:
                self.source.ccmd = 1
                self.source.set_state(State.OFF)
                if config.SYS_LOG_EVENT:
                    print('                                             \033[1;33;40mRT{}\'s tranceiver shutdown \033[0m'.format(
                        self.source.address))
                self.source.number_of_current_cmd = 0
        elif self.word.dword_count == 5:
            # Mode code command for
            pass
        # ...
        elif self.word.dword_count == 17:
            if self.source.fake == False:
                self.source.ccmd = 1
                self.source.set_state(State.RECEIVE)
                if config.SYS_LOG_EVENT:
                    print('                                             \033[1;33;40mRT{} synchronization initiated ... \033[0m'.format(
                        self.source.address))
                self.source.number_of_current_cmd = 0
        elif self.word.dword_count == 30:
            if self.source.fake == False:
                self.source.set_state(State.IDLE)
                self.source.memory.clear()
                if config.SYS_LOG_EVENT:
                    print('                                             \033[1;33;40mRT{} cache cleared: received data destroyed successfully! \033[0m'.format(
                        self.source.address))
        elif self.word.dword_count == 31:
            if self.source.fake == False:
                self.source.set_state(State.IDLE)
                if config.SYS_LOG_EVENT:
                    print('                                             \033[1;33;40mRT{} cancelled previous command ... \033[0m'.format(
                        self.source.address))


'''
This happens when an RT recieves data from the bus
Occurs during 3 protocols:
BC-RT, RT-RT, Broadcast
'''


class Event_RT_REC_DATA(Event):

    @delay
    def reponse_data(self):
        if not self.source.rt_cmd_cancelled:
            self.source.set_state(State.TRANSMIT)
            status = Status(address=self.source.address)
            self.write(status)
            self.source.number_of_current_cmd = 0
            self.source.rt_cmd_cancelled = False
            self.source.in_brdcst = False
            self.source.set_state(State.IDLE)

    def default_handler(self):

        if not self.source.fake:
            # Check if this data is related to the current command
            if self.source.ccmd == 0:
                self.source.dword_count += 1
                # do something with the data
                # print(self.word)
                if self.source.dword_count == self.source.dword_expected and not self.source.in_brdcst:
                    self.source.set_state(State.WAIT)
                    if config.SYS_LOG_EVENT:
                        print('                                             \033[1;44;40mRT{} idling for {} seconds\033[0m'.format(
                              self.source.address, config.DEFAULT_RT_DELAY))
                    self.reponse_data(delay=config.DEFAULT_RT_DELAY)
                elif self.source.dword_count == self.source.dword_expected and self.source.in_brdcst:
                    self.source.number_of_current_cmd = 0
                    self.source.rt_cmd_cancelled = False
                    self.source.in_brdcst = False
                    self.source.set_state(State.IDLE)
                else:
                    pass
            else:
                if config.SYS_LOG_EVENT:
                    delta_time = datetime.timedelta(milliseconds=int.from_bytes(self.word.data, "little"))
                    self.source.clock_start = self.source.clock_start - delta_time
                    print('                                             \033[1;33;40mRT{}\'s local clock set to {}\033[0m'.format(
                        self.source.address, self.source.clock()))
                self.source.set_state(State.IDLE)
            self.source.ccmd = 0


'''
This happens when an RT recieves a status word from the bus
Occurs during 3 protocols:
BC-RT, RT-RT, Broadcast
'''


class Event_RT_REC_STS(Event):
    def default_handler(self):
        pass


'''                
class Event_RT_TRS_DATA(Event):
    def default_handler(self):
        pass          
'''
'''
This happens when a BC recieves data from the bus
Occurs during 1 protocol:
RT-BC
'''


class Event_BC_REC_DATA(Event):
    def default_handler(self):
        self.source.dword_count += 1
        if self.source.dword_count == self.source.dword_expected:
            self.source.set_state(State.IDLE)


'''
This happens when a BC receives a status message after transmitting data to an RT
Occurs during 1 (2?) protocol(s)
BC-RT, Broadcast?
'''


class Event_BC_REC_STS(Event):
    def default_handler(self):
        if self.source.state == State.RECEIVE:
            # rt2bc mode. do nothing
            pass
        elif self.source.state == State.TRANSMIT_CMD:
            # rt2rt mode. bc just transmitted two commnad words:
            # confirmed sender will transfer.
            # now wait for the reciever's confirmation
            self.source.set_state(State.WAIT)
        elif self.source.state == State.WAIT or self.source.state == State.TRANSMIT:
            # rt2rt - confrimed from reciever
            self.source.set_state(State.IDLE)


def route_Event(device: Device, word: Word):
    # PROBLEM: RECIEVE AND TRANSMIT COMMANDS FOR RT2RT ARE IDENTICAL

    # SHOULD REFACTOR FOR CLARITY - ORGANIZE BY COMMAND WORD WOULD MAKE MORE SENSE

    if isinstance(word, Command):
        if (word.address == device.address or device.fake or word.address == 31) and not device.state == State.OFF:
            if word.sub_address == 2:
                if word.tr == 0:
                    # receive
                    if device.mode == Mode.RT:
                        yield Event_RT_REC_CMD(device, word)
                else:
                    # transmit
                    if device.mode == Mode.RT:
                        yield Event_RT_TRS_CMD(device, word)
            elif word.sub_address == 1 or word.sub_address == 0:
                yield Event_RT_MC_CMD(device, word)

    elif isinstance(word, Data):
        if device.mode == Mode.RT and not device.state == State.OFF:
            if device.state == State.RECEIVE:
                yield Event_RT_REC_DATA(device, word)
            elif device.state == State.TRANSMIT:
                pass
                # yield Event_RT_TRS_DATA (device,word)

        elif device.mode == Mode.BC:
            if device.state == State.RECEIVE:
                yield Event_BC_REC_DATA(device, word)

    elif isinstance(word, Status):
        if device.mode == Mode.BC:
            # if device.state==State.TRANSMIT:
            yield Event_BC_REC_STS(device, word)
        elif device.mode == Mode.RT and not device.state == State.OFF:
            if word.address == device.address:
                if device.number_of_current_cmd == 1:
                    device.rt_cmd_cancelled = True
            elif word.address != device.address and device.fake:
                yield Event_RT_REC_STS(device, word)
