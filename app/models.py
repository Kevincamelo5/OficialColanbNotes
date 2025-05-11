from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

user_foro = db.Table(
    'user_foro',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('foro_id', db.Integer, db.ForeignKey('foro.id'), primary_key=True)
)

user_contacts = db.Table(
    'user_contacts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    notes = db.relationship('Note', backref='author', lazy=True)

    foros = db.relationship('Foro', secondary=user_foro, backref=db.backref('user_participants', lazy='dynamic'), lazy='dynamic')

     # Relaciones para solicitudes de amistad
    sent_friend_requests = db.relationship(
        'FriendRequest',
        foreign_keys='FriendRequest.sender_id',
        back_populates='sender',
        lazy=True
    )
    received_friend_requests = db.relationship(
        'FriendRequest',
        foreign_keys='FriendRequest.receiver_id',
        back_populates='receiver',
        lazy=True
    )

    contacts = db.relationship(
    'User', 
    secondary=user_contacts, 
    primaryjoin=(user_contacts.c.user_id == id), 
    secondaryjoin=(user_contacts.c.contact_id == id), 
    backref=db.backref('friends', lazy='dynamic'), 
    lazy='dynamic'
)
    
    # Relaciones para mensajes privados
    sent_messages = db.relationship(
        'PrivateMessage',
        foreign_keys='PrivateMessage.sender_id',
        backref='sender_user',
        lazy=True
    )
    received_messages = db.relationship(
        'PrivateMessage',
        foreign_keys='PrivateMessage.receiver_id',
        backref='receiver_user',
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Foro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    participants = db.relationship('User', secondary=user_foro, backref=db.backref('forum_foros', lazy='dynamic'), lazy='dynamic')

    messages = db.relationship('Message', backref='foro', lazy=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    foro_id = db.Column(db.Integer, db.ForeignKey('foro.id'), nullable=False)

    user = db.relationship('User', backref='messages')

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'

    # Relaciones inversas
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_friend_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_friend_requests')

class PrivateMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Marca de tiempo del mensaje

     # Relaciones inversas
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_private_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_private_messages')