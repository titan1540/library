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


@app.route('/')
def index():
    return


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=False)
