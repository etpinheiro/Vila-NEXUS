from datetime import datetime
from app import db

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    cnpj_cpf = db.Column(db.String(30), nullable=True)
    business_type = db.Column(db.String(50), nullable=False, default='Imobiliária')  # Imobiliária, Hotel, Pousada, Proprietário Particular, Outro
    phone = db.Column(db.String(30), nullable=False)
    whatsapp = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    neighborhood = db.Column(db.String(100), nullable=False, default='Vila dos Cabanos')
    description = db.Column(db.Text, nullable=True)
    logo_filename = db.Column(db.String(255), nullable=True)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='company', lazy='dynamic')
    properties = db.relationship('Property', backref='company', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'


class CompanyRegistrationRequest(db.Model):
    __tablename__ = 'company_registration_requests'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(120), nullable=False)
    cnpj_cpf = db.Column(db.String(30), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    whatsapp = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, contacted, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CompanyRegistrationRequest {self.company_name} - {self.status}>'
