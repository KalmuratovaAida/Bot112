from sqlalchemy.orm import scoped_session, sessionmaker
from database import engine

session_factory = sessionmaker(engine, autocommit=False, autoflush=False)
bot_session = scoped_session(session_factory=session_factory)
