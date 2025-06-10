import os

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DUCKFY_BASE_URL = "https://app.duckfyoficial.com/api/v1"
    PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
    DUCKFY_SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configurações de produção
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    FLASK_ENV = 'production'
    # Configurações de segurança para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
