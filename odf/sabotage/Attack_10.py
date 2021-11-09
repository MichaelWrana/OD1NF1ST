from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *
import random

class Command_Invalidation_Attack(Sabotage):
    name = "Command Invalidation Attack"
    descr = "Upon receiving a transmit command, send a another fake command word to invalidate the original"

    def __init__(self, target = -1) -> None:
       super().__init__()
       self.target = target
      
        
        
    def find_RT_tcmd(self, e: Event_RT_TRS_CMD):
        cmd: Command = e.word
        if cmd.address==self.target and cmd.sub_address==2 and self.rt.target_found==False:
           e.log(' \x1b[1;31;40m Attacker>> Target detected (RT{})\x1b[0m'.format(self.target))
           self.rt.target_found=True
           self.inject_command(e)
                     
    
    def inject_command(self, e: Event):
        rt: Device = e.source
        e.log(' \x1b[1;31;40m Attacker>> Injecting fake command on RT{}...\x1b[0m'.format(self.target))
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        cmd = Command(self.target, sub_address=1, dword_count=31)
        self.rt.write(cmd)
        self.rt.success = True
        
        
  
            
    def go(self, system: System, attacker_address = 99, starting_time = None):
    
        if self.target == -1:
          self.target = random.choice(range(1, len(system.devices))) 
          
        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, 
        fake=True, target_found=False, success = False)
        if starting_time:
            self.rt.clock_start = starting_time
        
        #Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.find_RT_tcmd)
        
     
        
