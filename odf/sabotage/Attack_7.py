from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *


class Fake_Status_trcmd(Sabotage):
    name = "Fake Status Reply to Transmit Command"
    descr = "Reply with a fake status word after receiving transmit command to abort the transmit process"
   
    def __init__(self, target = -1) -> None: #target default -1 means for any transmit command regardless of the target
        super().__init__()
        self.target = target

        
        
    def intercept_trcmd(self, e: Event_RT_TRS_CMD):
        cmd: Command = e.word
        if cmd.address != self.rt.address:
           if self.target != -1:
              if cmd.address == self.target and cmd.tr == 1 and not self.rt.found_target:
                 e.log(' \x1b[1;31;40mAttacker>> Target detected (RT{})\x1b[0m'.format(self.target))  
                 self.rt.found_target = True 
                 e.log(' \x1b[1;31;40m' + 'Sending fake status word (after tr_cmd_word)' + '\x1b[0m')
                 self.fake_sts(e)
           else:
              if cmd.tr == 1 and cmd.address != 31:
                 e.log(' \x1b[1;31;40m' + 'Sending fake status word (after tr_cmd_word)' + '\x1b[0m')
                 self.fake_sts(e)
        else:
           pass  
          
    def fake_sts(self, e: Event):
        rt: Device = e.source
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        sts = Status(address=e.word.address, parity_bit='0')
        rt.write(sts)
        e.log(' \x1b[6;30;42m' + 'Fake status injected!' + '\x1b[0m')
        self.rt.found_target = False
        self.rt.success = True
         
        
    def go(self, system: System, attacker_address = 99, starting_time = None):
    
        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.IDLE, address=attacker_address, 
        found_target=False, fake = True, success = False)
        if starting_time:
            self.rt.clock_start = starting_time
        
        #Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.intercept_trcmd)
        
