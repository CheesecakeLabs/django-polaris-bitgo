from uuid import uuid4

from polaris.models import Asset, Transaction
from rest_framework.request import Request
from stellar_sdk.keypair import Keypair

from .mocks import bitgo as bitgo_mocks, constants


def test_get_distribution_account(mocker, make_bitgo_integration):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")

    stellar_account_address = Keypair.random().public_key
    bitgo_mock = mocker.patch(
        "polaris_bitgo.bitgo.BitGo.get_public_key",
        return_value=stellar_account_address,
    )

    asset = mocker.Mock(spec=Asset)
    asset.code = "USDC"
    asset.issuer = Keypair.random().public_key

    bitgo_integration = make_bitgo_integration
    bitgo_account_address = bitgo_integration.get_distribution_account(asset)

    bitgo_mock.assert_called_once()

    assert bitgo_account_address == stellar_account_address


def test_save_receiving_account_and_memo(db, mocker, make_bitgo_integration):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")
    mocker.patch(
        "polaris_bitgo.bitgo.integration.memo_hex_to_base64", return_value="aramdommemo"
    )

    stellar_account_address = Keypair.random().public_key
    bitgo_mock = mocker.patch(
        "polaris_bitgo.bitgo.BitGo.get_public_key",
        return_value=stellar_account_address,
    )

    request = mocker.Mock(spec=Request)

    asset = mocker.Mock(spec=Asset)
    asset.code = "USDC"
    asset.issuer = Keypair.random().public_key

    transaction = mocker.Mock(spec=Transaction)
    transaction.id = uuid4()
    transaction.asset = asset

    bitgo_integration = make_bitgo_integration
    bitgo_integration.save_receiving_account_and_memo(request, transaction)

    bitgo_mock.assert_called_once()

    assert transaction.receiving_anchor_account == stellar_account_address
    assert transaction.memo_type == Transaction.MEMO_TYPES.hash
    assert transaction.memo == "aramdommemo"


def test_create_destination_account(mocker, make_bitgo_integration):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")
    mocker.patch(
        "polaris_bitgo.bitgo.BitGo._decrypt_private_key",
        return_value=Keypair.random().secret,
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.send_transaction",
        return_value=bitgo_mocks.send_transaction_response().json(),
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.build_transaction",
        return_value=bitgo_mocks.build_transaction_response().json(),
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_transfer_by_id",
        return_value={
            "state": "confirmed",
            "txid": "d263fdff34da8ca22400a1df68e5364b808e3a73dc2e762d17f6b6631165658c",
        },
    )
    mocker.patch(
        "stellar_sdk.call_builder.transactions_call_builder.TransactionsCallBuilder.call",
        return_value=constants.STELLAR_TRANSACTION_INFO_CREATE_ACCOUNT_RESPONSE,
    )

    transaction = mocker.Mock(spec=Transaction)
    transaction.to_address = Keypair.random().public_key

    bitgo_integration = make_bitgo_integration
    transaction_info = bitgo_integration.create_destination_account(transaction)

    assert (
        transaction_info == constants.STELLAR_TRANSACTION_INFO_CREATE_ACCOUNT_RESPONSE
    )


def test_submit_deposit_transaction(mocker, make_bitgo_integration):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")
    mocker.patch(
        "polaris_bitgo.bitgo.BitGo._decrypt_private_key",
        return_value=Keypair.random().secret,
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.send_transaction",
        return_value=bitgo_mocks.send_transaction_response().json(),
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.build_transaction",
        return_value=bitgo_mocks.build_transaction_response().json(),
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_transfer_by_id",
        return_value={
            "state": "confirmed",
            "txid": "d263fdff34da8ca22400a1df68e5364b808e3a73dc2e762d17f6b6631165658c",
        },
    )
    mocker.patch(
        "stellar_sdk.call_builder.transactions_call_builder.TransactionsCallBuilder.call",
        return_value=constants.STELLAR_TRANSACTION_INFO_PAYMENT_RESPONSE,
    )

    asset = mocker.Mock(spec=Asset)
    asset.significant_decimals = 2

    transaction = mocker.Mock(spec=Transaction)
    transaction.to_address = Keypair.random().public_key
    transaction.amount_in = 100
    transaction.amount_fee = 3
    transaction.asset = asset

    bitgo_integration = make_bitgo_integration
    transaction_info = bitgo_integration.submit_deposit_transaction(transaction)

    assert transaction_info == constants.STELLAR_TRANSACTION_INFO_PAYMENT_RESPONSE
