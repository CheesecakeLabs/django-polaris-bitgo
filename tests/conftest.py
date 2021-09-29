import django
from stellar_sdk import Keypair


def pytest_configure(config):
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        SECRET_KEY="not very secret in tests",
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ),
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "polaris",
        ),
    )

    # Polaris settings
    settings.POLARIS_ACTIVE_SEPS = ["sep-1", "sep-10", "sep-24"]
    settings.POLARIS_SIGNING_SEED = Keypair.random().secret
    settings.POLARIS_SERVER_JWT_KEY = "arandomkeythatissecret"
    settings.POLARIS_HOST_URL = "https://example.com/"
    settings.SESSION_COOKIE_SECURE = True

    # BitGo specific
    settings.BITGO_API_URL = "https://api.bitgo-test.com"
    settings.BITGO_API_KEY = "myapikey"
    settings.BITGO_API_PASSPHRASE = "mypassphrase"
    settings.BITGO_WALLET_ID = "walletid"
    settings.BITGO_STELLAR_COIN_CODE = "txlm"

    django.setup()
