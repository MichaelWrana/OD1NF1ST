# python -m odf.mfs.collector

import datetime
import os
import time
from datetime import datetime
from threading import Thread

import cv2
import mss
import pandas as pd
import wave
import pyaudio
from odf.config import config
from PIL import Image
import numpy
import json

sensors = {
    # up to seven groups, each group has up to 32/2=16 float values. (max rt2rt)

    'Instrument': [

        # Instrument Data (Shown to User)
        'AIRSPEED_INDICATED', 'VERTICAL_SPEED', 'INDICATED_ALTITUDE',
        'WISKEY_COMPASS_INDICATION_DEGREES', 'PLANE_HEADING_DEGREES_GYRO', 'HEADING_INDICATOR',
        'ANGLE_OF_ATTACK_INDICATOR',

        # Fuel Data
        'FUEL_TOTAL_QUANTITY', 'ESTIMATED_FUEL_FLOW'

    ],


    'Speed': [
        # Raw Speed Data (in ft/s and ft/s^2) relative to world
        'GROUND_VELOCITY', 'TOTAL_WORLD_VELOCITY', 'VELOCITY_WORLD_X', 'VELOCITY_WORLD_Y', 'VELOCITY_WORLD_Z',
        'ACCELERATION_WORLD_X', 'ACCELERATION_WORLD_Y', 'ACCELERATION_WORLD_Z',

        # Raw Speed Data (in ft/s and ft/s^2) relative to plane
        'VELOCITY_BODY_X', 'VELOCITY_BODY_Y', 'VELOCITY_BODY_Z',
        'ACCELERATION_BODY_X', 'ACCELERATION_BODY_Y', 'ACCELERATION_BODY_Z'],

    # Angle and Turning Data (in radians not degrees)
    'Angle': ['PLANE_PITCH_DEGREES', 'PLANE_BANK_DEGREES',
              # AoA and Sideslip angles
              'INCIDENCE_ALPHA', 'INCIDENCE_BETA'],

    # GPS and Position Data
    'GPS': ['GPS_POSITION_LAT', 'GPS_POSITION_LON', 'GPS_POSITION_ALT',
            'PLANE_LATITUDE', 'PLANE_LONGITUDE', 'PLANE_ALTITUDE'],

    # Weather and Conditions Data
    'Weather': ['AMBIENT_DENSITY', 'AMBIENT_TEMPERATURE', 'AMBIENT_PRESSURE',
                'AMBIENT_WIND_VELOCITY', 'AMBIENT_WIND_X', 'AMBIENT_WIND_Y', 'AMBIENT_WIND_Z',
                'TOTAL_AIR_TEMPERATURE'],

    # Time Data
    # 'Time': ['TIME_OF_DAY', 'ABSOLUTE_TIME', 'LOCAL_TIME'],

    # # Some data pieces that rarely change
    # 'Some': ['NUMBER_OF_ENGINES', 'FUEL_TOTAL_CAPACITY'],

    # Autopilot Data
    # 'Autopilot': ['AI_DESIRED_SPEED', 'AI_DESIRED_HEADING', 'AI_GROUNDCRUISESPEED',
    #               'AI_GROUNDTURNSPEED']

}


class VideoRecorder(Thread):

    def __init__(self, folder, monitor=0) -> None:
        self.folder = folder
        self.running = True
        self.monitor = monitor
        Thread.__init__(self)

    def run(self):
        with mss.mss() as sct:
            monitor = sct.monitors[self.monitor]
            monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
            # codec = cv2.VideoWriter_fourcc(*"XVID")
            codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            frames = []
            start = datetime.now()
            while self.running:
                pic = sct.grab(monitor)
                im = cv2.cvtColor(numpy.array(pic), cv2.COLOR_BGRA2BGR)
                frames.append(im)

            duration = (datetime.now() - start).total_seconds()
            fps = len(frames) / duration
            print('saving data... fps: ', fps)
            out = cv2.VideoWriter(
                os.path.join(
                    self.folder, 'video.avi'),
                codec,
                fps,
                (monitor['width'], monitor['height'])
            )
            for im in frames:
                out.write(im)

            out.release()
            print('saved')

    def done(self):
        self.running = False


class AudioRecorder():

    def __init__(self, folder, device=0) -> None:
        self.device = device
        self.folder = folder
        self.running = True
        self.stream = None

    def start(self):
        audio = pyaudio.PyAudio()
        self.wavefile = wave.open(os.path.join(self.folder, 'audio.wav'), 'wb')
        self.wavefile.setnchannels(2)
        self.wavefile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        self.wavefile.setframerate(44100)

        self.stream = audio.open(
            input_device_index=self.device,
            format=pyaudio.paInt16, channels=2,
            rate=44100, input=True,
            frames_per_buffer=1024,
            # recording speaker
            as_loopback=True,
            stream_callback=self.get_callback())

        self.stream.start_stream()

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback

    def done(self):
        if self.stream and self.running:
            self.stream.stop_stream()
            self.wavefile.close()
        self.running = False


class MFSCollector(Thread):

    def __init__(self, folder, keys, interval=300) -> None:
        from SimConnect import AircraftRequests, SimConnect
        # Create SimConnect link
        sm = SimConnect()
        # Note the default _time is 2000 to be refreshed every 2 seconds
        aq = AircraftRequests(sm, _time=interval)
        self.interval = interval
        self.aq = aq
        self.sm = sm
        self.all_data = []
        self.running = True
        self.folder = folder
        self.keys = keys
        Thread.__init__(self)

    def pull_mfs(self):
        data = {'_t': datetime.now()}

        print("Collecting: " + str(datetime.now()))
        for k in self.keys:
            data[k] = self.aq.get(k)

        return data

    def run(self):
        self.all_data.clear()
        while self.running:
            time.sleep(self.interval/1000)
            self.all_data.append(self.pull_mfs())

        csv = os.path.join(
            self.folder, 'msf.csv'
        )
        # sorted columns by name (so _t will be the first)
        pd.DataFrame(self.all_data).sort_index(axis=1).to_csv(csv)
        self.sm.exit()

    def done(self):
        self.running = False


def record(monitor=0, audio=0):
    folder = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folder = os.path.join(
        config.DATA_PATH, folder
    )
    os.makedirs(folder)

    keys = [k for v in sensors.values() for k in v]
    with open(os.path.join(folder, 'keys.json'), 'w') as wf:
        json.dump(sensors, wf)

    mfs = MFSCollector(folder, keys=keys)
    rcv = VideoRecorder(folder, monitor=monitor)
    #rca = AudioRecorder(folder, device=audio)

    mfs.start()
    rcv.start()
    # rca.start()

    input("Press Enter to STOP recording...")

    # rca.done()
    mfs.done()
    rcv.done()

    # wait for threads to finish

    mfs.join()
    rcv.join()


def print_device():
    print('monitors')
    with mss.mss() as sct:
        for m in sct.monitors:
            print(m)
    print()
    print('audio')
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        d = p.get_device_info_by_index(i)
        print(i, d['name'], 'out:{}'.format(d['maxOutputChannels']),
              'in:{}'.format(d['maxInputChannels']), )


if __name__ == '__main__':

    # print_device()
    record(audio=4, monitor=1)
