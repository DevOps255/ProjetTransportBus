# import secrets
from pydantic_settings import SettingsConfigDict,  BaseSettings
from typing import List

class Settings(BaseSettings):

    DATABASE_URL: str = "sqlite+aiosqlite:///./films.db"

    DATABASE_URL_SYNC: str = "sqlite:///./contacts.db"

    # configuration de redis

    redis_url: str = "redis://redis:6379"
    # JWT
    
    JWT_SECRET_KEY: str ="je suis "
    
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

    jwt_algorithm: str = "HS256"

    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire: int = 7


    #API KEYS

    api_key_prefix: str = 'sk_live_'
    api_key_key_length: int = 32

    #Rate limiting

    login_max_attempts: int = 5
    login_lockout_minutes: int = 15
    
    #Gemini projects
    
    gemini_project_a: str =" "
    gemini_project_b: str =" "
    gemini_project_c: str=" "
    
    #Gemini keys
    
    gemini_key_a: str = ""
    gemini_key_b: str = ""
    gemini_key_c: str = ""
    
    # Mistral API key
    Mistral_key: str = ""
    Mistral_model: str = "mistral-small-latest"
    
    #cache session redis

    session_cache_tll_seconds: int = 300
    
    #Indempotence
    
    webhook_max_age_seconds: int = 300    
    idempotency_ttl_seconds: int = 600
    
    #ticket de bus 
    
    ticket_price: int = 150    
    ticket_price_minor_units: int = 15_000
    
    # Recharge minimum   
    
    minimum_recharge: int = 100    
    minimum_recharge_minor_units: int = 10_000
    
    # Gestion du TOTP (Time-based One-Time Password)
    totp_step_seconds: int = 30
    totp_valid_window: int = 5
    totp_max_trip_duration_minutes: int = 120
    
    # anti-replay    
    totp_replay_ttl_seconds: int = 3600
    
    #Circuit breaker 
    circuit_breaker_max_failures: int = 5    
    circuit_breaker_window_seconds: int = 900
    
    # Circuit breaker des  recharges    
     
    wallet_circuit_breaker_max_failures: int = 5    
    wallet_circuit_breaker_window_seconds: int = 900
    
    allowed_sms_beneficiaries: List[str] = [
        ""
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra = 'ignore'
    )
    
settings = Settings()