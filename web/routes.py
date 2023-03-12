from database import funcs
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from web.forms import LoginForm, RegForm, ChangePasswordForm
from web.models import User
from web.avatars import Avatar
from web import app, web_session


@app.errorhandler(404)
def error404(e):
    error = {'code': e.code,
             'message': 'Страница не найдена'}
    return render_template('web/error.html', error=error), e.code


@app.errorhandler(500)
def error500(e):
    error = {'code': e.code,
             'message': 'Внутренняя ошибка сервера'}
    return render_template('web/error.html', error=error), e.code


@app.errorhandler(401)
def error401(e):
    return render_template('web/login.html', form=LoginForm()), 401


@app.route('/main')
@app.route('/')
@login_required
def main():
    try:
        days = int(request.args.get('days', default=1826))  # Love magic numbers?
    except ValueError:
        days = 1826

    processed = funcs.count_calls_by_proceed(days, session=web_session())
    incidents = funcs.count_calls_by_incident(days, session=web_session())
    dates = funcs.count_calls_by_datetime(session=web_session())
    data = {'incidents': {r[0]: r[1] for r in incidents},
            'processed': processed,
            'dates': dates,
            'all': sum((r[1] for r in incidents))}
    return render_template('web/main.html', user=current_user, data=data)


@app.route('/calls')
@login_required
def calls():
    return render_template('web/calls.html', user=current_user)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    login_history = funcs.get_account_logs(current_user.aid, session=web_session())

    form = ChangePasswordForm()
    if form.validate_on_submit():
        account = funcs.get_account(username=current_user.username, session=web_session())
        if account and check_password_hash(account.password, form.old_password.data):
            pw_hash = generate_password_hash(form.new_password.data)
            res = funcs.update_account(username=current_user.username, pw=pw_hash)
            flash('Пароль обновлён.' if res[0] else res[1])
        else:
            flash('Неправильный пароль.')

    return render_template('web/user.html', user=current_user, form=form, login_history=login_history)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(message='Вы уже авторизованы', category='auth')
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        account = funcs.get_account(username=form.login.data, session=web_session())
        if account and check_password_hash(account.password, form.password.data):
            user_obj = User(username=account.username, first_name=account.first_name,
                            last_name=account.last_name, aid=account.account_id)
            login_user(user_obj)
            funcs.log_account(aid=user_obj.aid, ip=str(request.remote_addr), session=web_session())
            res = funcs.clear_account_logs(aid=user_obj.aid, session=web_session())

            return redirect(url_for('main'))
        else:
            flash('Неправильный логин или пароль')

    return render_template('web/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash(message='Вы уже авторизованы', category='auth')
        return redirect(url_for('main'))
    form = RegForm()
    if form.validate_on_submit():
        pw_hash = generate_password_hash(form.password.data)
        avatar = Avatar((form.first_name.data, form.last_name.data), size=(256, 256))
        res = funcs.add_account(form.login.data, pw_hash, form.first_name.data, form.last_name.data,
                                session=web_session())
        if res[0]:
            funcs.add_account_avatar(aid=res[1], avatar=avatar.get_bytes().getvalue())
            flash('Вы успешно зарегистрировались!')
            return redirect(url_for('login'))
        flash(res[1])

    for key in form.errors:
        for error in form.errors[key]:
            flash(error)

    return render_template('web/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    flash(message='Вы вышли из системы', category='auth')
    logout_user()
    return redirect(url_for('login'))


print('Routes imported!')
