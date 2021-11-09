import sys
import os
import logging as log
import logging.handlers as handlers
from queue import Queue
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections


class Configurations(object):

    DEBUG = False
    CI = False

    FLASK_NAME = 'OD1NF1ST'
    FLASK_PORT = '8572'
    DATA_PATH = 'odf_data'
    DATA_PATH_TMP = 'odf_data/tmp'

    SYS_LOG_EVENT_WORD_REC = False
    SYS_LOG_EVENT = False
    SYS_BUS_RRC_TIMEOUT = 1
    SYS_MAX_SIM = 10
    DEFAULT_RT_DELAY = 0

    DEFAULT_REPLICAS = 1
    DEFAULT_SHARDS = 1

    ES_IP = "127.0.0.1"
    ES_PORT = "9200"
    ES_JVM = "-Xmx2g -Xms2g"
    ES_TIMEOUT = 60

    def __init__(self, **kwargs):
        for k, v in Configurations.__dict__.items():
            if k in os.environ:
                if isinstance(v, bool):
                    value = True if os.environ[k] == 'True' else False
                else:
                    value = type(v)(os.environ[k])
                object.__setattr__(self, k, value)
        self.update(kwargs)

    def update(self, Configurations):
        for k, v in Configurations.items():
            k = k.upper()
            object.__setattr__(self, k, v)
            os.environ[k] = str(v)

    def __setattr__(self, name, value):
        os.environ[name] = value
        object.__setattr__(self, name, value)


config: Configurations = Configurations()

if not os.path.exists(config.DATA_PATH):
    os.makedirs(config.DATA_PATH)
if not os.path.exists(config.DATA_PATH_TMP):
    os.makedirs(config.DATA_PATH_TMP)

log_handler = log.StreamHandler(sys.stdout)
logs = Queue()
if "pytest" in sys.modules:
    log_handler = handlers.QueueHandler(Queue)

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s [PID-%(process)-5.5s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        # log.FileHandler(
        #     "{0}/{1}.log".format(config.DATA_PATH, 'runtime')),
        log.StreamHandler(sys.stdout)
    ])
