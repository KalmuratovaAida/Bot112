import pjsua2 as pj
from bot import endpoint, account
from bot.configuration import AppConfig


class Application:
    def __init__(self) -> None:
        self.config = AppConfig()
        self.ep = endpoint.Endpoint()
        self.accs = []

    def start(self, app_cfg_path, acc_cfg_path, dgis_cfg_path):
        self.config.load_file(app_cfg_path)

        self.ep.libCreate()
        self.ep.libInit(self.config.epConfig)
        self.ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, self.config.udp)

        acc = account.Account(acc_cfg_path, dgis_cfg_path, self.ep)
        self.accs.append(acc)
        acc.create(acc.cfg)

        self.ep.audDevManager().setPlaybackDev(
            self.config.playbackDevId)  # INPUT Line 1
        self.ep.audDevManager().setCaptureDev(self.config.captureDevId)  # OUTPUT Line 2

        self.ep.libStart()
        acc.loop()


if __name__ == '__main__':
    app = Application()
    app.start(app_cfg_path='data/app.cfg', acc_cfg_path='data/acc.cfg', dgis_cfg_path='data/dgis.cfg')
