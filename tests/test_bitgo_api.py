import dataclasses
from urllib.parse import urljoin

import pytest
from stellar_sdk.transaction_envelope import TransactionEnvelope

from polaris_bitgo.bitgo.api import BitGoAPI
from polaris_bitgo.bitgo.dtos import Recipient, Wallet
from polaris_bitgo.helpers.exceptions import BitGoKeyInfoNotFound
from .mocks import bitgo as bitgo_mocks


# TODO: Move BitGoAPI instantiations to a pytest fixture
def test_get_wallet_success(mocker):
    bitgo = BitGoAPI(
        asset_code="BST",
        asset_issuer="GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    )
    wallet_id = bitgo.WALLET_ID

    bitgo_request_mock = mocker.patch(
        "requests.Session.get",
        return_value=bitgo_mocks.get_wallet_response(wallet_id=wallet_id),
    )

    expected_value = bitgo_mocks.get_wallet_data(wallet_id=wallet_id)

    bitgo.get_wallet()

    bitgo_request_mock.assert_called_once_with(
        urljoin(bitgo.API_URL, f"/api/v2/{bitgo.COIN}/wallet/{wallet_id}"),
    )

    assert bitgo_request_mock.return_value.json() == expected_value


def test_get_wallet_key_info_success(mocker):
    bitgo = BitGoAPI(
        asset_code="BST",
        asset_issuer="GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    )
    wallet_id = bitgo.WALLET_ID

    wallet_data_mock = bitgo_mocks.get_wallet_data(wallet_id=wallet_id)
    wallet = Wallet(
        public_key=wallet_data_mock.get("coinSpecific", {}).get("rootAddress"),
        keys=wallet_data_mock.get("keys", []),
    )

    bitgo_key_info_request_mock = mocker.patch(
        "requests.Session.get", return_value=bitgo_mocks.get_wallet_key_info_response()
    )

    expected_value = bitgo_mocks.get_wallet_key_info_data()

    key_info = bitgo.get_wallet_key_info(wallet)

    bitgo_key_info_request_mock.assert_called_once_with(
        urljoin(bitgo.API_URL, f"/api/v2/{bitgo.COIN}/key"),
    )

    assert bitgo_key_info_request_mock.return_value.json() == expected_value
    assert key_info == {
        "coinSpecific": {},
        "encryptedPrv": '{"iv":"SomeIVtest==","v":1,"iter":10000,"ks":256,"ts":64,"mode":"ccm","adata":"","cipher":"aes","salt":"MySalt/tx=","ct":"DLZqoR9x3vsJmkr/l3wCdHq1zcdTlOrRbZ6bV73BVVIBzc5nt/PzanzPTbXM586/8lbyfjt8he8OvBGNEhC1bg=="}',
        "id": "key1-user",
        "pub": "GCABV25ZAOFZDRFMRHTGVVV7FMJFS2CK2XKF5WR5B475DWML4275OFLI",
        "source": "user",
    }


def test_get_wallet_key_info_not_found(mocker):
    bitgo = BitGoAPI(
        asset_code="BST",
        asset_issuer="GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    )
    wallet_id = bitgo.WALLET_ID

    wallet_data_mock = bitgo_mocks.get_wallet_data(
        wallet_id=wallet_id, keys=["key1", "key2", "key3"]
    )
    wallet = Wallet(
        public_key=wallet_data_mock.get("coinSpecific", {}).get("rootAddress"),
        keys=wallet_data_mock.get("keys", []),
    )

    mocker.patch(
        "requests.Session.get", return_value=bitgo_mocks.get_wallet_key_info_response()
    )

    with pytest.raises(BitGoKeyInfoNotFound):
        bitgo.get_wallet_key_info(wallet)


def test_build_transaction_success(mocker):
    bitgo_request_mock = mocker.patch(
        "requests.Session.post", return_value=bitgo_mocks.build_transaction_response()
    )

    bitgo = BitGoAPI(
        asset_code="BST",
        asset_issuer="GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    )

    amount = "10000"
    address = "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3"

    recipient = Recipient(amount=amount, address=address)

    response = bitgo.build_transaction(recipient)

    bitgo_request_mock.assert_called_once_with(
        urljoin(
            bitgo.API_URL, f"/api/v2/{bitgo.COIN}/wallet/{bitgo.WALLET_ID}/tx/build"
        ),
        json={"recipients": [dataclasses.asdict(recipient)]},
    )

    assert response == bitgo_request_mock.return_value.json()


def test_send_transaction_success(mocker):
    bitgo_build_response = bitgo_mocks.build_transaction_data()

    bitgo_request_mock = mocker.patch(
        "requests.Session.post", return_value=bitgo_mocks.send_transaction_response()
    )

    bitgo = BitGoAPI(
        asset_code="BST",
        asset_issuer="GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
    )

    transaction_envelope = TransactionEnvelope.from_xdr(
        bitgo_build_response["txBase64"], "Test SDF Network ; September 2015"
    )

    transaction_response = bitgo.send_transaction(transaction_envelope.to_xdr())

    bitgo_request_mock.assert_called_once_with(
        urljoin(
            bitgo.API_URL, f"/api/v2/{bitgo.COIN}/wallet/{bitgo.WALLET_ID}/tx/send"
        ),
        json={
            "halfSigned": {
                "txBase64": transaction_envelope.to_xdr(),
            }
        },
    )

    assert transaction_response == bitgo_request_mock.return_value.json()
