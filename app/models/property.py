from datetime import datetime
from app import db

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.String(30), nullable=False, default='Venda')  # Venda, Aluguel, Temporada, Hospedagem
    property_type = db.Column(db.String(50), nullable=False, default='Casa')  # Casa, Apartamento, Terreno, Pousada/Quarto, Hotel/Suíte, Galpão/Comercial, Sítio/Chácara
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    neighborhood = db.Column(db.String(100), nullable=False, default='Vila dos Cabanos')
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    bedrooms = db.Column(db.Integer, default=0)
    bathrooms = db.Column(db.Integer, default=0)
    suites = db.Column(db.Integer, default=0)
    parking_spaces = db.Column(db.Integer, default=0)
    area_sqm = db.Column(db.Float, default=0.0)
    features = db.Column(db.Text, nullable=True)  # Comma-separated or JSON tags: Piscina, Garagem, Ar Condicionado...
    
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    status = db.Column(db.String(30), nullable=False, default='disponivel')  # disponivel, vendido, alugado, reservado
    is_highlighted = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to images
    images = db.relationship('PropertyImage', backref='property', lazy='joined', cascade='all, delete-orphan', order_by='PropertyImage.order')

    def primary_image_url(self):
        if self.images:
            primary = next((img for img in self.images if img.is_primary), self.images[0])
            return primary.get_url()
        return '/static/images/property_placeholder.svg'

    def get_features_list(self):
        if not self.features:
            return []
        return [f.strip() for f in self.features.split(',') if f.strip()]

    def formatted_price(self):
        return f"R$ {self.price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def __repr__(self):
        return f'<Property {self.title} (R$ {self.price})>'


class PropertyImage(db.Model):
    __tablename__ = 'property_images'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_url(self):
        if self.filename.startswith('http://') or self.filename.startswith('https://'):
            return self.filename
        if self.filename == 'property_placeholder.svg':
            return '/static/images/property_placeholder.svg'
        return f'/static/uploads/{self.filename}'

    def __repr__(self):
        return f'<PropertyImage {self.filename} (Property ID: {self.property_id})>'
