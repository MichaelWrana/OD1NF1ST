from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *


class Fake_Status_reccmd(Sabotage):
    name = "Fake Status Reply to Receive Command"
    descr = "Reply with a fake status word after receiving data to thrash data and fake response"
   
    def __init__(self, target = -1) -> None: #target default -1 means for any receive command regardless of the target
        super().__init__()
        self.target = target

        
        
    def intercept_reccmd(self, e: Event_RT_REC_CMD):
        cmd: Command = e.word
        if cmd.address != self.rt.address:
           if self.target != -1 and cmd.address == self.target and cmd.tr == 0:
              self.rt.found_target = True
              e.log(' \x1b[1;31;40mAttacker>> Target detected (RT{})\x1b[0m'.format(self.target))  
              self.rt.wc_n = cmd.dword_count 
              self.rt.dst=cmd.address
              e.log(' \x1b[1;31;40m' + 'Fake status trigged (after cmd_word)' + '\x1b[0m')
           else:
              if cmd.tr == 0 and cmd.address != 31:
                 e.log(' \x1b[1;31;40mAttacker>> Target detected (RT{})\x1b[0m'.format(cmd.address))  
                 self.rt.wc_n = cmd.dword_count 
                 self.rt.dst=cmd.address
                 self.rt.found_target = True
                 e.log(' \x1b[1;31;40m' + 'Fake status trigged (after cmd_word)' + '\x1b[0m')
        else:
           pass 
           
        
    def intercept_dw(self, e: Event_RT_REC_DATA):
        rt: Device = e.source
        dt: Data = e.word
        if self.rt.found_target and int.from_bytes(dt.data, "little") != 0xffff:
            self.rt.wc_n -= 1
            if self.rt.wc_n == 0:
                self.rt.found_target = False
                e.log(' \x1b[6;30;42m' + 'Fake status injected!' + '\x1b[0m')
                self.inject_words(e)          
          
    
    def inject_words(self, e: Event):
        rt: Device = e.source
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        sts = Status(address=self.rt.dst, parity_bit='0')
        rt.write(sts)
        self.rt.success = True
        self.rt.dst = -1

        
    def go(self, system: System, attacker_address = 99, starting_time = None):
    
        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, found_target=False, 
        wc_n=0, dst=-1, fake = True, success = True)
        if starting_time:
            self.rt.clock_start = starting_time
        
        #Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.intercept_reccmd)
       
        
        #Trigger upon DATA_word arrival
        self.rt.on(Event_RT_REC_DATA, self.intercept_dw)
