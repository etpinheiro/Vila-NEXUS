"""
Script executado pelo Render no Build Command para criar as tabelas no Supabase.
Rode localmente também para inicializar o SQLite: python init_db.py
"""
import os
from app import create_app, db
from app.models.user import User                                          # noqa: F401
from app.models.company import Company, CompanyRegistrationRequest        # noqa: F401
from app.models.property import Property, PropertyImage                   # noqa: F401
from app.models.client_interactions import Favorite, VisitRequest, SavedSearch  # noqa: F401

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas (ou já existentes) com sucesso.")
    print(f"   Banco: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI']}")
