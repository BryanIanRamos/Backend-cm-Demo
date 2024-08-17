from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Date(db.Model):
    __tablename__ = 'date_created_tbl'

    date_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True) 

    def __repr__(self):
        return f'<Date {self.date_id}>'
    
class Accounts(db.Model):
    __tablename__ = 'accounts_tbl'

    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    date_id = db.Column(db.Integer, db.ForeignKey('date_created_tbl.date_id'), nullable=False)

    # Define the relationship to the Date model
    date_time = db.relationship('Date', backref=db.backref('accounts', lazy=True))

    def __repr__(self):
        return f'<Accounts {self.username}>'
    
class Posts(db.Model):
    __tablename__ = 'posts_tbl'

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=True)
    date_id = db.Column(db.Integer, db.ForeignKey('date_created_tbl.date_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts_tbl.account_id'), nullable=False)

    # Define the relationship to the Date model
    date_time = db.relationship('Date', backref=db.backref('posts', lazy=True))
    creator = db.relationship('Accounts', backref=db.backref('posts', lazy=True))

    def __repr__(self):
        return f'<Posts {self.post_id}>'
    
class PostsData(db.Model):
    __tablename__ = 'posts_data_tbl'

    data_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data  = db.Column(db.LargeBinary, nullable=True)
    date_id = db.Column(db.Integer, db.ForeignKey('date_created_tbl.date_id'), nullable=False)
    
    # Define the relationship to the Date model
    date_time = db.relationship('Date', backref=db.backref('postsData', lazy=True))

    def __repr__(self):
        return f'<PostsData {self.data_id}>'




