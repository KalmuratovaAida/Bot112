from bot.app import Application
import os


if __name__ == '__main__':
    for f in os.listdir('temp'):
        try:
            os.remove(os.path.join('temp', f))
        except Exception as e:
            print('Failed to delete temp file. Reason: ', e)
    print('Temp folder clean complete.')

    app = Application()
    app.start(app_cfg_path='bot/data/app.cfg', acc_cfg_path='bot/data/acc.cfg', dgis_cfg_path='bot/data/dgis.cfg')
