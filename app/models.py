from datetime import datetime
from flask_login import UserMixin
from app import db, login


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    number = db.Column(db.Integer, index=True)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Problem {self.number}; name {self.name}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, index=True, unique=True)
    scratchpads = db.relationship('Scratchpad', backref='solver', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}; id {self.id}>'


class Scratchpad(db.Model):
    __tablename__ = 'scratchpad'
    id = db.Column(db.Integer, primary_key=True)

    language = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship('Problem')

    def __repr__(self):
        return f'<Scratchpad {self.language}; timestamp {self.timestamp}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
