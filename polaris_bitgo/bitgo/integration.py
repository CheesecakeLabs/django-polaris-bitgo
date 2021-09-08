from time import sleep
from decimal import Decimal
from typing import Union

from polaris import settings as polaris_settings
from polaris.integrations import CustodyIntegration
from polaris.models import Asset, Transaction
from polaris.utils import get_logger, memo_hex_to_base64
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
        num_retries: int = 5,
    ):

        if not api_key:
            raise ValueError("The API Key is required.")
        if not api_passphrase:
            raise ValueError("The API Passphrase is required.")
        if not wallet_id:
            raise ValueError("The Wallet ID is required.")

        super().__init__()

        self.api_key = api_key
        self.api_passphrase = api_passphrase
        self.wallet_id = wallet_id
        self.api_url = api_url
        self.stellar_coin_code = stellar_coin_code
        self.num_retries = num_retries

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
        """
        Save the Stellar account that the client should use as the destination
        of the payment transaction to ``Transaction.receiving_anchor_account``,
        the string representation of the memo the client should attach to the
        transaction to ``Transaction.memo``, and the type of that memo to
        ``Transaction.memo_type``.

        This method is only called once for a given transaction. The values
        saved will be returned to the client in the response to this request or
        in future ``GET /transaction`` responses.

        **Polaris assumes ``Transaction.save()`` is called within this method.**

        The memo saved to the transaction object _must_ be unique to the
        transaction, since the anchor is expected to match the database record
        represented by `transaction` with the on-chain transaction submitted.

        This function differs from ``get_distribution_account()`` by allowing the
        anchor to return any Stellar account that can be used to receive a payment.
        This is ideal when the account used is determined by a custody service
        provider that does not guarantee that the account provided will be the
        account provided for future transactions.

        :param request: the request that initiated the call to this function
        :param transaction: the transaction a Stellar account and memo must be
            saved to
        """
        padded_hex_memo = "0" * (64 - len(transaction.id.hex)) + transaction.id.hex

        bitgo = self._create_integration_from_asset(transaction.asset)

        transaction.receiving_anchor_account = bitgo.get_public_key()
        transaction.memo = memo_hex_to_base64(padded_hex_memo)
        transaction.memo_type = Transaction.MEMO_TYPES.hash
        transaction.save(
            update_fields=["receiving_anchor_account", "memo", "memo_type"]
        )

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

    def _poll_stellar_transaction_information(self, txid: str) -> dict:
        """
        Pooling the stellar network to get the transaction information.
        This method is used to retrieve the "envelope_xdr" and "paging_token"
        since BitGo doesn't return these values

        :param txid: The Stellar Network transaction id.
        :returns: Returns the transaction's information.
        """
        try:
            return get_stellar_network_transaction_info(
                txid, num_retries=self.num_retries
            )
        except NotFoundError:
            raise RuntimeError(
                f"Error trying to retrieve transaction information. Transaction id: {txid}"
            )

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

    @property
    def claimable_balances_supported(self) -> bool:
        """
        Return ``True`` if the custody service provider supports sending deposit
        payments in the form of claimable balances, ``False`` otherwise.
        """
        return False

    @property
    def account_creation_supported(self) -> bool:
        """
        Return ``True`` if the custody service provider supports funding Stellar
        accounts not custodied by the provider, ``False`` otherwise.
        """
        return True
