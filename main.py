import json
import os
import datetime
import copy

from flask import Flask, url_for, request, render_template, redirect
from flask import jsonify, session, make_response

from flask_sqlalchemy import SQLAlchemy

from flask_restful import reqparse, abort, Api, Resource

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
        return '<LibraryUser {} {}>'.format(
            self.id, self.username)


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

parser_user = reqparse.RequestParser()
parser_user.add_argument('username', required=True)
parser_user.add_argument('email', required=True)
parser_user.add_argument('about_me', required=False)

parser_book = reqparse.RequestParser()
parser_book.add_argument('name', required=True)
parser_book.add_argument('link', required=True)
parser_book.add_argument('genre', required=True)
parser_book.add_argument('review', required=False)


def abort_if_book_not_found(book_id):
    if BookModel.query.filter_by(id=book_id).first() is None:
        abort(404, message="Book {} not found".format(book_id))


class Books(Resource):
    def get(self, book_id):
        abort_if_book_not_found(book_id)
        book = BookModel.query.filter_by(id=book_id).first()
        return jsonify({'book': book})

    def delete(self, book_id):
        abort_if_book_not_found(book_id)
        book = BookModel.query.filter_by(id=book_id).first()

        db.session.delete(book)
        db.session.commit()

        return jsonify({'success': 'OK'})

    def put(self, book_id):
        abort_if_book_not_found(book_id)
        args = parser_book.parse_args()
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

        return jsonify({'books': books})

    def post(self):
        args = parser_book.parse_args()

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
    return


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
