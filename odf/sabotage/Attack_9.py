from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *
import random

class Data_Corruption_Attack(Sabotage):
    name = "Data Corruption Attack"
    descr = "Upon receiving a transmit command, send a fake status word instead of the original RT followed by fake data"
    
    def __init__(self, target = -1, data=0x7171) -> None:
        super().__init__()
        self.data = data
        self.target = target
      
    def find_RT_tcmd(self, e: Event_RT_TRS_CMD):
        cmd: Command = e.word
        if cmd.address==self.target and cmd.sub_address==2 and self.rt.target_found==False:
           self.rt.wc= e.word.dword_count
           e.log(' \x1b[1;31;40mAttacker>> Target detected (RT{})\x1b[0m'.format(self.target))
           self.rt.target_found=True
           self.inject_fake_data(e)  
        
    
    def inject_fake_data(self, e: Event):
        rt: Device = e.source
        e.log(' \x1b[1;31;40mAttacker>> Injecting a fake status word followed by fake data ...\x1b[0m')
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        sts = Status(address=self.target, parity_bit='0')
        self.rt.write(sts)
        for i in range(self.rt.wc):
           data = Data(self.data)
           self.rt.write(data)
        self.rt.target_found=False
        self.rt.success = True 
        
  
            
    def go(self, system: System, attacker_address = 99, starting_time = None):
        
        if self.target == -1:
          self.target = random.choice(range(1, len(system.devices))) 

        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, fake=True,
        target_found=False, flag=0, wc=0, success = False)
        if starting_time:
            self.rt.clock_start = starting_time
        
        #Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.find_RT_tcmd)
      
        
