"""
Cria o usuário administrador lendo as credenciais de variáveis de ambiente.
Seguro para rodar a cada deploy: ignora se o email já existir.

Configure no Render (Environment Variables):
  ADMIN_NAME     → seu nome completo
  ADMIN_EMAIL    → seu email de login
  ADMIN_PASSWORD → sua senha
  ADMIN_PHONE    → seu telefone (opcional)
"""
import os
import sys
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    name     = os.environ.get('ADMIN_NAME', 'Administrador')
    email    = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')
    phone    = os.environ.get('ADMIN_PHONE', '')

    if not email or not password:
        print("❌ ADMIN_EMAIL e ADMIN_PASSWORD são obrigatórios. Configure as variáveis de ambiente no Render.")
        sys.exit(1)

    if User.query.filter_by(email=email).first():
        print(f"✅ Admin '{email}' já existe. Nenhuma ação necessária.")
        sys.exit(0)

    admin = User(
        name=name,
        email=email,
        phone=phone,
        role='admin',
        status='active'
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"✅ Admin criado com sucesso: {email}")
