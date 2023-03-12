from database import funcs
from web import web_session, export, csrf
from flask import Blueprint, jsonify, request, send_file, session
from flask_login import login_required, current_user
from collections import defaultdict
from io import BytesIO
import codecs

api = Blueprint('api', __name__, url_prefix='/api')


# @api.app_errorhandler(401)
# def error401(e):
#     return jsonify(status='error', message='Unauthorized. Please log in.'), 401


# @api.app_errorhandler(404)
# def error404(e):
#     return jsonify(status='error', message='Not found. Try again.'), 404


@api.route('/')
@login_required
def main():
    return jsonify(status='ok')


@api.route('/all_calls')
@login_required
def all_calls():
    calls = funcs.get_all_calls(session=web_session)
    if calls:
        return jsonify(status='ok', data=[{'id': c.call_id,
                                           'number': c.number,
                                           'incident': c.incident,
                                           'address': c.address,
                                           'datetime': c.datetime,
                                           'processed': c.processed,
                                           'account': c.account_id} for c in calls])
    else:
        return jsonify(status='error', data=[])


@api.route('/call')
@login_required
def call():
    cid = request.args.get('cid')
    res = funcs.get_one_call(cid, session=web_session)
    if res[0]:
        c = res[1]
        return jsonify(status='ok', data={'id': c.call_id,
                                          'number': c.number,
                                          'incident': c.incident,
                                          'address': c.address,
                                          'datetime': c.datetime,
                                          'processed': c.processed,
                                          'account': c.account_id,
                                          'transcription': c.transcription,
                                          'point': c.point})
    else:
        return jsonify(status='error', message=res[1])


@api.route('/call_mp3')
@login_required
def call_mp3():
    cid = request.args.get('cid', default=-99)
    res = funcs.get_call_record(cid, session=web_session)
    if res[0]:
        cr = res[1]
        return send_file(BytesIO(cr.mp3), mimetype='audio/vnd.wave', attachment_filename=f'{cid}.wav')
    else:
        return jsonify(status='error', message=res[1])


@api.route('/update_call')
@login_required
def update_call():
    cid = request.args.get('cid', default=-99)
    proceed = int(request.args.get('proceed', default=True))
    res = funcs.update_call(cid, bool(proceed), current_user.aid, session=web_session())
    if res[0]:
        return jsonify(status='ok', message=res[1])
    else:
        return jsonify(status='error', message=res[1])


@api.route('/delete_call')
@login_required
def delete_call():
    cid = request.args.get('cid', default=-99)
    res = funcs.delete_call(cid, session=web_session())
    if res[0]:
        return jsonify(status='ok', message=res[1])
    else:
        return jsonify(status='error', message=res[1])


@api.route('/avatar')
@login_required
def avatar():
    aid = request.args.get('aid', default=-99)
    res = funcs.get_account_avatar(aid, session=web_session())
    if res[0]:
        av = res[1]
        return send_file(BytesIO(av.avatar), mimetype='image/jpeg', attachment_filename=f'{av.avatar_id}.jpg')
    else:
        return send_file('static/noavatar.jpg', mimetype='image/jpeg', attachment_filename='noavatar.jpg')


@api.route('/count_by_date')
@login_required
def count_by_date():
    data = {
        'datasets': [],
        'dataCols': []
    }
    result = funcs.count_calls_group_by_date_inc(days=30, session=web_session())
    if result:
        d = defaultdict(list)
        for item in result:
            d[item[0]].append(item[1:3])
        [data['datasets'].append({'dataName': inc, 'data': value}) for inc, value in d.items()]

    result = funcs.count_calls_group_by_date(days=30, session=web_session())
    data['datasets'].append(
        {'dataName': 'Все звонки',
         'data': [(r[0], r[1]) for r in result]}
    )

    return jsonify(status='ok', data=data)


@api.route('/export/<path:filetype>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def export_func(filetype):
    if filetype not in ('word', 'excel'):
        return jsonify(status='error', message='incorrect export type')

    if request.method == 'GET':
        days = 30
        processed = funcs.count_calls_by_proceed(days, session=web_session())
        incidents = funcs.count_calls_by_incident(days, session=web_session())
        dates = funcs.count_calls_by_datetime(session=web_session())
        if filetype == 'word':
            file_data = export.word({**{r[0]: r[1] for r in incidents},
                                     **{f't{str(r[0])}': r[1] for r in processed},
                                     **{t: r for r, t in zip(dates, ('month', 'sdays', 'tdays', 'today'))},
                                     }, filename=session.get('filename', None))
            return send_file(file_data,
                             mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             attachment_filename='stat.docx')
        elif filetype == 'excel':
            file_data = export.excel({**{r[0]: r[1] for r in incidents},
                                      **{'обработано' if r[0] else 'не обработано': r[1] for r in processed},
                                      **{t: r for r, t in zip(dates, ('месяц', '7 дней', '3 дня', 'сегодня'))}})
            return send_file(file_data,
                             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             attachment_filename='stat.xlsx')

    image_b64 = request.form.get('image', None).encode()
    if image_b64:
        session['filename'] = f'temp/{current_user.aid}_temp.png'
        with open(session['filename'], 'wb') as f:
            f.write(codecs.decode(image_b64, 'base64'))

    return jsonify(status='ok', message='go redirect wahahahaha')


print('Api blueprint imported!')
