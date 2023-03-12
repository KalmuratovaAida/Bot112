from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    login = StringField('Логин: ', validators=[DataRequired()])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=8, max=32)])
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    first_name = StringField('Имя: ', validators=[DataRequired()])
    last_name = StringField('Фамилия: ', validators=[DataRequired()])
    login = StringField('Логин: ', validators=[DataRequired(), Length(min=4, max=16)])
    password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=8, max=32)])
    confirm_password = PasswordField('Повтор пароля: ',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Пароли должны совпадать!')])
    submit = SubmitField('Зарегистрироваться')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль: ', validators=[DataRequired(), Length(min=8, max=32)])
    new_password = PasswordField('Новый пароль: ', validators=[DataRequired(), Length(min=8, max=32)])
    confirm_password = PasswordField('Повтор пароля: ',
                                     validators=[DataRequired(),
                                                 EqualTo('new_password', message='Пароли должны совпадать!')])
    submit = SubmitField('Сохранить')
