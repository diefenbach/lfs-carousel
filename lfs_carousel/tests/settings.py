"""Settings for the add-on's tests: LFS with its required apps and lfs_carousel, without a theme, so the add-on's
own templates are used."""

from lfs.settings import LFS_APPS

SECRET_KEY = "test-only"
ALLOWED_HOSTS = ["testserver"]
SITE_ID = 1
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
INSTALLED_APPS = [*LFS_APPS, "lfs_carousel"]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "lfs_carousel.tests.urls"
STATIC_URL = "static/"
STATIC_ROOT = "/tmp/lfs-carousel-tests/static"
MEDIA_ROOT = "/tmp/lfs-carousel-tests/media"
STATICFILES_FINDERS = ["django.contrib.staticfiles.finders.AppDirectoriesFinder", "compressor.finders.CompressorFinder"]
COMPRESS_ENABLED = False
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "lfs.core.context_processors.main",
            ]
        },
    }
]
USE_TZ = True
LANGUAGE_CODE = "en"
SESSION_SERIALIZER = "lfs.core.pickle_serializer.PickleSerializer"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
REVIEWS_IS_MODERATED = False
LOGIN_URL = "/login/"
