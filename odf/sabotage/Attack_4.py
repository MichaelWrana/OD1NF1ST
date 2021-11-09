from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *


class MITM_attack_on_RTs(Sabotage):
    name = "Man in The Middle (MITM) Attack"
    descr = "Perform MITM on two RTs after monitoring previous communications"

    def __init__(self, target=-2, delay=3, time_next_attack=10) -> None:
        super().__init__()
        self.delay = delay
        self.target = -2
        self.time_next_attack = time_next_attack

    def find_RTs(self, e: Event_RT_REC_CMD):
        if (not (self.rt.target_dst_found and self.rt.target_src_found)) and not self.rt.done:
            cmd: Command = e.word
            if cmd.tr == 0 and not self.rt.target_dst_found and cmd.address != 31:
                self.rt.target_dst = cmd.address
                self.rt.target_dst_found = True
                self.rt.wc_n = cmd.dword_count
                if self.rt.nwords_inj == 0:
                    self.rt.nwords_inj = cmd.dword_count
                e.log(' \x1b[1;31;40m Attacker>> Target dst identified (RT{})\x1b[0m'.format(
                    self.rt.target_dst))
            elif cmd.tr == 1 and not self.rt.target_src_found and cmd.address != 31:
                self.rt.target_src = cmd.address
                self.rt.target_src_found = True
                e.log(' \x1b[1;31;40m Attacker>> Target src identified (RT{})\x1b[0m'.format(
                    self.rt.target_src))

    def getReady_for_MITM(self, e: Event):
        rt: Device = e.source
        sts: Status = e.word
        if self.rt.target_src == sts.address and not (self.rt.done):
            if self.rt.target_dst_found and self.rt.target_src_found:
                time.sleep(self.delay)
                self.start_MITM(e)
        elif self.rt.target_src == sts.address and self.rt.done:
            e.log(
                ' \x1b[6;30;42m' + 'Attacker>> Man in the Middle Successfully Completed!' + '\x1b[0m')
            self.rt.success = True
            self.rt.target_src_found = False
            self.rt.target_dst_found = False
            self.rt.done = False

    def start_MITM(self, e: Event):
        rt: Device = e.source
        e.log(' \x1b[1;31;40m' +
              'Attacker>> Starting MITM attack...' + '\x1b[0m')
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        self.rt.set_state(State.OFF)

        cmd = Command(self.rt.target_src, dword_count=self.rt.nwords_inj, tr=0)
        self.rt.write(cmd)

        cmd = Command(self.rt.target_dst, dword_count=self.rt.nwords_inj, tr=1)
        self.rt.write(cmd)

        self.rt.done = True
        time.sleep(self.time_next_attack)
        self.rt.set_state(State.RECEIVE)

    def go(self, system: System, attacker_address=99, starting_time=None):

        # Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, fake=True, target_dst=-1,
                                    target_src=-1, target_dst_found=False, target_src_found=False, done=False, nwords_inj=0, success=False)
        if starting_time:
            self.rt.clock_start = starting_time

        # Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.find_RTs)

        # Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.find_RTs)

        # Trigger upon STATUS_word arrival
        self.rt.on(Event_RT_REC_STS, self.getReady_for_MITM)
