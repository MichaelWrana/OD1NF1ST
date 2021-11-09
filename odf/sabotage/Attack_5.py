from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *
import random

class Shutdown_Attack_on_RT(Sabotage):
    name = "Shutdown Attack on Target RT"
    descr = "Send fake shutdown command to specific target RT"
   
    def __init__(self, target = -1, data=None) -> None:
        super().__init__()
        self.target = target
      
        
        
    def find_RT_rcmd(self, e: Event_RT_REC_CMD):
        cmd: Command = e.word
        if cmd.address==self.target and cmd.sub_address==2 and self.rt.target_found==False:
           e.log(' \x1b[1;31;40m Attacker>> Target detected (RT{})\x1b[0m'.format(self.target))
           self.rt.target_found=True
           self.kill_RT(e)
    
    def find_RT_tcmd(self, e: Event_RT_TRS_CMD):
        cmd: Command = e.word
        if cmd.address==self.target and cmd.sub_address==2 and self.rt.target_found==False:
           e.log(' \x1b[1;31;40m Attacker>> Target detected (RT{})\x1b[0m'.format(self.target))
           self.rt.target_found=True
           self.kill_RT(e)
           
    def find_RT_sw(self, e: Event_RT_REC_STS):
        sts: Status = e.word
        if sts.address==self.target and self.rt.target_found==False:
           e.log(' \x1b[1;31;40m Attacker>> Target detected (RT{})\x1b[0m'.format(self.target))
           self.rt.target_found=True
           self.kill_RT(e)
          
    
    def kill_RT(self, e: Event):
        rt: Device = e.source
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        e.log(' \x1b[1;31;40m Attacker>> Killing RT{}...\x1b[0m'.format(self.target))
        cmd = Command(self.target, sub_address=1, dword_count=4)
        self.rt.write(cmd)
        self.rt.success = True
        self.rt.set_state(State.OFF)
        self.rt.state = State.OFF
        
        
  
            
    def go(self, system: System, attacker_address = 99, starting_time = None):
    
        if self.target == -1:
          self.target = random.choice(range(1, len(system.devices)))
          
        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, 
        fake=True, target_found = False, success = False)
        if starting_time:
            self.rt.clock_start = starting_time
        
        #Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.find_RT_rcmd)
       
        #Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.find_RT_tcmd)
        
        #Trigger upon STATUS_word arrival
        self.rt.on(Event_RT_REC_STS, self.find_RT_sw)
        
