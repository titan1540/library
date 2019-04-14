from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirm = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Почта', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class AddBookForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    link = StringField('Ссылка на книгу', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    review = TextAreaField('Отзыв о книге')
    submit = SubmitField('Добавить')


class EditBookForm(FlaskForm):
    name = StringField('Название книги', validators=[DataRequired()])
    link = StringField('Ссылка на книгу', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    review = TextAreaField('Отзыв о книге')
    submit = SubmitField('Изменить')
