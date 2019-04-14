import json
import os
import datetime
import copy

from flask import Flask, url_for, request, render_template, redirect
from flask import jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.security import generate_password_hash, check_password_hash

from form import RegistrationForm, LoginForm, AddBookForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class LibraryUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    about_me = db.Column(db.String(300), unique=False, nullable=True)

    def __repr__(self):
        return '<LibraryUser {} {} {}>'.format(
            self.id, self.username, self.email)


class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    link = db.Column(db.String(128), unique=True, nullable=False)
    genre = db.Column(db.String(50), unique=False, nullable=False)
    review = db.Column(db.Text(), unique=False, nullable=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('library_user.id'),
                        nullable=False)
    user = db.relationship('LibraryUser',
                           backref=db.backref('BookModel',
                                              lazy=True))

    def __repr__(self):
        return '<Book {} {} {}>'.format(
            self.id, self.name, self.genre)


db.create_all()

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('link', required=True)
parser.add_argument('genre', required=True)
parser.add_argument('review', required=False)


def abort_if_book_not_found(book_id):
    if BookModel.query.filter_by(id=book_id).first() is None:
        abort(404, message="Book {} not found".format(book_id))


class Book(Resource):
    def get(self, book_id):
        abort_if_book_not_found(book_id)
        book = BookModel.query.filter_by(id=book_id).first()
        return jsonify({'book': {'id': book.id,
                                 'genre': book.genre,
                                 'name': book.name,
                                 'link': book.link,
                                 'review': book.review}})

    def delete(self, book_id):
        abort_if_book_not_found(book_id)
        book = BookModel.query.filter_by(id=book_id).first()

        db.session.delete(book)
        db.session.commit()

        return jsonify({'success': 'OK'})

    def put(self, book_id):
        abort_if_book_not_found(book_id)
        args = parser.parse_args()
        book = BookModel.query.filter_by(id=book_id).first()

        book.name = args['name']
        book.link = args['link']
        book.genre = args['genre']
        book.review = args['review']

        db.session.add(book)
        db.session.commit()

        return jsonify({'success': 'OK'})


class BooksList(Resource):
    def get(self):
        books = BookModel.query.all()

        books_list = [{'id': book.id,
                       'genre': book.genre,
                       'name': book.name,
                       'link': book.link,
                       'review': book.review}
                      for book in books]

        return jsonify({'books': books_list})

    def post(self):
        args = parser.parse_args()

        user = LibraryUser.query.filter_by(id=session['user_id']).first()
        book = BookModel(name=args['name'],
                         link=args['link'],
                         genre=args['genre'],
                         review=args['review'])

        user.BookModel.append(book)
        db.session.commit()

        return jsonify({'success': 'OK'})


@app.route('/')
def index():
    bl = BooksList()
    books = json.loads(bl.get().data)

    return render_template('index.html', session=session,
                           books=books)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        password_confirm = form.password_confirm.data
        email = form.email.data

        if password == password_confirm and \
                LibraryUser.query.filter_by(username=username).first() is None:
            user = LibraryUser(username=username,
                               password_hash=generate_password_hash(password),
                               email=email)

            db.session.add(user)
            db.session.commit()

            session['username'] = username
            session['user_id'] = user.id

            return redirect('/')
    return render_template('registration.html', session=session, form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = LibraryUser.query.filter_by(username=username).first()

        if user is not None:
            if check_password_hash(user.password_hash, password):
                session['username'] = username
                session['user_id'] = user.id
                return redirect('/')
    return render_template('login.html', session=session, form=form)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        return redirect('/')
    form = AddBookForm()
    if form.validate_on_submit():
        name = form.name.data
        link = form.link.data
        genre = form.genre.data
        review = form.review.data
        book = BookModel(name=name,
                         link=link,
                         genre=genre,
                         review=review)
        user = LibraryUser.query.filter_by(id=session['user_id']).first()
        user.BookModel.append(book)
        db.session.commit()
        return redirect('/')
    return render_template('add_book.html', session=session, form=form)


@app.route('/book/<int:book_id>')
def book(book_id):
    b = Book()
    book = json.loads(b.get(book_id).data)
    return render_template('book.html', book=book['book'], session=session)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
