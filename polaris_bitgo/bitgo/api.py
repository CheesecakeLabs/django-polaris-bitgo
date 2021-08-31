import dataclasses
from typing import Optional
from urllib.parse import urljoin

import requests
from django.conf import settings

from polaris_bitgo.helpers.exceptions import BitGoAPIError, BitGoKeyInfoNotFound
from .dtos import Recipient, Wallet


class BitGoAPI:
    def __init__(self, asset_code: str, asset_issuer: Optional[str] = None):
        self.API_URL = settings.BITGO_API_URL
        self.API_KEY = settings.BITGO_API_KEY
        self.API_PASSPHRASE = settings.BITGO_API_PASSPHRASE
        self.WALLET_ID = settings.BITGO_WALLET_ID
        self.COIN = self._get_coin(asset_code, asset_issuer)

        base_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_KEY}",
        }

        self.session = requests.Session()
        self.session.headers.update(**base_headers)

    @staticmethod
    def _get_coin(asset_code: str, asset_issuer: Optional[str] = None) -> str:
        return (
            f"{settings.BITGO_STELLAR_COIN_CODE}:{asset_code}-{asset_issuer}"
            if asset_issuer
            else settings.BITGO_STELLAR_COIN_CODE
        )

    @staticmethod
    def _handle_response(response: requests.Response) -> dict:
        """
        Handle the BitGo's API response. In case the response is not
        successful, it raises a :class:`BitGoAPIError`, otherwise it
        returns the response's JSON.

        :return: Returns BitGo's API response's JSON.
        """
        if response.ok:
            return response.json()
        msg = f"{response.status_code} Error: {response.reason} for url {response.url}. Response Text: {response.text}"
        raise BitGoAPIError(msg, response=response)

    def get_wallet(self) -> dict:
        """
        Gets the wallet's information.

        :return: Returns a dict with the wallet's information.
        """
        url = urljoin(self.API_URL, f"/api/v2/{self.COIN}/wallet/{self.WALLET_ID}")
        response = self.session.get(url)
        return self._handle_response(response)

    def get_wallet_key_info(self, wallet: Wallet) -> dict:
        """
        Gets the wallet's keys information. Generally, the API returns 3
        keys: user, backup, and BitGo.

        Each key has some information, like the encrypted private key
        (except the BitGo one) with the AES-CCM cipher.

        The important one is the user key. That encrypted private key is
        used to pre-sign the transaction locally before being sent to
        BitGo's API.

        :param wallet: The wallet's information.
        :return: Returns a dict with the wallet's user key information.
        """
        keys_id_list = wallet.keys

        url = urljoin(self.API_URL, f"/api/v2/{self.COIN}/key")

        response = self.session.get(url)

        wallet_keys_info = self._handle_response(response)
        for wallet_key_info in wallet_keys_info["keys"]:
            if (
                wallet_key_info["id"] in keys_id_list
                and wallet_key_info["source"] == "user"
            ):
                return wallet_key_info

        raise BitGoKeyInfoNotFound("Wallet Key info not found.")

    def build_transaction(self, recipient: Recipient) -> dict:
        """
        Builds a transaction on BitGo's API. It returns some information
        about the transaction, like the transaction's XDR.

        :param recipient: The :class:`Recipient` object with the amount
        (XDR Amount) and the destination address.
        :return: Returns the BitGo's API response.
        """
        url = urljoin(
            self.API_URL, f"/api/v2/{self.COIN}/wallet/{self.WALLET_ID}/tx/build"
        )
        data = {
            "recipients": [
                dataclasses.asdict(recipient),
            ]
        }

        response = self.session.post(url, json=data)

        return self._handle_response(response)

    def send_transaction(self, transaction_envelope_xdr: str) -> dict:
        """
        Sends the transaction's XDR to BitGo, which does another
        signature to the transaction, then sends it to the Stellar
        Network.

        :param transaction_envelope_xdr: The base64 string with the
        transaction's information.
        :return: Returns the BitGo's API response. It contains some
        information about the transaction, like the Stellar Network
        transaction id.
        """
        url = urljoin(
            self.API_URL, f"/api/v2/{self.COIN}/wallet/{self.WALLET_ID}/tx/send"
        )
        data = {
            "halfSigned": {
                "txBase64": transaction_envelope_xdr,
            }
        }

        response = self.session.post(url, json=data)

        return self._handle_response(response)
