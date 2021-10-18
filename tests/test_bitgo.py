import pytest
from stellar_sdk import Keypair
from stellar_sdk.operation import Operation

from .mocks import bitgo as bitgo_mocks


def test_bitgo_build_transaction(mocker, make_bitgo, make_recipient):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.build_transaction",
        return_value=bitgo_mocks.build_transaction_response().json(),
    )

    bitgo = make_bitgo()
    recipient = make_recipient()

    transaction_envelope = bitgo.build_transaction(recipient)

    asset_code = "BST"
    asset_amount = "10000"
    destination_account_public_key = (
        "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3"
    )

    assert transaction_envelope.transaction.source.account_id == bitgo.wallet.public_key
    assert (
        str(
            Operation.to_xdr_amount(
                transaction_envelope.transaction.operations[0].amount
            )
        )
        == asset_amount
    )
    assert transaction_envelope.transaction.operations[0].asset.code == asset_code
    assert (
        transaction_envelope.transaction.operations[0].destination.account_id
        == destination_account_public_key
    )
    assert transaction_envelope.transaction.operations[0].source is None
    assert not transaction_envelope.transaction.v1


def test_bitgo_sign_transaction(mocker, make_bitgo, make_recipient):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )

    bitgo_get_wallet_key_info = mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info"
    )
    bitgo_get_wallet_key_info.return_value = {
        "coinSpecific": {},
        "encryptedPrv": '{"iv":"SomeIVtest==","v":1,"iter":10000,"ks":256,"ts":64,"mode":"ccm","adata":"","cipher":"aes","salt":"MySalt/tx=","ct":"DLZqoR9x3vsJmkr/l3wCdHq1zcdTlOrRbZ6bV73BVVIBzc5nt/PzanzPTbXM586/8lbyfjt8he8OvBGNEhC1bg=="}',
        "id": "key1-user",
        "pub": "GCABV25ZAOFZDRFMRHTGVVV7FMJFS2CK2XKF5WR5B475DWML4275OFLI",
        "source": "user",
    }

    mocker.patch(
        "polaris_bitgo.bitgo.BitGo._decrypt_private_key",
        return_value=Keypair.random().secret,
    )
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.build_transaction",
        return_value=bitgo_mocks.build_transaction_response().json(),
    )

    bitgo_adapter = make_bitgo()
    recipient = make_recipient()

    transaction_envelope = bitgo_adapter.build_transaction(recipient)
    transaction_envelope_signed = bitgo_adapter.sign_transaction(transaction_envelope)

    assert transaction_envelope_signed.signatures


def test_get_stellar_transaction_id_success(mocker, make_bitgo):
    network_tx_id = "7586ec0223fc193da6fc609b92a62a96ae86258873480d8bc288723e29028cd3"

    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")

    bitgo_api_mock = mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_transfer_by_id",
        side_effect=[
            {"state": "pending"},
            {"state": "pending"},
            {"state": "pending"},
            {"state": "confirmed", "txid": network_tx_id},
        ],
    )

    bitgo = make_bitgo()
    stellar_transaction_id = bitgo.get_stellar_transaction_id(
        "615da283c6d7cb000686dacbdfdca0ec"
    )

    bitgo_api_mock.assert_called()

    assert stellar_transaction_id == network_tx_id


def test_get_stellar_transaction_id_runtime_error(mocker, make_bitgo):

    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")

    bitgo_api_mock = mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_transfer_by_id",
        side_effect=[
            {"state": "pending"},
            {"state": "pending"},
            {"state": "pending"},
            {"state": "failed"},
        ],
    )

    bitgo = make_bitgo()

    with pytest.raises(RuntimeError, match="BitGo failed to complete the transfer."):
        bitgo.get_stellar_transaction_id("615da283c6d7cb000686dacbdfdca0ec")

    bitgo_api_mock.assert_called()
