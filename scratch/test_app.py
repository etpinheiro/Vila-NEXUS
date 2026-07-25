import sys, os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import User, Company, CompanyRegistrationRequest, Property

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

with app.app_context():
    client = app.test_client()
    
    # 1. Test Homepage
    res = client.get('/')
    assert res.status_code == 200, f"Index failed: {res.status_code}"
    print("[OK] Rota '/' (Homepage) OK [200]")

    # 2. Test Properties Catalog
    res = client.get('/imoveis')
    assert res.status_code == 200, f"Properties list failed: {res.status_code}"
    print("[OK] Rota '/imoveis' (Catalogo) OK [200]")

    # 3. Test Commercial Lead Request Form
    res = client.get('/solicitar-cadastro')
    assert res.status_code == 200, f"Request company form failed: {res.status_code}"
    print("[OK] Rota '/solicitar-cadastro' (Formulario do Empresario) OK [200]")

    # 4. Test Property Detail Page
    p = Property.query.first()
    res = client.get(f'/imovel/{p.id}')
    assert res.status_code == 200, f"Property detail failed: {res.status_code}"
    print(f"[OK] Rota '/imovel/{p.id}' (Detalhes do Imovel) OK [200]")

    # 5. Test Login Page
    res = client.get('/auth/login')
    assert res.status_code == 200, f"Login failed: {res.status_code}"
    print("[OK] Rota '/auth/login' OK [200]")

    # 6. Test Admin POST Login & Accessing Admin Routes
    res = client.post('/auth/login', data={
        'email': 'admin@vilanexus.com.br',
        'password': 'admin123'
    }, follow_redirects=True)
    assert res.status_code == 200, f"Admin login failed: {res.status_code}"
    print("[OK] Login do Administrador bem-sucedido [200]")

    res = client.get('/admin/dashboard')
    assert res.status_code == 200, f"Admin dashboard failed: {res.status_code}"
    print("[OK] Rota '/admin/dashboard' (Painel do Administrador) OK [200]")

    res = client.get('/admin/solicitacoes')
    assert res.status_code == 200, f"Admin company requests failed: {res.status_code}"
    print("[OK] Rota '/admin/solicitacoes' (Leads de Empresarios) OK [200]")

    # 7. Test Entrepreneur Login & Accessing Entrepreneur Routes
    client = app.test_client()
    res = client.post('/auth/login', data={
        'email': 'carlos@cabanosprime.com.br',
        'password': 'empresa123'
    }, follow_redirects=True)
    assert res.status_code == 200, f"Entrepreneur login failed: {res.status_code}"
    print("[OK] Login do Empresario bem-sucedido [200]")

    res = client.get('/empresario/dashboard')
    assert res.status_code == 200, f"Entrepreneur dashboard failed: {res.status_code}"
    print("[OK] Rota '/empresario/dashboard' (Painel do Empresario) OK [200]")

    print("\n==================================================")
    print(" TODAS AS ROTAS E AUTENTICACAO FUNCIONAM 100%!")
    print("==================================================")
