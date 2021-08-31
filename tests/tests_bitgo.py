from stellar_sdk import Keypair
from stellar_sdk.operation import Operation

from polaris_bitgo.bitgo import BitGo
from polaris_bitgo.bitgo.dtos import Recipient
from .mocks import bitgo as bitgo_mocks


def test_bitgo_build_transaction(mocker):
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.get_wallet",
        return_value=bitgo_mocks.get_wallet_response().json(),
    )
    mocker.patch("polaris_bitgo.bitgo.api.BitGoAPI.get_wallet_key_info")
    mocker.patch(
        "polaris_bitgo.bitgo.api.BitGoAPI.build_transaction",
        return_value=bitgo_mocks.build_transaction_response().json(),
    )

    asset_code = "BST"
    asset_amount = "10000"
    asset_issuer = "GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L"

    destination_account_public_key = (
        "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3"
    )

    bitgo = BitGo(
        asset_code=asset_code,
        asset_issuer=asset_issuer,
    )

    recipient = Recipient(
        amount=asset_amount,
        address=destination_account_public_key,
    )

    transaction_envelope = bitgo.build_transaction(recipient)

    assert transaction_envelope.transaction.source.public_key == bitgo.wallet.public_key
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
        transaction_envelope.transaction.operations[0].destination
        == destination_account_public_key
    )
    assert transaction_envelope.transaction.operations[0].source is None
    assert not transaction_envelope.transaction.v1


def test_bitgo_sign_transaction(mocker):
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

    asset_code = "BST"
    asset_issuer = "GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L"
    asset_amount = "10000"
    destination_account_public_key = (
        "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3"
    )

    bitgo_adapter = BitGo(
        asset_code=asset_code,
        asset_issuer=asset_issuer,
    )

    recipient = Recipient(
        amount=asset_amount,
        address=destination_account_public_key,
    )

    transaction_envelope = bitgo_adapter.build_transaction(recipient)
    transaction_envelope_signed = bitgo_adapter.sign_transaction(transaction_envelope)

    assert transaction_envelope_signed.signatures
