import logging
import pytest
from odf import *
from odf.mfs import Monitor


def test_rt2rt():
    logs.empty()
    system2 = System('s2', max_devices=7)
    system2.add_device(mode=Mode.RT, address=1)
    system2.add_device(mode=Mode.RT, address=2)
    system2.add_device(mode=Mode.BC, address=0).act_rt2rt(1, 2, 3)
    time.sleep(5)
    system2.shutdown()
