# import secrets
from pydantic_settings import SettingsConfigDict,  BaseSettings

class Settings(BaseSettings):

    DATABASE_URL: str

    DATABASE_URL_SYNC:str 


    #configuration de redis

    redis_url: str

    # JWT

    JWT_private_key: str 
    
    JWT_SECRET_KEY: str 
    
    
    
    


    """en developpement vous pouvez toujours importer le module secrets
    si vous n'avez pas configuré un .env.test
    vous passez ensuite cette expression
    """
    # jwt_secret_key: str = secrets.token_urlsafe(64)

    """secrets.token_urlsafe(64) génère une chaine aléatoire cryptographiquement sûre de
    64 bytes encodés en base64 URL-safe (environ 86 caractères)
    
    le problème c'est que cette valeur change à chaque redemerrage s'il elle n'est pas
    fixée en variable d'environnement 3
    """

    jwt_algorithm: str = "RS256"

    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire: int = 7


    #API KEYS

    api_key_prefix: str = 'sk_live_'
    api_key_key_length: int = 32

    #Rate limiting

    login_max_attempts: int = 5
    login_lockout_minutes: int = 15


    #cache session redis

    session_cache_tll_seconds: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra = 'ignore'
    )

settings = Settings()