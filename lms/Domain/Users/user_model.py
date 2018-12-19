from lms.app import db
from uuid import uuid4 as uid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from lms.Domain.Teachers import Teacher
from lms.Domain.Students import Student

class User(UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    registration_uid = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    second_name = db.Column(db.String(64))
    # expects a class
    student = db.relationship('Student', backref='user', uselist=False)
    teacher = db.relationship('Teacher', backref='user', uselist=False)

    def __repr__(self):
        return '<User {username}, {name} {second_name} {surname}>'.format(username=self.username, name=self.name, second_name=self.second_name,
                                                                          surname=self.surname)
    def get_data(self):
        return 'Логин: {username}, ' \
               'Email: {email}, ' \
               'ФИО: {surname} {name} {second_name}'.format(username=self.username,
                                                email=self.email, name=self.name,
                                                second_name=self.second_name, surname=self.surname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_uid():
        return str(uid())
