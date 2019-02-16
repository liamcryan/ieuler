from datetime import datetime
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, index=True, unique=True)
    problems = db.relationship('Problem', backref='solver', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}; id {self.id}>'


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    number = db.Column(db.Integer, index=True)
    name = db.Column(db.String, index=True)
    content = db.Column(db.String, nullable=False)
    codes = db.relationship('Code', backref='file', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Problem {self.name}; number {self.number}; id {self.id} user_id {self.user_id}>'


class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    language = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))

    def __repr__(self):
        return f'<Code {self.language}; id {self.id}; timestamp {self.timestamp}; problem_id {self.problem_id}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
