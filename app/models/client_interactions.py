from datetime import datetime
from app import db

class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint per user and property
    __table_args__ = (
        db.UniqueConstraint('user_id', 'property_id', name='_user_property_uc'),
    )

    property = db.relationship('Property', backref=db.backref('favorited_by', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Favorite User:{self.user_id} Prop:{self.property_id}>'


class VisitRequest(db.Model):
    __tablename__ = 'visit_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    client_name = db.Column(db.String(120), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(30), nullable=False)
    preferred_date = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    property = db.relationship('Property', backref=db.backref('visit_requests', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<VisitRequest {self.client_name} - Prop:{self.property_id}>'


class SavedSearch(db.Model):
    __tablename__ = 'saved_searches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    filters_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedSearch {self.title} User:{self.user_id}>'
