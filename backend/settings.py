"""
Django settings for backend project.
"""
from pathlib import Path
import environ, os

# ---------------------
# BASE DIR & ENV
# ---------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ---------------------
# 기본 설정
# ---------------------
SECRET_KEY = env("SECRET_KEY", default="dev-secret")

DEBUG = True
ALLOWED_HOSTS = ["*"]

# ---------------------
# APP 설정
# ---------------------
INSTALLED_APPS = [
    # Django 기본 앱
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_yasg",

    # Local Apps
    "accounts",
    "wellness",
    "usage",
]

# ---------------------
# Middleware
# ---------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # ✅ 반드시 최상단 부근에 추가
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True  # 개발 중만 허용

# ---------------------
# URL & WSGI
# ---------------------
ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# ---------------------
# DATABASE
# ---------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------
# PASSWORD VALIDATION (기본 유지)
# ---------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------
# 언어 / 시간 설정
# ---------------------
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

# ---------------------
# STATIC
# ---------------------
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------
# ✅ Custom User Model
# ---------------------
AUTH_USER_MODEL = "accounts.User"

# ---------------------
# ✅ DRF + JWT 설정
# ---------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
