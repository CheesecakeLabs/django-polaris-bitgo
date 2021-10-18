import django
import pytest
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
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            },
        },
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


@pytest.fixture
def make_bitgo_api():
    from django.conf import settings

    from polaris_bitgo.bitgo.api import BitGoAPI

    def _make_bitgo_api(
        asset_code: str = "BST",
        asset_issuer: str = "GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    ) -> BitGoAPI:
        return BitGoAPI(
            asset_code=asset_code,
            asset_issuer=asset_issuer,
            api_url=settings.BITGO_API_URL,
            api_key=settings.BITGO_API_KEY,
            api_passphrase=settings.BITGO_API_PASSPHRASE,
            wallet_id=settings.BITGO_WALLET_ID,
            stellar_coin_code=settings.BITGO_STELLAR_COIN_CODE,
        )

    return _make_bitgo_api


@pytest.fixture
def make_bitgo():
    from django.conf import settings

    from polaris_bitgo.bitgo import BitGo

    def _make_bitgo(
        asset_code: str = "BST",
        asset_issuer: str = "GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    ) -> BitGo:
        return BitGo(
            asset_code=asset_code,
            asset_issuer=asset_issuer,
            api_url=settings.BITGO_API_URL,
            api_key=settings.BITGO_API_KEY,
            api_passphrase=settings.BITGO_API_PASSPHRASE,
            wallet_id=settings.BITGO_WALLET_ID,
            stellar_coin_code=settings.BITGO_STELLAR_COIN_CODE,
        )

    return _make_bitgo


@pytest.fixture
def make_bitgo_integration():
    from django.conf import settings

    from polaris_bitgo.bitgo.integration import BitGoIntegration

    return BitGoIntegration(
        api_url=settings.BITGO_API_URL,
        api_key=settings.BITGO_API_KEY,
        api_passphrase=settings.BITGO_API_PASSPHRASE,
        wallet_id=settings.BITGO_WALLET_ID,
        stellar_coin_code=settings.BITGO_STELLAR_COIN_CODE,
    )


@pytest.fixture
def make_recipient():
    from polaris_bitgo.bitgo.dtos import Recipient

    def _make_recipient(
        amount: str = "10000",
        address: str = "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3",
    ) -> Recipient:
        return Recipient(
            amount=amount,
            address=address,
        )

    return _make_recipient


@pytest.fixture
def make_wallet():
    from polaris_bitgo.bitgo.dtos import Wallet

    def _make_wallet(
        public_key: str,
        keys: list,
    ) -> Wallet:
        return Wallet(
            public_key=public_key,
            keys=keys,
        )

    return _make_wallet
