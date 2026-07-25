from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # admin, entrepreneur, client
    status = db.Column(db.String(20), nullable=False, default='active')  # active, blocked
    phone = db.Column(db.String(30), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Favorite, VisitRequest, SavedSearch
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    visit_requests = db.relationship('VisitRequest', backref='user', lazy='dynamic')
    saved_searches = db.relationship('SavedSearch', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_entrepreneur(self):
        return self.role == 'entrepreneur'

    def is_client(self):
        return self.role == 'client'

    def is_active_user(self):
        return self.status == 'active'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
