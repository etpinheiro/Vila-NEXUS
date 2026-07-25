import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vila-nexus-tropical-brutalism-barcarena-secret-key-2026'
    
    # Configuração de Banco de Dados
    # Para rodar com SQLite local (padrão de desenvolvimento/testes):
    #   SQLALCHEMY_DATABASE_URI = sqlite:///vila_nexus.db
    # Para migrar futuramente para SQL Server, defina a variável de ambiente DATABASE_URL:
    #   mssql+pyodbc://usuario:senha@servidor/vila_nexus_db?driver=ODBC+Driver+17+for+SQL+Server
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(BASE_DIR, 'vila_nexus.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit per upload request
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
    
    # Paged listing
    PROPERTIES_PER_PAGE = 9
