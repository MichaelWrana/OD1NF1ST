from odf.mfs import sim
from odf import *
from odf.ids.gcnn import GCNN
import json

if __name__ == '__main__':

    # sensor reading with 2 numbers [the first one is time offset in milisecond]
    # num_values = 6
    # feed = Feed(
    #     sources=[f'test_d{i}' for i in range(num_values)],
    #     descriptions=[f'test_d{i}' for i in range(num_values)],
    #     # 5 minutes data, 200ms per sample
    #     data=[tuple([i*200] + [i]*num_values) for i in range(5*60*5)]
    # )

    # test
    # simulation = Sim('sim0')
    # simulation.add_monitor()
    # simulation.add_feed('test0', feed)
    # simulation.add_feed('test1', feed)
    # simulation.add_feed('test2', feed)
    # simulation.add_feed('test3', feed)
    # simulation.add_feed('test4', feed)
    # simulation.add_feed('test5', feed)
    # simulation.add_feed('test6', feed)

    #attack = Command_Invalidation_Attack(target=4)
    # attack.go(simulation.system)

    # simulation.monitors[0].log_data()

    # simulation = serve_data('UiOff')
    # simulation.start()
    # time.sleep(60*5)
    # simulation.dump_monitor(saved=True)
    # simulation.shutdown()
    # for _ in range(500):
    #     simulation = serve_data('UiOff')
    #     simulation.start()
    #     simulation.sabotage(random_delay=60)
    #     time.sleep(60)
    #     simulation.dump_monitor(saved=True)
    #     simulation.shutdown()

    simulation = serve_data('scene_1', GCNN())
    simulation.start()
    time.sleep(60*5)
    simulation.shutdown()

    #data = simulation.monitors[0].get_data()
    #attack_timestamps = attack.rt.store_get('attack_time')
    # dump = {
    #    'data': data,
    #    'attack_time': attack_timestamps
    #    }
    #dump_str = jsonpickle.encode(dump)
    # with open('Attack_10.json', 'w') as outfile:
    #    json.dump(dump_str, outfile)

    # s0 = Sensor('s0', 'test', system)
    # g0 = Gauge('g0', system)
    # system.bc.act_rt2rt(s0.rt.address, g0.rt.address, 10)
    # time.sleep(6)
    # g0.log_data()
    # m0.log_data()
    # system.shutdown()
