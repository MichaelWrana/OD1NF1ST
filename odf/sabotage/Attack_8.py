from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *
import random


class Desynchronization_Attack_on_RT(Sabotage):
    name = "Desynchronization Attack on Target RT"
    descr = "Send a desynchronization command to mess with the local clock of RT"

    def __init__(self, target=-1, data=0x000F) -> None:
        super().__init__()
        self.data = data
        self.target = target

    def find_RT_rcmd(self, e: Event_RT_REC_CMD):
        cmd: Command = e.word
        if cmd.address == self.target and cmd.sub_address == 2 and self.rt.target_found == False:
            if self.rt.flag == 0:
                self.rt.flag = 1
            self.rt.wc = e.word.dword_count
            e.log(' \x1b[1;31;40mAttacker>> Target detected (RT{})\x1b[0m'.format(
                self.target))
            self.rt.target_found = True

    def find_RT_tcmd(self, e: Event_RT_TRS_CMD):
        cmd: Command = e.word
        if cmd.address == self.target and cmd.sub_address == 2 and self.rt.target_found == False:
            if self.rt.flag == 0:
                self.rt.flag = 2
                self.rt.wc = e.word.dword_count
            e.log(' \x1b[1;31;40mAttacker>> Target detected (RT{})\x1b[0m'.format(
                self.target))
            self.rt.target_found = True

    def watch_data(self, e: Event_RT_TRS_CMD):
        self.rt.wc -= 1
        if self.rt.flag == 2 and self.rt.wc == 0:
            time.sleep(3)
            self.desynchronize_RT(e)

    def find_RT_sw(self, e: Event_RT_REC_STS):
        sts: Status = e.word
        if sts.address == self.target and self.rt.flag == 1 and self.rt.wc == 0:
            time.sleep(3)
            self.desynchronize_RT(e)
        elif sts.address == self.target and self.rt.flag == 2:
            pass

    def desynchronize_RT(self, e: Event):
        rt: Device = e.source
        e.log(' \x1b[1;31;40mAttacker>> Desynchronizing RT{} ...\x1b[0m'.format(
            self.target))
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        cmd = Command(self.target, sub_address=1, dword_count=17)
        self.rt.write(cmd)
        data = Data(self.data)
        self.rt.write(data)
        self.rt.target_found = False
        self.rt.success = True

    def go(self, system: System, attacker_address=99, starting_time=None):

        if self.target == -1:
            self.target = random.choice(range(1, len(system.devices)))

        # Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, fake=True,
                                    target_found=False, flag=0, wc=0, success=False)
        if starting_time:
            self.rt.clock_start = starting_time

        # Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.find_RT_rcmd)

        # Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.find_RT_tcmd)

        # Trigger upon DATA_word arrival
        self.rt.on(Event_RT_REC_DATA, self.watch_data)

        # Trigger upon STATUS_word arrival
        self.rt.on(Event_RT_REC_STS, self.find_RT_sw)
