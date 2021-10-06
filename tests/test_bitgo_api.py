import dataclasses
from urllib.parse import urljoin

import pytest
from rest_framework import status
from stellar_sdk.transaction_envelope import TransactionEnvelope

from polaris_bitgo.bitgo.dtos import Wallet
from polaris_bitgo.helpers.exceptions import BitGoAPIError, BitGoKeyInfoNotFound
from .mocks import bitgo as bitgo_mocks

REQUEST_METHOD_GET_MOCK = "requests.Session.get"
REQUEST_METHOD_POST_MOCK = "requests.Session.post"


def test_get_wallet_success(mocker, make_bitgo_api):
    bitgo_api = make_bitgo_api()
    wallet_id = bitgo_api.WALLET_ID

    bitgo_request_mock = mocker.patch(
        REQUEST_METHOD_GET_MOCK,
        return_value=bitgo_mocks.get_wallet_response(wallet_id=wallet_id),
    )

    expected_value = bitgo_mocks.get_wallet_data(wallet_id=wallet_id)

    bitgo_api.get_wallet()

    bitgo_request_mock.assert_called_once_with(
        urljoin(bitgo_api.API_URL, f"/api/v2/{bitgo_api.COIN}/wallet/{wallet_id}"),
    )

    assert bitgo_request_mock.return_value.json() == expected_value


def test_get_wallet_key_info_success(mocker, make_bitgo_api):
    bitgo_api = make_bitgo_api()
    wallet_id = bitgo_api.WALLET_ID

    wallet_data_mock = bitgo_mocks.get_wallet_data(wallet_id=wallet_id)
    wallet = Wallet(
        public_key=wallet_data_mock.get("coinSpecific", {}).get("rootAddress"),
        keys=wallet_data_mock.get("keys", []),
    )

    bitgo_key_info_request_mock = mocker.patch(
        REQUEST_METHOD_GET_MOCK, return_value=bitgo_mocks.get_wallet_key_info_response()
    )

    expected_value = bitgo_mocks.get_wallet_key_info_data()

    key_info = bitgo_api.get_wallet_key_info(wallet)

    bitgo_key_info_request_mock.assert_called_once_with(
        urljoin(bitgo_api.API_URL, f"/api/v2/{bitgo_api.COIN}/key"),
    )

    assert bitgo_key_info_request_mock.return_value.json() == expected_value
    assert key_info == {
        "coinSpecific": {},
        "encryptedPrv": '{"iv":"SomeIVtest==","v":1,"iter":10000,"ks":256,"ts":64,"mode":"ccm","adata":"","cipher":"aes","salt":"MySalt/tx=","ct":"DLZqoR9x3vsJmkr/l3wCdHq1zcdTlOrRbZ6bV73BVVIBzc5nt/PzanzPTbXM586/8lbyfjt8he8OvBGNEhC1bg=="}',
        "id": "key1-user",
        "pub": "GCABV25ZAOFZDRFMRHTGVVV7FMJFS2CK2XKF5WR5B475DWML4275OFLI",
        "source": "user",
    }


def test_get_wallet_key_info_not_found(mocker, make_bitgo_api, make_wallet):
    bitgo_api = make_bitgo_api()
    wallet_id = bitgo_api.WALLET_ID

    wallet_data_mock = bitgo_mocks.get_wallet_data(
        wallet_id=wallet_id, keys=["key1", "key2", "key3"]
    )
    wallet = make_wallet(
        wallet_data_mock.get("coinSpecific", {}).get("rootAddress"),
        wallet_data_mock.get("keys", []),
    )

    mocker.patch(
        REQUEST_METHOD_GET_MOCK, return_value=bitgo_mocks.get_wallet_key_info_response()
    )

    with pytest.raises(BitGoKeyInfoNotFound):
        bitgo_api.get_wallet_key_info(wallet)


def test_build_transaction_success(mocker, make_bitgo_api, make_recipient):
    bitgo_request_mock = mocker.patch(
        REQUEST_METHOD_POST_MOCK, return_value=bitgo_mocks.build_transaction_response()
    )

    bitgo_api = make_bitgo_api()
    recipient = make_recipient()

    response_data = bitgo_api.build_transaction(recipient)

    bitgo_request_mock.assert_called_once_with(
        urljoin(
            bitgo_api.API_URL,
            f"/api/v2/{bitgo_api.COIN}/wallet/{bitgo_api.WALLET_ID}/tx/build",
        ),
        json={"recipients": [dataclasses.asdict(recipient)]},
    )

    assert response_data == bitgo_request_mock.return_value.json()


def test_send_transaction_success(mocker, make_bitgo_api):
    bitgo_build_response = bitgo_mocks.build_transaction_data()

    bitgo_request_mock = mocker.patch(
        REQUEST_METHOD_POST_MOCK, return_value=bitgo_mocks.send_transaction_response()
    )

    bitgo_api = make_bitgo_api()

    transaction_envelope = TransactionEnvelope.from_xdr(
        bitgo_build_response["txBase64"], "Test SDF Network ; September 2015"
    )

    transaction_response = bitgo_api.send_transaction(transaction_envelope.to_xdr())

    bitgo_request_mock.assert_called_once_with(
        urljoin(
            bitgo_api.API_URL,
            f"/api/v2/{bitgo_api.COIN}/wallet/{bitgo_api.WALLET_ID}/tx/send",
        ),
        json={
            "halfSigned": {
                "txBase64": transaction_envelope.to_xdr(),
            }
        },
    )

    assert transaction_response == bitgo_request_mock.return_value.json()


def test_get_transfer_by_id_success(mocker, make_bitgo_api):
    transaction_id = "615da283c6d7cb000686dacbdfdca0ec"
    bitgo_api = make_bitgo_api()

    bitgo_request_mock = mocker.patch(
        REQUEST_METHOD_GET_MOCK,
        return_value=bitgo_mocks.get_transaction_by_id_response(
            transaction_id=transaction_id, wallet_id=bitgo_api.WALLET_ID
        ),
    )

    response_data = bitgo_api.get_transfer_by_id(transaction_id)

    bitgo_request_mock.assert_called_once_with(
        urljoin(
            bitgo_api.API_URL,
            f"/api/v2/{bitgo_api.COIN}/wallet/{bitgo_api.WALLET_ID}/transfer/{transaction_id}",
        ),
    )

    assert response_data == bitgo_request_mock.return_value.json()
    assert response_data["id"] == transaction_id
    assert response_data["tags"] == [bitgo_api.WALLET_ID]


def test_get_transfer_by_id_bad_request(mocker, make_bitgo_api):
    transaction_id = "615da283c6d7cb000686dacbdfdca0ec"

    bitgo_api = make_bitgo_api()

    url = urljoin(
        bitgo_api.API_URL,
        f"/api/v2/{bitgo_api.COIN}/wallet/{bitgo_api.WALLET_ID}/transfer/{transaction_id}",
    )

    bitgo_request_mock = mocker.patch(
        REQUEST_METHOD_GET_MOCK,
        return_value=bitgo_mocks.get_transaction_by_id_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            url=url,
            reason="Bad Request",
            transaction_id=transaction_id,
            wallet_id=bitgo_api.WALLET_ID,
        ),
    )

    with pytest.raises(
        BitGoAPIError,
        match=f"400 Error: Bad Request for url {url}. Response Text: ",
    ):
        bitgo_api.get_transfer_by_id(transaction_id)

    bitgo_request_mock.assert_called_once_with(url)
