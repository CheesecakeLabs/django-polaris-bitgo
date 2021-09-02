import json
from typing import Optional

from polaris import settings as polaris_settings
from polaris.utils import get_account_obj
from stellar_sdk import Keypair
from stellar_sdk.account import Account
from stellar_sdk.transaction_envelope import TransactionEnvelope

from .api import BitGoAPI
from .dtos import Recipient, Wallet
from .utils import SJCL


class BitGo:
    def __init__(
        self,
        asset_code: str = "XLM",
        asset_issuer: Optional[str] = None,
        api_key: str = "",
        api_passphrase: str = "",
        wallet_id: str = "",
        api_url: str = "https://app.bitgo-test.com",
        stellar_coin_code: str = "txlm",
    ):
        self.bitgo_api = BitGoAPI(
            asset_code=asset_code,
            asset_issuer=asset_issuer,
            api_url=api_url,
            api_key=api_key,
            api_passphrase=api_passphrase,
            wallet_id=wallet_id,
            stellar_coin_code=stellar_coin_code,
        )
        self.asset_code = asset_code
        self.asset_issuer = asset_issuer

        wallet = self.bitgo_api.get_wallet()
        self.wallet = Wallet(
            public_key=wallet.get("coinSpecific", {}).get("rootAddress"),
            keys=wallet.get("keys", []),
        )

        self.wallet.encrypted_private_key = self.bitgo_api.get_wallet_key_info(
            self.wallet
        ).get("encryptedPrv")

    def build_transaction(self, recipient: Recipient) -> TransactionEnvelope:
        """
        Create a :class:`TransactionEnvelope` based on the "txBase64"
        field returned by BitGo's API build transaction.

        :param recipient: The :class:`Recipient` object with the
        amount (XDR Amount) and the destination address.
        :return: A new :class:`TransactionEnvelope` object.
        """
        response_data = self.bitgo_api.build_transaction(recipient)
        return TransactionEnvelope.from_xdr(
            response_data["txBase64"],
            polaris_settings.STELLAR_NETWORK_PASSPHRASE,
        )

    def sign_transaction(
        self, transaction_envelope: TransactionEnvelope
    ) -> TransactionEnvelope:
        """
        Adds the Anchor's BitGo wallet signature for the given TransactionEnvelope.

        :param transaction_envelope: The TransactionEnvelope that is
        going to be signed by the Anchor's BitGo wallet.
        :return: Returns the received TransactionEnvelope signed.
        """
        keypair = Keypair.from_secret(self.get_private_key())
        transaction_envelope.sign(keypair)

        return transaction_envelope

    def send_transaction(self, transaction_envelope_xdr: str) -> dict:
        """
        Sends the transaction's XDR to BitGo, which adds another
        signature to the transaction, then sends it to the
        Stellar Network.

        :param transaction_envelope_xdr: The base64 string with
        the transaction's information.
        :return: Returns the BitGo's API response. It contains
        some information about the transaction, like the Stellar
        Network transaction id.
        """
        return self.bitgo_api.send_transaction(transaction_envelope_xdr)

    def _decrypt_private_key(self) -> str:
        """
        Decrypt the signer encrypted private key.

        The BitGo's Keys List API returns a list of the wallet's
        encrypted keys. This API returns the keys in the SJCL format
        and encrypts using the AES algorithm with CCM mode, using
        the wallet passcode as the key.

        :return: Returns the wallet's private key.
        """
        return SJCL().decrypt(
            json.loads(self.wallet.encrypted_private_key),
            self.bitgo_api.API_PASSPHRASE,
        )

    def get_source_account(self) -> Account:
        """
        Retrieves an :class:`Account` object with the "source account"
        for the given Anchor's BitGo wallet public key.

        :return: Returns a :class:`Account` object.
        """
        source_account, _ = get_account_obj(
            Keypair.from_public_key(self.get_public_key())
        )
        return source_account

    def get_public_key(self) -> str:
        """
        Returns the wallet's public key. This public key hash is from the account
        that has the supplies.

        :return: Returns the public key hash.
        """
        return self.wallet.public_key

    def get_private_key(self) -> str:
        """
        Returns the private key from a signer, in this case, the user key.
        It doesn't return the private key from the account that has the
        supplies.

        :return: Returns the signer private key hash.
        """
        return self._decrypt_private_key()
