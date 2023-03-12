from database import engine
from flask import Flask
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from flask_moment import Moment
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.url_map.strict_slashes = False
app.jinja_env.globals.update(zip=zip)

csrf = CSRFProtect()
csrf.init_app(app)

talisman = Talisman(app, content_security_policy={'default-src': '\'self\'',
                                                  'media-src': ['\'self\'',
                                                                'youtube.com',
                                                                'youtu.be'],
                                                  'img-src': ['*',
                                                              'data:'],
                                                  'script-src': [
                                                      '\'self\'',
                                                      'cdn.jsdelivr.net',
                                                      'code.jquery.com',
                                                      'cdnjs.cloudflare.com',
                                                      'cdn.jsdelivr.net',
                                                      'code.jquery.com',
                                                      'cdn.datatables.net',
                                                      'momentjs.com',
                                                      'https://cdnjs.cloudflare.com'
                                                  ],
                                                  'style-src': [
                                                      '\'self\'',
                                                      'cdn.jsdelivr.net',
                                                      'use.fontawesome.com',
                                                      'cdnjs.cloudflare.com',
                                                      'cdn.datatables.net',
                                                  ],
                                                  'font-src': [
                                                      '\'self\'',
                                                      'use.fontawesome.com'
                                                  ]
                                                  },
                    content_security_policy_nonce_in=['script-src'],
                    feature_policy={
                        'geolocation': '\'none\'',
                    }
                    )

app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.secret_key = 'CZ3EL5IH12ASMQ6RRXV3458JBC2GPDK0JL3RCKPGU648NBO5'
manager = LoginManager(app)

session_factory = sessionmaker(engine, autocommit=False, autoflush=False)
web_session = scoped_session(session_factory=session_factory)

moment = Moment(app)


@app.teardown_appcontext
def cleanup(r):
    web_session.remove()


from web.api import api
from web import routes, models

app.register_blueprint(api)

print('Flask init complete!')
