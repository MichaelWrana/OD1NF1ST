from psutil import NoSuchProcess, Process
import collections
import functools
import sys
import logging as log
import os
import urllib.error
import urllib.parse
import urllib.request
import datetime
import threading
from functools import wraps

import requests
from tqdm import tqdm


def fn_from_url(url):
    return os.path.basename(urllib.parse.urlparse(url).path)


def download_file(url, dest, progress=False):

    if os.path.exists(dest) and progress:
        log.info('File already exists {} ...'.format(dest))
    else:
        if progress:
            log.info('downloading from: %s to %s', url, dest)

        r = requests.get(url, stream=True)
        total_length = r.headers.get('content-length')
        pg = tqdm(total=int(total_length)) if (
            total_length is not None and progress) else None
        dl = 0
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    if progress and pg:
                        pg.update(len(chunk))
                    f.write(chunk)
                    f.flush()
        if progress and pg:
            pg.close()

    return dest


def which(program):

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def load_class(s):
    if '.' in s:
        mod, attr = s.rsplit('.', 1)
        __import__(mod)
        mod = sys.modules[mod]
        return getattr(mod, attr)
    else:
        # print(globals())
        mod = globals()[s]()
        return mod


def process_exists(pid):
    if os.name == 'nt':
        try:
            return Process(pid).status() == 'running'
        except NoSuchProcess:
            return False
    else:
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True


def __all_subclasses(cls, recursive=True):
    if issubclass(cls, type):
        subclasses = cls.__subclasses__(cls)
    else:
        subclasses = cls.__subclasses__()
    if recursive:
        for subclass in subclasses:
            subclasses.extend(all_subclasses(subclass))
    return subclasses


def all_subclasses(cls, leaves_only=False):
    classes = __all_subclasses(cls)
    if leaves_only:
        return [x for x in classes if len(__all_subclasses(x, False)) < 1]
    else:
        return classes


class NestedDotGettable(object):
    """Able to access attributes through nested dot path:
    a['b.c.d'] equals a.b.c.d

    """

    def dotget(self, attr, default=None):

        def _get(object, name):
            if isinstance(object, dict):
                return object[name]
            else:
                return getattr(object, name)
        try:
            return functools.reduce(_get, attr.split('.'), self)
        except:
            return None

    def __getitem__(self, key):
        return self.dotget(key)

    def __getattr__(self, name):
        if isinstance(self, dict):
            return self[name]
        raise AttributeError


def time_diff(start, end, formatted=True, auto_end=True):
    if not start:
        if formatted:
            return '0:0:0s'
        return 0, 0, 0
    if auto_end:
        end = end or datetime.now()
    diff = end - start
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if formatted:
        return '{}:{}:{}s'.format(
            hours,
            minutes,
            seconds
        )
    else:
        return hours, minutes, seconds


def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def delay(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'delay' in kwargs:
            sec = kwargs['delay']
            del kwargs['delay']
            if sec > 0:
                t = threading.Timer(sec, func, args, kwargs)
                t.start()
                return
        func(*args, **kwargs)
    return wrapper
