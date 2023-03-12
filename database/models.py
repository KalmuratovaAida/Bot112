from datetime import datetime

from sqlalchemy import (BLOB, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text, BIGINT)
from sqlalchemy.orm import declarative_base, relationship

from database import engine

base = declarative_base()


class Call(base):
    __tablename__ = 'calls'

    call_id = Column(BIGINT, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    number = Column(String(64), nullable=True)
    incident = Column(String(16), nullable=True)
    address = Column(String(32), nullable=True)
    transcription = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    account_id = Column(Integer, ForeignKey(
        'accounts.account_id'), nullable=True)
    point = Column(String(32), nullable=True)

    records = relationship("CallRecord", cascade="all,delete", backref="calls")


class CallRecord(base):
    __tablename__ = 'call_records'

    record_id = Column(BIGINT, ForeignKey('calls.call_id', ondelete='CASCADE'), primary_key=True)
    mp3 = Column(BLOB, nullable=True)


class Account(base):
    __tablename__ = 'accounts'

    account_id = Column(BIGINT, primary_key=True, autoincrement=True)
    username = Column(String(16), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(16), nullable=True)
    last_name = Column(String(16), nullable=True)

    avatar = relationship("AccountAvatar", cascade="all,delete", backref="accounts")


class AccountAvatar(base):
    __tablename__ = 'avatars'

    avatar_id = Column(BIGINT, ForeignKey('accounts.account_id', ondelete='CASCADE'), primary_key=True)
    avatar = Column(BLOB, nullable=True)


class AccountLog(base):
    __tablename__ = 'log_history'

    log_id = Column(BIGINT, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'))
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip = Column(String(16), nullable=False, default='unknown')


class ArchivedCall(base):
    __tablename__ = 'archived'

    call_id = Column(BIGINT, primary_key=True, autoincrement=False)
    datetime = Column(DateTime)
    incident = Column(String(16))
    address = Column(String(32))


base.metadata.create_all(engine)

print('All database models imported!')
