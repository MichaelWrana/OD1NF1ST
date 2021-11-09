# The ability for a terminal to operate and behave like a BC or an RT.
# The ability for a terminal to send words (commands/data/status) at the same time as another terminal.
# The ability for a terminal to play the role of a BC and an RT at the same time.
# The ability to simulate the collision of messages.
# The ability for a terminal to modify each individual bit in a given word (commands/data/status).



my_bus = Bus(cables=3)

rt0 = RT(name=0)
rt1 = RT(name=1)
bc = BC(name=1)

bc.connect(bus=my_bus, port=0)
rt0.connect(bus=my_bus, port=1)
rt1.connect(bus=my_bus, port=2)

for i in range(10):
    rt_i = RT(name=i)
    rt_i.connect(bus=my_bus, port=i+3)


# showing gps information (rt0) on pilot's monitor (rt1)
bc.rt2rt(rt0, rt1)
# behind the sence:
# bc.send(rt1, recv)
# bc.send(rt2, transmit)


RT_WAITE_FOR_RT_MSG = 'whatever'
RT_WAITE_FOR_RT_DATA = 'w2'

class RT():

    def read():
        # read from sqlite database
        pass

    def listen(self):
        
        rt_status = None

        while True:

            status, target = read()
            if target == self.id and status == 'rec':
                rt_status = RT_WAITE_FOR_RT_MSG 


            if target == self.id and status == 'transmit' and rt_status == RT_WAITE_FOR_RT_MSG:
                write(bus, status_confirmed)
                write(bus, data)
                write(bus, data)
                write(bus, data)
                rt_status = None


            if target == self.id and status == 'data' and rt_status :
                data = read(bus)
                print(data)
                write(bus, status_confirmed)




class MalRTResponeRT2RT(RT):
    

    def _handle_data_transmit():
            write(bus, data)
            write(bus, data)



class Bus():
    
    

    def __init__(self) -> None:
        super().__init__()

    
    def on_write():
        pass


    def write(data):
        for d in devices():
            d.notify(d)
            

def TransportationLayer():

    @classmethod
    def write_transmite_command_word(cls, rt, data, bus)
    

    @classmethod
    def read
