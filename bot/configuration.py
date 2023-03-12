import pjsua2 as pj
from configparser import ConfigParser


class AppConfig():
	def __init__(self) -> None:
		self.epConfig = pj.EpConfig()
		self.udp = pj.TransportConfig()
		self.playbackDevId = 0
		self.captureDevId = 0

	def load_file(self, path):
		cfg = ConfigParser()
		if cfg.read(path):
			self.udp.port = cfg.getint('TRANSPORT_UDP','PORT')
			self.playbackDevId = cfg.getint('AUDIO_DEV', 'PLAYBACK_ID')
			self.captureDevId = cfg.getint('AUDIO_DEV', 'CAPTURE_ID')
		else:
			self.defaults()

	def defaults(self):
		self.udp.port = 5060
