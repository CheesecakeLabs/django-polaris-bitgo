from time import sleep
from decimal import Decimal
from typing import Union

from polaris import settings as polaris_settings
from polaris.integrations import CustodyIntegration
from polaris.models import Asset, Transaction
from polaris.utils import get_logger
from rest_framework.request import Request
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.operation import Operation

from . import BitGo
from .bitgo import Recipient
from polaris_bitgo.helpers.exceptions import BitGoAPIError
from polaris_bitgo.utils import get_stellar_network_transaction_info

logger = get_logger(__name__)


class BitGoIntegration(CustodyIntegration):
    def __init__(
        self,
        api_key: str = "",
        api_passphrase: str = "",
        wallet_id: str = "",
        api_url: str = "https://app.bitgo-test.com",
        stellar_coin_code: str = "txlm",
    ):

        assert api_key, "The API Key is required."
        assert api_passphrase, "The API Passphrase is required."
        assert wallet_id, "The Wallet ID is required."

        super().__init__()

        self.api_key = api_key
        self.api_passphrase = api_passphrase
        self.wallet_id = wallet_id
        self.api_url = api_url
        self.stellar_coin_code = stellar_coin_code

    def get_distribution_account(self, asset: Asset) -> str:
        """
        Return the Stellar account used to receive payments of `asset`. This
        method is a replacement for the ``Asset.distribution_account`` property
        which is derived from the ``Asset.distribution_seed`` database column.

        :param asset: the asset sent in payments to the returned Stellar account
        """
        bitgo = self._create_integration_from_asset(asset)

        return bitgo.get_public_key()

    def save_receiving_account_and_memo(
        self, request: Request, transaction: Transaction
    ):
        pass

    def create_destination_account(self, transaction: Transaction) -> dict:
        """
        Creates the destination account of the transaction.
        All Stellar's accounts only exist after receiving an
        amount of XLM on its balance.
        Read more at: https://developers.stellar.org/docs/glossary/accounts/#account-creation

        :param public_key: The destination account public key.
        :returns: Returns a tuple with the :class:`Account` object based on
        the destination account's public key and a `True` value.
        """
        recipient = self._create_recipient(
            address=transaction.to_address,
            amount=polaris_settings.ACCOUNT_STARTING_BALANCE,
        )

        bitgo = self._create_integration_from_asset(Asset(code="XLM", issuer=None))

        envelope = bitgo.build_transaction(recipient)
        signed_envelope = bitgo.sign_transaction(envelope)

        response = bitgo.send_transaction(signed_envelope.to_xdr())

        if not response:
            raise BitGoAPIError("Error in BitGo send transaction")

        return self._poll_stellar_transaction_information(txid=response["txid"])

    def submit_deposit_transaction(
        self, transaction: Transaction, has_trustline: bool = True
    ) -> dict:
        """
        Sends the transaction to BitGo.

        :param transaction: The transaction model instance
        :returns: Returns the transaction's information at Stellar
        Network.
        """
        bitgo = self._create_integration_from_asset(transaction.asset)

        amount = round(
            Decimal(transaction.amount_in) - Decimal(transaction.amount_fee),
            transaction.asset.significant_decimals,
        )

        recipient = self._create_recipient(
            address=transaction.to_address,
            amount=amount,
        )

        envelope = bitgo.build_transaction(recipient)
        signed_envelope = bitgo.sign_transaction(envelope)

        response = bitgo.send_transaction(signed_envelope.to_xdr())

        if not response:
            raise BitGoAPIError("Error in BitGo send transaction")

        return self._poll_stellar_transaction_information(txid=response["txid"])

    @staticmethod
    def _poll_stellar_transaction_information(txid: str) -> dict:
        """
        Pooling the stellar network to get the transaction information.
        This method is used to retrieve the "envelope_xdr" and "paging_token"
        since BitGo doesn't return these values

        :param txid: The Stellar Network transaction id.
        :returns: Returns the transaction's information.
        """
        timeout_count = 0
        max_timeout = 10
        while timeout_count > max_timeout:
            try:
                return get_stellar_network_transaction_info(txid)
            except NotFoundError:
                sleep(1)
                timeout_count += 1
                pass

    @staticmethod
    def _create_recipient(address: str, amount: Union[Decimal, str]) -> Recipient:
        """
        Creates :class:`Recipient` instance.

        :param address: The destination account public key.
        :param amount: The transaction's amount.
        :returns: Returns a :class:`Recipient` instance.
        """
        return Recipient(
            amount=str(Operation.to_xdr_amount(amount)),
            address=address,
        )

    def _create_integration_from_asset(
        self,
        asset: Asset,
    ) -> BitGo:
        """
        Creates :class:`BitGo` instance.

        :param asset: the asset sent in payments.
        :returns: Returns a :class:`BitGo` instance.
        """
        return BitGo(
            asset_code=asset.code,
            asset_issuer=asset.issuer,
            api_key=self.api_key,
            api_passphrase=self.api_passphrase,
            wallet_id=self.wallet_id,
            api_url=self.api_url,
            stellar_coin_code=self.stellar_coin_code,
        )
