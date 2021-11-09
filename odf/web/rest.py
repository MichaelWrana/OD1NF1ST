
import inspect
import io
import json
from odf.utils import all_subclasses, load_class
from typing import Generator, Type
import logging as log
import os
from shutil import unpack_archive

import jsonpickle
from flask import abort, jsonify, send_file, Response
from flask_restful import Api, Resource, inputs, reqparse, request
from odf.web.resources import bp_api, configure_parser_for_file
from odf.config import config
from odf.utils import all_subclasses
from odf.sabotage import Sabotage, all_attacks
from odf.ids.models import GCNN, OD1N
from slugify import slugify
from odf.mfs.sim import serve_data, Sim, generate_frames
import logging as log
import inspect


running_systems = []


def error(message):
    return {'err': True, 'msg': message}


@bp_api.route('/get_scenes', methods=['GET'])
def get_scenes():
    return jsonify(
        [{'name': p,
          'thumbnail': os.path.join('api', 'dat', p, 'thumbnail.png'),
          'video': os.path.join('api', 'dat', p, 'video.mp4')
          }
         for p in os.listdir(config.DATA_PATH)
         if os.path.isdir(os.path.join(config.DATA_PATH, p))
         and p != 'tmp' and p != 'dump' and p != 'models'])


@bp_api.route('get_sim', methods=['GET'])
def get_sim():
    if len(running_systems) < 1:
        return error('no system is running')
    try:
        sim = running_systems[0]
        sim: Sim
        return sim.to_dict()
    except Exception as e:
        log.error(e)
    return {}


@bp_api.route('read_ids', methods=['GET'])
def get_ids():
    if len(running_systems) < 1:
        return error('no system is running')
    sim = running_systems[0]
    sim: Sim
    res = list(sim.get_ids())
    if len(res) == 0:
        res = [0] * (len(all_attacks)+1)
    else:
        res = [res[0], *res[1]]
    return jsonify(res)


@bp_api.route('/run/<scene>', methods=['POST'])
def run_scene(scene):
    scene = slugify(scene)
    target = os.path.join(config.DATA_PATH, scene)
    if not os.path.exists(target):
        log.info(target)
        return error('scene not existed. [{}]'.format(scene))
    if len(running_systems) > 0:
        return error('a simulation is already running.')

    sim = serve_data(scene, ids=OD1N())
    running_systems.append(sim)
    return {}


@bp_api.route('/takeoff', methods=['POST'])
def take_off():
    if len(running_systems) < 1:
        return error('no system is running')
    try:
        sim = running_systems[0]
        sim: Sim
        if not sim.running:
            sim.run()
    except Exception as e:
        log.error(e)
    return {}


@bp_api.route('/stop', methods=['POST'])
def stop():
    global running_systems
    if len(running_systems) < 1:
        return error('no system is running')
    try:
        sim = running_systems[0]
        sim: Sim
        running_systems.clear()
        sim.shutdown()
    except Exception as e:
        log.error(e)


@bp_api.route('/read_guages', methods=['GET'])
def read_gauges():
    if len(running_systems) < 1:
        return error('no system is running')
    sim = running_systems[0]
    sim: Sim
    return jsonify(sim.read())


def gen_frames(sim: Sim):
    for frame in generate_frames(sim):
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@bp_api.route('/video_feed')
def read_frame():
    if len(running_systems) < 1:
        return error('no system is running')
    sim = running_systems[0]
    return Response(
        gen_frames(sim),
        mimetype='multipart/x-mixed-replace; boundary=frame')


@bp_api.route('/get_guages', methods=['GET'])
def get_gauges():
    if len(running_systems) < 1:
        return error('no system is running')
    sim = running_systems[0]
    sim: Sim
    return jsonify(sim.get_guages())


@bp_api.route('/list_attacks', methods=['GET'])
def get_attacks():
    attacks = []
    for a in all_subclasses(Sabotage, True):
        a: Type[Sabotage]
        constructor = inspect.signature(a.__init__)
        # log.info('{}'.format(constructor.parameters))
        args = {k: (v.default if v.default != v.empty else '')
                for k, v in constructor.parameters.items() if k != 'self'}
        attacks.append({
            'name': a.name,
            'description': a.descr,
            'class': a.__name__,
            'args': args
        })
    return jsonify(attacks)


@bp_api.route('/sabotage/<attack_class>', methods=['POST'])
def launch_attack(attack_class):
    req_json = request.get_json()
    log.info(f'{attack_class} - {req_json}')
    if len(running_systems) < 1:
        return error('no system is running')
    sim = running_systems[0]
    sim: Sim
    sim.sabotage(attack_class, req_json)
    return {}
