import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'bn_immo.db'}"
    ).replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"

    COMPANY_NAME = os.getenv("COMPANY_NAME", "B&N Immo-Invest Limited")
    COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "info@bnimmo-invest.com")
    COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+254 705 540 754")
    COMPANY_PHONE_ALT = os.getenv("COMPANY_PHONE_ALT", "+254 729 004 000")
    COMPANY_ADDRESS = os.getenv(
        "COMPANY_ADDRESS",
        "Off Mombasa Road, Green Square Godown, Behind Mastermind, Nairobi, Kenya",
    )

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@bnimmo-invest.com").lower()
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMeNow!2026")
