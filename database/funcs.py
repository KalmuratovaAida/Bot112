from typing import Tuple, Any

from datetime import timedelta
from sqlalchemy.exc import *
from sqlalchemy import func, desc, asc
from database import Session, with_session
from database.models import *


# CALL FUNCS
@with_session
def add_call(number, incident, address, transcription=None, point=None, session=Session()):
    if transcription:
        transcription = '\n'.join(transcription)
    call = Call(number=number, incident=incident, address=address, transcription=transcription,
                point=point)
    try:
        session.add(call)
        session.commit()
        return True, call.call_id

    except Exception as e:
        session.rollback()
        return False, e


@with_session
def add_call_record(call_id, wav_path, session=Session()):
    if wav_path:
        with open(wav_path, 'rb') as f:
            wav_data = f.read()

    record = CallRecord(record_id=call_id, mp3=wav_data)
    try:
        session.add(record)
        session.commit()
        return True, 'ok'
    except Exception as e:
        session.rollback()
        return False, e


@with_session
def update_call(cid, processed, account_id, session=Session()):
    try:
        session.query(Call).filter_by(call_id=cid).update({'processed': processed, 'account_id': account_id},
                                                          synchronize_session="fetch")
        session.commit()
        return True, 'ok'
    except Exception as e:
        session.rollback()
        return False, e


@with_session
def delete_call(cid, session=Session()):
    try:
        call = session.query(Call).filter_by(call_id=cid).one()
        session.delete(call)
        session.commit()
        return True, 'Deleted!'
    except NoResultFound:
        session.rollback()
        return False, 'Call not found!'
    except Exception as e:
        session.rollback()
        return False, e


@with_session
def get_all_calls(session=Session()) -> list:
    result = session.query(Call).all()
    return result if result else False


@with_session
def count_calls_by_incident(days=30, session=Session()):
    _delta = datetime.today().date() - timedelta(days)
    result = session.query(Call.incident, func.count(Call.call_id)).filter(_delta < Call.datetime).group_by(
        Call.incident).all()
    return [(r[0], r[1]) for r in result] if result else [(0, None) for i in range(3)]


@with_session
def count_calls_by_proceed(days=30, session=Session()):
    _delta = datetime.today().date() - timedelta(days)
    result = session.query(Call.processed, func.count(Call.call_id)).filter(_delta < Call.datetime).group_by(
        Call.processed).all()
    return [(r[0], r[1]) for r in result] if result else [(0, None) for i in range(2)]


def count_calls_by_datetime(session=Session()):
    _today = datetime.today().date()
    _3days = datetime.today() - timedelta(3)
    _7days = datetime.today().date() - timedelta(7)
    _month = datetime.today().date().replace(day=1)

    today = session.query(func.count(Call.call_id).filter(_today < Call.datetime)).one()
    three_d = session.query(func.count(Call.call_id).filter(_3days < Call.datetime)).one()
    seven_d = session.query(func.count(Call.call_id).filter(_7days < Call.datetime)).one()
    month = session.query(func.count(Call.call_id).filter(_month < Call.datetime)).one()

    return [r[0] for r in [month, seven_d, three_d, today]]


@with_session
def count_calls_group_by_date(days=30, session=Session()):
    _delta = datetime.today().date() - timedelta(days)
    result = session.query(func.date(Call.datetime), func.count(Call.call_id)).filter(_delta < Call.datetime).group_by(
        func.date(Call.datetime)).all()

    return [(r[0], r[1]) for r in result] if result else False


@with_session
def count_calls_group_by_date_inc(days=30, session=Session()):
    _delta = datetime.today().date() - timedelta(days)
    result = session.query(Call.incident, func.date(Call.datetime),
                           func.count(Call.call_id)). \
        filter(_delta < Call.datetime). \
        group_by(func.date(Call.datetime), Call.incident).all()

    return [(r[0], r[1], r[2]) for r in result] if result else False


@with_session
def get_one_call(cid, session=Session()) -> Tuple[bool, Any]:
    try:
        result = session.query(Call).filter_by(call_id=cid).one()
        return True, result
    except NoResultFound:
        return False, 'Call not found!'


@with_session
def get_call_record(cid, session=Session()):
    try:
        result = session.query(CallRecord).filter_by(record_id=cid).one()
        return True, result
    except NoResultFound:
        return False, 'CallRecord not found!'


# ACCOUNT FUNCS

@with_session
def get_account(username, session=Session()):
    try:
        result = session.query(Account).filter_by(username=username).one()
        return result
    except NoResultFound:
        return None


@with_session
def get_account_avatar(aid, session=Session()):
    try:
        result = session.query(AccountAvatar).filter_by(avatar_id=aid).one()
        return True, result
    except NoResultFound:
        return False, 'Avatar not found!'


@with_session
def add_account(un, pw, fn, ln, session=Session()):
    acc = Account(username=un, password=pw, first_name=fn, last_name=ln)
    try:
        session.add(acc)
        session.commit()
        return True, acc.account_id
    except IntegrityError:
        session.rollback()
        return False, 'Этот логин уже занят!'
    except Exception as e:
        session.rollback()
        return False, e


@with_session
def update_account(username, pw, session=Session()):
    try:
        session.query(Account).filter_by(username=username).update({'password': pw},
                                                                   synchronize_session="fetch")
        session.commit()
        return True, 'ok'
    except Exception as e:
        session.rollback()
        return False, e


@with_session
def log_account(aid, ip, session=Session()):
    al = AccountLog(account_id=aid, ip=ip)
    try:
        session.add(al)
        session.commit()
        return True, 'ok'
    except Exception as e:
        session.rollback()
        return False, e


@with_session
def clear_account_logs(aid, session=Session()):
    deleted = 0
    try:
        count = session.query(func.count(AccountLog.account_id)).filter_by(account_id=aid).one()
        if count[0] > 5:
            sq = session.query(AccountLog.log_id).filter_by(account_id=aid).order_by(
                asc(AccountLog.datetime)).limit(count[0] - 5).subquery()
            deleted = session.query(AccountLog).filter(AccountLog.log_id.in_(sq)).delete(synchronize_session="fetch")
        session.commit()
        return True, deleted

    except Exception as e:
        session.rollback()
        return False, e


@with_session
def get_account_logs(aid, session=Session()):
    result = session.query(AccountLog).filter_by(account_id=aid).order_by(desc(AccountLog.datetime)).limit(5).all()
    return result if result else None


@with_session
def add_account_avatar(aid, avatar, session=Session()):
    ava = AccountAvatar(avatar_id=aid, avatar=avatar)
    try:
        session.add(ava)
        session.commit()
        return True, 'ok'
    except IntegrityError:
        session.rollback()
        return False, 'Этот id уже занят!'
    except Exception as e:
        session.rollback()
        return False, e


print('All database funcs imported!')
