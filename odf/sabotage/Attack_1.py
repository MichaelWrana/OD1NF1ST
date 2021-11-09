from jsonpickle.tags import STATE
from odf.sabotage.interface import *
from odf.events import *
from odf.components import *


class Collision_Attack_against_the_Bus(Sabotage):
    name = "Collision Attack Against The Bus"
    descr = "Send fake data messages to collide with current communications on the bus"

    def __init__(self, target=-2, data=0xffff, nwords_inj = 1) -> None:
        super().__init__()
        self.target = target
        self.nwords_inj = nwords_inj
        self.data = data
     
    def jam_cmdwords(self, e: Event_RT_REC_CMD):
        cmd: Command = e.word
        if cmd.tr == 0:
           e.log(' \x1b[1;31;40m' + 'Jamming launched (after rcmd_word)' + '\x1b[0m')
        else:
           e.log(' \x1b[1;31;40m' + 'Jamming launched (after tcmd_word)' + '\x1b[0m')
        self.inject_words(e, self.nwords_inj)
  
        
    def jam_datawords(self, e: Event_RT_REC_DATA):
        dt: Data = e.word
        if int.from_bytes(dt.data, "little") != self.data: 
          e.log(' \x1b[1;31;40m' + 'Jamming launched (after data_word)' + '\x1b[0m')
          self.inject_words(e,self.nwords_inj)
    
    
    def jam_statuswords(self, e: Event_RT_REC_STS):
        e.log(' \x1b[1;31;40m' + 'Jamming launched (after status_word)' + '\x1b[0m')
        self.inject_words(e,self.nwords_inj)
    
        
    def inject_words(self, e: Event, n: int):
        rt: Device = e.source
        if len(self.rt.store_get('attack_time')) == 0:
            clock = self.rt.clock()
            self.rt.store_append(clock, 'attack_time')
            self.rt.success = True
        for x in range(n):
            rt.write(Data(self.data))
            e.log(' \x1b[0;33;40m' + 'sent Fake Data 0x{:02X} '.format(self.data) + '\x1b[0m',) 
        
    def go(self, system: System, attacker_address = 99, starting_time=None):
    
        #Create attacker terminal
        self.rt = system.add_device(mode=Mode.RT, state=State.RECEIVE, address=attacker_address, 
        found_target=False, fake = True , success = False)
        if starting_time:
            self.rt.clock_start = starting_time

        
        #Trigger upon CMD_receive_word arrival
        self.rt.on(Event_RT_REC_CMD, self.jam_cmdwords)
        
        #Trigger upon CMD_transmit_word arrival
        self.rt.on(Event_RT_TRS_CMD, self.jam_cmdwords)
        
        #Trigger upon DATA_word arrival
        self.rt.on(Event_RT_REC_DATA, self.jam_datawords)
        
        #Trigger upon STATUS word arrival
        self.rt.on(Event_RT_REC_STS, self.jam_statuswords)
