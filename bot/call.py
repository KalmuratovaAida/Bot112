import pjsua2 as pj

import bot.endpoint as ep


class Call(pj.Call):
    def __init__(self, acc, call_id, random_id):
        pj.Call.__init__(self, acc, call_id)
        self.rec = None
        self.acc = acc
        self.connected = False
        self.random_id = random_id

    def onCallState(self, prm):
        ci = self.getInfo()
        self.connected = ci.state == pj.PJSIP_INV_STATE_CONFIRMED
        print('on call state --', self.connected)
        if ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.acc.bot_start()
        if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            if self.acc.current_call == self:
                self.acc.call_active = False
                self.acc.current_call = None
                del self.rec

    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for mi in ci.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
                    (mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE or
                     mi.status == pj.PJSUA_CALL_MEDIA_REMOTE_HOLD):
                am = self.getAudioMedia(mi.index)

                self.rec = pj.AudioMediaRecorder()
                self.rec.createRecorder(f'temp/call_{self.random_id}.wav')

                # connect ports
                cap_dev = ep.Endpoint.instance.audDevManager().getCaptureDevMedia()
                cap_dev.startTransmit(am)

                am.startTransmit(ep.Endpoint.instance.audDevManager().getPlaybackDevMedia())
                cap_dev.startTransmit(self.rec)
                am.startTransmit(self.rec)

    def onDtmfDigit(self, prm):
        print(f'Got DTMF: {prm.digit}')
        if prm.digit == '7':
            pass

    def sendDtmfDigit(self, digit):
        dtmf = pj.CallSendDtmfParam()
        dtmf.digits = str(digit)
        self.sendDtmf(dtmf)
