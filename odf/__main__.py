from odf import *

if __name__ == '__main__':
    # entry point by python -m odf under the root folder

    '''
    system = System('s1', max_devices=3)
    log.info('creating bc')
    bc = system.add_device(mode=Mode.BC, address=0)
    log.info('creating rt')
    rt = system.add_device(mode=Mode.RT, address=1)
    log.info('creating adversarials')
    DataInjectionForRT(target=1).go(system)
    log.info('sending data')
    # ignore limit for now so the injection can be successful
    # [otherwise the BC is too fast]
    bc.act_bc2rt(1, [Data(0xa0a0)]*100, ignore_limit=True)
    system.join()
    '''

    # run another simulation at the same time:
    system2 = System('s2', max_devices=7)
    bc = system2.add_device(mode=Mode.BC, address=0)
    rt = system2.add_device(mode=Mode.RT, address=1)
    rt = system2.add_device(mode=Mode.RT, address=2)
    rt = system2.add_device(mode=Mode.RT, address=3)
    rt = system2.add_device(mode=Mode.RT, address=4)
    monitor = Monitor(system2)
    
    #Attack 1 (Tested for 3 scenarios): The following instruction executes the collision attack against the entire bus (irrespective of RTs)
    #Collision_Attack_against_the_Bus().go(system2)
    
    #Attack 2 (Tested for 3 scenarios): The following instruction executes the collision attack on a specific target RT
    #Collision_Attack_against_an_RT(target=4).go(system2)
     
    #Attack 3 (Tested for 2 scenarios, RT2BC not concerned): The following instruction executes the data thrashing attack on a specific target RT
    #Data_Thrashing_Attack_against_an_RT(target=2).go(system2)    
 
    #Attack 4 (Tested for one case, RT2RT): The following instruction executes the MITM attack by creating an illegitimate data flow between two observed RTs
    #MITM_attack_on_RTs().go(system2)    
    
    #Attack 5 (Tested for one case, RT2RT): The following instruction executes the TX shutdown attack through a fake command mode code (targets specific RTs)
    #Shutdown_Attack_on_RT(target=1).go(system2)    

    #Attack 6 (Tested for one case, RT2RT and BC2RT): The following instruction executes the fake status word attack through a fake status mode code (targets specific RTs)
    #Fake_Status_reccmd().go(system2)
    
    #Attack 7 (Tested for one case, RT2RT and RT2BC): The following instruction executes the fake status word attack through a fake status mode code (targets specific RTs)
    #Fake_Status_trcmd(target=1).go(system2)    
    
    #Attack 8 (Tested for one case, RT2RT and BC.RT): The following instruction executes the desynchronization attack through a fake synchronization mode code command (targets specific RTs)
    #Desynchronization_Attack_on_RT(target=2).go(system2) 
    
    #Attack 9 (Tested for one case, RT2RT and RT2BC): The following instruction executes the data corruption attack through a fake status word and data in race condition (targets specific RTs)
    #Data_Corruption_Attack(target=2).go(system2)
    
    #Attack 10 (Tested for one case, RT2RT, BC2RT, and RT2BC): The following instruction executes the command invalidation by sending a fake command (targets specific RTs)
    # Command_Invalidation_Attack(target=2).go(system2) 

    #****************************************************************************
    #****************************************************************************
    #****************************************************************************
    
       
    #To simulate Attack 10, uncomment one of the following communication scenarios:
    #------------------------------------------------------------------------------ 
    # bc.act_rt2bc(2, 2)
    #bc.act_rt2rt(2, 3, 3)

    # To simulate Attack 9, uncomment one of the following communication scenarios:
    # ------------------------------------------------------------------------------
    #bc.act_rt2bc(2, 2)
    #bc.act_rt2rt(2, 3, 3)
   
   
    #To simulate Attack 8, uncomment one of the following communication scenarios:
    #------------------------------------------------------------------------------ 
    #bc.act_rt2bc(2, 2)
    #bc.act_rt2rt(2, 3, 3)
    #bc.act_bc2rt(2, [Data(0x3333)]*7)
   
   
    #To simulate Attack 7, uncomment one of the following communication scenarios:
    #------------------------------------------------------------------------------ 
    #bc.act_rt2bc(1, 2)
    #bc.act_rt2rt(1, 2, 3)


    #To simulate Attack 6, uncomment one of the following communication scenarios:
    #------------------------------------------------------------------------------ 
    #bc.act_rt2rt(2, 3, 3)
    #bc.act_bc2rt(2, [Data(0x3333)]*7)
   
  
    #To simulate Attack 5, uncomment one of the following communication scenarios:
    #------------------------------------------------------------------------------ 
    #bc.act_rt2bc(1, 2)
    #bc.act_rt2rt(1, 2, 3)
    # bc.act_rt2rt(2, 1, 3)  #This assumes that an RT can receive commands when being in RECEIVE mode
    #bc.act_bc2rt(1, [Data(0x3333)]*7)

    # To simulate Attack 4, uncomment one of the following communication scenarios:
    # ------------------------------------------------------------------------------
    #bc.act_rt2rt(2, 3, 3)
    # time.sleep(50)
    #bc.act_rt2rt(4, 1, 3)

    # To simulate Attack 3, uncomment one of the following communication scenarios:
    # ------------------------------------------------------------------------------
    # bc.act_rt2rt(1, 2, 3)
    # bc.act_bc2rt(2, [Data(0x3333)]*7)
   
   
    #To simulate Attack 2, uncomment one of the following communication scenarios:
    #------------------------------------------------------------------------------ 
    # bc.act_rt2bc(4, 2)
    #bc.act_rt2rt(4, 3, 3)
    # bc.act_bc2rt(4, [Data(0x3333)]*7)

    # To simulate Attack 1, uncomment one of the following communication scenarios:
    # ------------------------------------------------------------------------------
    bc.act_rt2bc(4, 2)
    # bc.act_rt2rt(4, 3, 3)
    # bc.act_bc2rt(4, [Data(0x3333)]*7)

    time.sleep(30)
    system2.shutdown()
    monitor.log_data()
