import os
from app import create_app, db

app = create_app()  # db.create_all() já é chamado dentro de create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==================================================================")
    print(f" Servidor Vila Nexus iniciado com sucesso!")
    print(f" Acesse a plataforma no seu navegador em: http://127.0.0.1:{port}")
    print(f"==================================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
