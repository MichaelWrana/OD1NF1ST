from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *
import random


class Collision_Attack_against_an_RT(Sabotage):
    name = "Collision Attack Against Target RT"
    descr = "Send fake data messages to jam communication with specific target RT"

    def __init__(self, target = -1, data=0xffff, nwords_inj = 1) -> None:
        super().__init__()
        self.data = data
        self.target = target
        self.nwords_inj = nwords_inj

        
        
    def jam_cmdwords(self, e: Event_RT_REC_CMD):
        cmd: Command = e.word
        if cmd.address == self.target:
          self.rt.found_target = True
          self.rt.wc_n = cmd.dword_count 
          rt: Device = e.source
          #rt.state = State.TRANSMIT
          e.log(' \x1b[1;31;40m' + 'Jamming launched (after cmd_word)' + '\x1b[0m')
          self.inject_words(e, self.nwords_inj)
    
    
    def jam_statuswords(self, e: Event_RT_REC_STS):
        sts: Status = e.word
        if sts.address == self.target:
          rt: Device = e.source
          e.log(' \x1b[1;31;40m' + 'Jamming launched (after status_word)' + '\x1b[0m')
          self.inject_words(e, self.nwords_inj)
          
              
    def jam_datawords(self, e: Event_RT_REC_DATA):
        dt: Data = e.word
        rt: Device = e.source
        if self.rt.found_target == True and int.from_bytes(dt.data, "little") != self.data: 
          e.log(' \x1b[1;31;40m' + 'Jamming launched (after data_word)' + '\x1b[0m')
          self.inject_words(e, self.nwords_inj)
          self.rt.wc_n -= 1
          if self.rt.wc_n == 0:
            self.rt.found_target = False
          
    
    def inject_words(self, e: Event, n: int):
        rt: Device = e.source
        #rt.state = State.IDLE # not firing any rec data event
        clock = self.rt.clock()
        self.rt.store_append(clock, 'attack_time')
        for x in range(n):
          rt.write(Data(self.data))
          #rt.state = State.IDLE 
          e.log(' \x1b[0;33;40m' + 'sent Fake Data 0x{:02X} '.format(self.data) + '\x1b[0m',) 
        self.rt.success = True
         
        
    def go(self, system: System, attacker_address = 99, starting_time = None):

        if self.target == -1:
          self.target = random.choice(range(1, len(system.devices)))
    
        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, 
        found_target=False, fake = True, success = False)
        if starting_time:
            self.rt.clock_start = starting_time
        
        #Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.jam_cmdwords)
       
        #Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.jam_cmdwords)
        
        #Trigger upon DATA_word arrival
        self.rt.on(Event_RT_REC_DATA, self.jam_datawords)
        
        #Trigger upon Status_word arrival
        self.rt.on(Event_RT_REC_STS, self.jam_statuswords)
