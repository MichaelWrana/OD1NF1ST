import json
import logging
import os
import platform
import re
import subprocess
import sys
import tarfile
from collections import namedtuple
#from zipfile import ZipFile
from shutil import unpack_archive, copytree
from subprocess import Popen
from time import clock, sleep

import requests
import yaml
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections
from odf import config
from odf.utils import download_file, process_exists
from jvd.resources import ResourceAbstract, require
from psutil import Process


class Elastic(ResourceAbstract):
    def __init__(self, version='7.10.1'):
        super().__init__()
        url = 'https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-{}-{}-x86_64.{}'
        self.linux = url.format(version, 'linux', 'tar.gz')
        self.windows = url.format(version, 'windows', 'zip')
        self.darwin = url.format(version, 'darwin', 'tar.gz')
        self.default = self.linux
        self.check_update = False
        self.version = version
        self.unpack = True

    def get(self):
        unpacked = os.path.join(
            super().get(), 'elasticsearch-{}'.format(self.version))
        elastic_cmd = {'windows': [os.path.join(unpacked,  'bin', 'elasticsearch.bat')],
                       'linux': [os.path.join(unpacked,  'bin', 'elasticsearch')],
                       'darwin': [os.path.join(unpacked,  'bin', 'elasticsearch')]
                       }[platform.system().lower()]

        return unpacked, elastic_cmd


MODULE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_es_log_header(log_file, limit=600):
    line = log_file.readline()
    server_pid = None
    es_port = None
    count = 0

    while count < limit:
        count += 1
        line = line.strip()

        if line == '':
            sleep(.1)

        m = re.search('pid\[(\d+)\]', line)
        if m:
            server_pid = int(m.group(1))

        m = re.search(r'publish_address.*:(\d+)}', line)
        if m:
            es_port = int(m.group(1))

        if re.search('started', line):
            return server_pid, es_port

        line = log_file.readline()

    logging.warn(
        'Read more than %d lines while parsing Elasticsearch log header. Giving up ...' % limit)

    return server_pid, es_port


# tuple holding information about the current Elasticsearch process
ElasticsearchState = namedtuple(
    'RunnerStatus', ['server_pid', 'wrapper_pid', 'ip', 'port', 'config_fn'])


class ElasticServer:
    def __init__(self, data_path, transient=False, quiet=False):
        self.es_state = None
        self.es_config = None
        self.es = None
        self.quiet = quiet
        self.wrapper_proc = None
        self.data_path = data_path
        home, cmd = require('elastic')
        self.cmd = cmd
        self.home = home

    def run(self):
        if self.is_running():
            logging.warn('Elasticsearch already running ...')
        else:
            logging.info('Starting up Elasticsearch')
            cluster_name = 'jarv1s-local-es'
            cluster_path = os.path.join(
                self.data_path, 'cluster')
            cluster_path = os.path.abspath(cluster_path)
            es_data_dir = os.path.join(cluster_path, "data")
            es_config_dir = os.path.join(cluster_path, "config")
            if not os.path.exists(es_config_dir):
                copytree(os.path.join(self.home, 'config'), es_config_dir)
            es_log_dir = os.path.join(cluster_path, "log")

            self.es_config = {
                'http': {'cors': {'enabled': True}},
                'cluster': {'name': cluster_name},
                'path': {
                    'logs': es_log_dir,
                    'data': es_data_dir
                },
                'indices.query.bool.max_clause_count': 2147483646,
                'http.max_content_length': '2147483646b'
            }

            config_fn = os.path.join(es_config_dir, 'elasticsearch.yml')

            os.makedirs(es_log_dir, exist_ok=True)
            os.makedirs(es_data_dir, exist_ok=True)
            # os.makedirs(es_config_dir, exist_ok=True)

            with open(config_fn, 'w') as f:
                yaml.dump(self.es_config, stream=f)

            es_log_fn = os.path.join(es_log_dir, '%s.log' % cluster_name)
            open(es_log_fn, 'a').close()

            logging.info('Ready to execute {}'.format(str(self.cmd)))
            es_env = os.environ.copy()
            java_executable = require('jdk')
            if '/' in os.path.dirname(java_executable):
                es_env['ES_PATH_JAVAHOME'] = os.path.dirname(java_executable)
                print(es_env)
            es_env['ES_PATH_CONF'] = es_config_dir
            es_env['ES_PATH_LOGS'] = es_log_dir
            es_env['ES_PATH_DATA'] = es_data_dir
            es_env['ES_JAVA_OPTS'] = config.ES_JVM
            wrapper_proc = Popen(self.cmd, env=es_env)
            self.wrapper_proc = wrapper_proc

            es_log_f = open(es_log_fn, 'r')
            es_log_f.seek(0, 2)

            # watch the log
            server_pid, es_port = parse_es_log_header(es_log_f)

            if not server_pid:
                logging.error(
                    'Server PID not detected ... runcall was %s' % self.cmd)

            if not es_port:
                logging.error('Server http port not detected ...')

            self.es_state = ElasticsearchState(wrapper_pid=wrapper_proc.pid,
                                               server_pid=server_pid,
                                               ip=...,
                                               port=es_port,
                                               config_fn=config_fn)
            self.es = Elasticsearch(timeout=config.ES_TIMEOUT)
            connections.add_connection('default', self.es)
            logging.info(
                'Started Elasticsearch pid {} at port {}'.format(server_pid, es_port))
        return self

    def stop(self):
        if self.is_running():
            logging.info('Stopping Elasticsearch...')
            server_proc = Process(self.es_state.server_pid)
            server_proc.terminate()
            server_proc.wait()

            if process_exists(self.es_state.server_pid):
                logging.warn(
                    'Failed to stop Elasticsearch server process PID %d ...' % self.es_state.server_pid)

            self.es_state = None
            self.es_config = None
        else:
            logging.warn('Elasticsearch is not running ...')

        return self

    def is_running(self):
        state = self.es_state
        return state and state.port and process_exists(state.server_pid)

    def wait_for_green(self, timeout=1.):
        if not self.es_state:
            logging.warn('Elasticsearch runner is not started ...')
            return self

        if self.es_state.port is None:
            logging.warn('Elasticsearch runner not properly started ...')
            return self
        end_time = clock() + timeout
        health_resp = requests.get(
            'http://localhost:%d/_cluster/health' % self.es_state.port)
        health_data = json.loads(health_resp.text)

        while health_data['status'] != 'green':
            if clock() > end_time:
                logging.error('Elasticsearch cluster failed to turn green in %f seconds, current status is %s ...' %
                              (timeout, health_data['status']))

                return self

            health_resp = requests.get(
                'http://localhost:%d/_cluster/health' % self.es_state.port)
            health_data = json.loads(health_resp.text)

        return self

    def wait(self):
        if self.wrapper_proc:
            self.wrapper_proc.wait()


def start_es(wait=False):
    ip = "127.0.0.1"
    port = config.ES_PORT
    timeout = config.ES_TIMEOUT

    logging.info(
        "Starting ES instance http://{ip}:{port}".format(ip=ip, port=port))

    elastic_server = ElasticServer(config.DATA_PATH)
    elastic_server.run()

    setup_all_models()
    if wait:
        elastic_server.wait()
    return elastic_server
