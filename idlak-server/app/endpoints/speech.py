# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import uuid
import time
import shutil
import wave
import uuid
import struct
from app import app, api, jwt, reqparser
from app.respmsg import mk_response
from app.middleware.auth import not_expired
from flask import send_from_directory
from flask_restful import Resource, abort, request
from flask_jwt_simple import jwt_required
from app.models.voice import Voice

sys.path.append('../src/')
from pyIdlak import TangleVoice         # noqa

spch_parser = reqparser.RequestParser()
spch_parser.add_argument('voice_id', help='Provide a voice id',
                         location='json', required=True)
spch_parser.add_argument('audio_format', choices=['wav', 'ogg', 'mp3'],
                         help='Valid choices: wav|ogg|mp3, default=wav',
                         location='json', default='wav')
spch_parser.add_argument('text', help='Provide a text to syntesise speech',
                         location='json', required=True)


def _convert_to(audio_format, filename):
    """ Converts a wav audio file into a provided audio format

        Args:
            audio_format (str): format of audio (assuming correct - ogg|mp3)
            filename (str): path of the file with its name
                            (assuming has extension of wav file)

        Returns:
            (str): filename of the converted file
    """
    new_filename = filename[:-3] + audio_format
    command = "ffmpeg -i {} {}".format(filename, new_filename)
    return_code = subprocess.call(command, shell=True)
    return new_filename


def _wav_to_file(waveform, fn, srate=48000):
    wav = wave.open(fn, 'wb')
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(srate)
    for w in waveform:
        wout = int(max(min(w, 0x7fff), (-0x7fff - 1)))  # ensures in range
        write_data = struct.pack("<h", wout)
        wav.writeframes(write_data)
    wav.close()


class Speech(Resource):
    decorators = ([not_expired, jwt_required]
                  if app.config['AUTHENTICATION'] else [])

    def post(self):
        """ Speech endpoint

            Args:
                voice_id (str): id of the voice
                audio_format (str, optional): wav|ogg|mp3
                text (str): text to process

            Returns:
                streamed audio file of the processed speech
        """

        args = spch_parser.parse_args()
        if isinstance(args, app.response_class):
            return args
        voice = Voice.query.filter_by(id=args['voice_id']).first()
        if voice is None:
            return mk_response("Voice could not be found", 400)

        # creating syntesised speech and saving into file
        tanglevoice = TangleVoice(voice_dir=os.path.abspath(voice.directory))
        audio_fn = os.path.abspath(uuid.uuid4().hex[:8] + '.wav')
        waveform = tanglevoice.speak(args['text'])
        _wav_to_file(waveform, audio_fn)

        # convert to requested type
        if 'audio_format' in args and args['audio_format'] != "wav":
            old_audio_fn = audio_fn
            audio_fn = _convert_to(args['audio_format'], audio_fn)
            os.remove(old_audio_fn)
        elif 'audio_format' not in args:
            args['audio_format'] = "wav"
        # get the audio as bytes, delete the file and return audio as bytes
        with open(audio_fn, 'rb') as audio_f:
            wavefile = b''.join(audio_f.readlines())
        os.remove(audio_fn)
        response = app.make_response(wavefile)
        response.headers['Content-Type'] = 'audio/' + args['audio_format']
        return response


api.add_resource(Speech, '/speech')
