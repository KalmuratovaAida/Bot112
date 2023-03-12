import logging
import wave
from io import BytesIO
import random

import pyaudio
import speech_recognition as sr

from bot.dialogflow import DialogflowClass

PLAYBACK_ID = 7  # INPUT Line 2
CAPTURE_ID = 4  # OUTPUT Line 1


class Bot:

    def __init__(self, df_cred, stt_cred) -> None:
        self.df = DialogflowClass(df_cred)
        self.rc = sr.Recognizer()
        self.rc.pause_threshold = 3
        self.logger = logging.getLogger()
        self.pa = pyaudio.PyAudio()
        self.sid = random.randint(1, 9999)
        self.PLAYBACK_ID = 7
        self.CAPTURE_ID = 4

        with open(stt_cred, 'r') as file:
            self.stt_key = file.read()

    def listen_mic(self) -> str or None:
        print('Listening...')
        with sr.Microphone(device_index=self.CAPTURE_ID) as source:
            try:
                return self.rc.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print('Say something!')
                return None

    def recognize(self, data):
        try:
            if data is not None:
                print('Recognizing...')
                res = self.rc.recognize_google_cloud(
                    data, self.stt_key, language='ru-RU')
                print(f'You said: {res}')
                return res
            else:
                return '. . .'
        except (sr.UnknownValueError, sr.RequestError, EOFError) as e:
            print(e)
            return '. . .'

    def answer(self, query: str):
        print('Thinking...')
        try:
            response = self.df.get_answer(
                query, self.sid)
            return response
        except Exception as e:
            print(e)
            return None

    def playback(self, audio):
        bts = BytesIO(audio)
        f = wave.open(bts)
        stream = self.pa.open(format=self.pa.get_format_from_width(f.getsampwidth()),
                              channels=f.getnchannels(),
                              rate=f.getframerate(),
                              output=True,
                              output_device_index=self.PLAYBACK_ID)
        data = f.readframes(1024)
        while data:
            stream.write(data)
            data = f.readframes(1024)
        stream.stop_stream()
        stream.close()

    def greeting(self):
        response = self.answer('привет')
        if response['audio']:
            self.playback(response['audio'])
