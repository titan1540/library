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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class LibraryReader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    about_me = db.Column(db.String(300), unique=False, nullable=True)

    def __repr__(self):
        return '<LibraryReader {} {}>'.format(
            self.id, self.username)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    review = db.Column(db.Text(), unique=False, nullable=True)
    link = db.Column(db.String(128), unique=True, nullable=False)
    genre = db.Column(db.String(50), unique=False, nullable=False)
    reader_id = db.Column(db.Integer,
                          db.ForeignKey('library_reader.id'),
                          nullable=False)
    reader = db.relationship('LibraryReader',
                             backref=db.backref('Book',
                                                lazy=True))

    def __repr__(self):
        return '<Book {} {} {}>'.format(
            self.id, self.name, self.genre)


db.create_all()


@app.route('/')
def index():
    return


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=False)
