import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def _get_database_url():
    """
    Resolve a URL do banco de dados:
    - Em produção (Render): lê DATABASE_URL do ambiente.
      O Supabase fornece URLs no formato 'postgres://...', que o SQLAlchemy
      exige como 'postgresql://...', então fazemos a correção automática.
    - Em desenvolvimento local: usa SQLite.
    """
    url = os.environ.get('DATABASE_URL')
    if url:
        # Supabase/Heroku exportam 'postgres://' mas SQLAlchemy >= 1.4 exige 'postgresql://'
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    # Fallback local: SQLite para testes no PC
    return f"sqlite:///{os.path.join(BASE_DIR, 'vila_nexus.db')}"

def _get_engine_options():
    """
    Opções de engine específicas por banco.
    PostgreSQL precisa de pool_pre_ping para reconectar após idle timeout do Supabase.
    SQLite não suporta pool_pre_ping da mesma forma.
    """
    url = os.environ.get('DATABASE_URL', '')
    if url:
        return {
            'pool_pre_ping': True,       # Reconecta automaticamente após idle timeout
            'pool_recycle': 300,         # Recicla conexões a cada 5 minutos
        }
    return {}  # SQLite: sem configurações extras de pool

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vila-nexus-tropical-brutalism-barcarena-secret-key-2026'

    # Banco de dados: PostgreSQL (Supabase) em produção, SQLite localmente
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _get_engine_options()

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit per upload request
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # Paged listing
    PROPERTIES_PER_PAGE = 9
