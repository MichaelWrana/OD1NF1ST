from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *
import random


class Data_Thrashing_Attack_against_an_RT(Sabotage):
    name = "Data Thrashing Against Target RT"
    descr = "Thrashing data received by RT by sending fake command word just after complete data transfer"

    def __init__(self, target=-1, data=None) -> None:
        super().__init__()
        self.data = data
        self.target = target

    def jam_cmdwords(self, e: Event_RT_REC_CMD):
        cmd: Command = e.word
        if cmd.address == self.target and cmd.tr == 0 and cmd.tr != 2:
            self.rt.found_target = True
            self.rt.wc_n = cmd.dword_count
            e.log(' \x1b[1;31;40m' +
                  'Trashing trigged (after cmd_word)' + '\x1b[0m')

    def jam_datawords(self, e: Event_RT_REC_DATA):
        rt: Device = e.source
        dt: Data = e.word
        if self.rt.found_target == True:
            self.rt.wc_n -= 1
            if self.rt.wc_n == 0:
                self.rt.found_target = False
                e.log(' \x1b[6;30;42m' + 'Fake command injected!' + '\x1b[0m')
                self.inject_words(e)

    def inject_words(self, e: Event):
        rt: Device = e.source
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        cmd = Command(self.target, sub_address=1, dword_count=30)
        rt.write(cmd)
        self.rt.success = True

    def go(self, system: System, attacker_address=99, starting_time=None):

        if self.target == -1:
            self.target = random.choice(range(1, len(system.devices)))

        # Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address,
                                    found_target=False, fake=True, success=False)
        if starting_time:
            self.rt.clock_start = starting_time

        # Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.jam_cmdwords)

        # Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.jam_cmdwords)

        # Trigger upon DATA_word arrival
        self.rt.on(Event_RT_REC_DATA, self.jam_datawords)
