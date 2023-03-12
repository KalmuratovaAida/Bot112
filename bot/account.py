import time
import threading
import os
from configparser import ConfigParser
from random import randint

import pjsua2 as pj

from bot import call
from bot.bot_funcs import Bot
from bot.dgis import DGis
from database import funcs
from bot import bot_session


class Account(pj.Account):

    def __init__(self, cfg_path, dgis_cfg_path, ep):
        pj.Account.__init__(self)

        self.current_call = None
        self.call_active = False
        self.bot_alive = False
        self.bot_data = {}

        self.ep = ep

        self.cfg = pj.AccountConfig()
        self.load_file(cfg_path)

        self.dgis = DGis(dgis_cfg_path)

    def onRegState(self, prm):
        print('>Registration: ', prm.code, prm.reason)
        pass

    def onIncomingCall(self, prm):
        c = call.Call(self, prm.callId, random_id=randint(10000, 99999))
        status = pj.CallOpParam()
        status.statusCode = 180
        c.answer(status)

        ci = c.getInfo()
        print(f'Incoming call {prm.callId} from {ci.remoteUri}')

        if not self.current_call:
            self.current_call = c
            status.statusCode = 200
            c.answer(status)
        else:
            status.statusCode = 486
            c.hangup(status)

    def load_file(self, path):
        parser = ConfigParser()
        if parser.read(path):
            self.cfg.idUri = parser['ACCOUNT']['SIP_URI']
            self.cfg.regConfig.registrarUri = parser['ACCOUNT']['REGISTRAR_URI']
            cred = pj.AuthCredInfo(
                "digest", "*", parser['ACCOUNT']['USERNAME'], 0, parser['ACCOUNT']['PASSWORD'])
            self.cfg.sipConfig.authCreds.append(cred)
        else:
            raise FileNotFoundError(f'Config file {path} not found')

    def bot_start(self):
        self.bot_alive = True
        self.call_active = True
        self.bot_data = {}
        bot_thr = threading.Thread(target=bot_process, kwargs={'acc': self,
                                                               'active': lambda: self.call_active,
                                                               'caller': self.current_call.getInfo().remoteUri})
        bot_thr.start()

    def bot_success(self, rid):
        if self.bot_data:
            info = self.dgis.get_info(self.bot_data['data']['address'])
            if info:
                self.bot_data['data']['address'] = info['address']
                self.bot_data['data']['point'] = ','.join(info['point'])

            status, cid = funcs.add_call(**self.bot_data['data'],
                                         session=bot_session)
            if status:
                status = funcs.add_call_record(call_id=cid,
                                               wav_path=f'temp/call_{rid}.wav',
                                               session=bot_session)
            if status:
                for f in os.listdir('temp'):
                    try:
                        os.remove(os.path.join('temp', f))
                    except Exception as e:
                        print('Failed to delete temp wav. Reason: ', e)
                print('Temp wav folder clean complete.')

    def loop(self):
        while True:
            self.ep.libHandleEvents(50)
            if self.call_active and not self.bot_alive:
                if not self.bot_data['status']:
                    self.current_call.xfer('sip:112bot1@sip.antisip.com', pj.CallOpParam())
                    self.call_active = False
                    self.current_call.hangup(pj.CallOpParam())

                else:
                    rid = self.current_call.random_id
                    self.current_call.hangup(pj.CallOpParam())
                    self.bot_success(rid)
            time.sleep(0.5)


def bot_process(acc, active, caller):
    bot = Bot('bot/data/dialog.json', 'bot/data/key.json')
    bot.greeting()
    chat_log = []
    while acc.bot_alive and active():
        data = bot.listen_mic()
        query = bot.recognize(data)
        response = bot.answer(query)
        if response:
            bot.playback(response['audio'])
            chat_log.extend((query, response['text']))
            if response['intent'] == 'operator_request':
                acc.bot_alive = False
                acc.bot_data = {
                    'status': False,
                    'data': {}
                }
            if response['is_end'] and response['payload']:
                acc.bot_alive = False
                acc.bot_data = {'status': True,
                                'data': {
                                    'number': caller,
                                    'incident': response['payload']['incident'].strip(),
                                    'address': response['payload']['locationOriginal'].strip(),
                                    'transcription': chat_log,
                                    'point': None}
                                }
    print('Bot stopped!')
