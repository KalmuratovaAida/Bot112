from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

print('Connecting...')
engine = create_engine(f'sqlite+pysqlite:///database/test.db', echo=False,
                       encoding='utf-8')

connect = engine.connect()
print('Connected!')
session_factory = sessionmaker(engine)
Session = scoped_session(session_factory)


def with_session(fn):
    def wrap(*args, **kwargs):
        with Session.begin() as session:
            return fn(*args, **kwargs)
    return wrap
