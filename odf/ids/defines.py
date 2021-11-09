import os
from odf.components import Word
from odf.config import config
import jsonpickle
from pathlib import Path


class IDS():
    prepared = False

    @classmethod
    def get_data_path(cls):
        return os.path.join(config.DATA_PATH, 'dump')

    @classmethod
    def get_prepared_data(cls):
        # data for trianing
        folder = cls.get_data_path()
        return [
            jsonpickle.decode(
                Path(os.path.join(folder, f)).read_text()
            ) for f in os.listdir(folder)]

    @classmethod
    def get_model_path(cls):
        p = os.path.join(config.DATA_PATH, 'models', cls.__name__)
        if not os.path.exists(p):
            os.makedirs(p)
        return p

    def prepare(self):
        pass

    def monitor(self, t: int, word: Word):
        # t: time, word: Data/Status/Command
        # return a tuple of two values:
        # anormaly score, list of attack probabilities
        return 0, []
