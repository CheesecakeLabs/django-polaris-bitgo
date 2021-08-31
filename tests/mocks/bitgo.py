from typing import List

import requests
from rest_framework import status

from . import constants


def get_wallet_data(*, wallet_id: str = "", keys: List[str] = None):
    if not keys:
        keys = ["key1-user", "key2-backup", "key3-bitgo"]

    return {
        "id": wallet_id,
        "users": [
            {
                "user": "61082e4964959100080276cbb1810333",
                "permissions": ["admin", "view", "spend"],
            }
        ],
        "coin": "txlm",
        "label": "Stellar Wallet",
        "m": 2,
        "n": 3,
        "keys": keys,
        "keySignatures": {},
        "tags": [wallet_id],
        "disableTransactionNotifications": False,
        "freeze": {},
        "deleted": False,
        "approvalsRequired": 1,
        "isCold": False,
        "coinSpecific": {
            "rootAddress": "GCVUOY77ULM5PZNDSP3S7N4RAHRP6PI4TF3ZFIYDSHQPW2QWBS2KUGLM",
            "pendingChainInitialization": False,
            "creationFailure": [],
            "lastMemoId": "0",
            "trustedTokens": [],
        },
        "admin": {
            "policy": {
                "date": "2021-08-02T18:09:43.675Z",
                "id": "610834e7a6ea8c00066e77c896d706e6",
                "label": "default",
                "rules": [],
                "version": 0,
                "latest": True,
            }
        },
        "clientFlags": [],
        "allowBackupKeySigning": False,
        "recoverable": True,
        "startDate": "2021-08-02T18:09:43.000Z",
        "type": "hot",
        "buildDefaults": {},
        "customChangeKeySignatures": {},
        "hasLargeNumberOfAddresses": False,
        "config": {},
        "balanceString": "49963520733",
        "confirmedBalanceString": "49963520733",
        "spendableBalanceString": "49938520633",
        "tokens": {
            "txlm:BST-GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L": {
                "balanceString": "1000000",
                "confirmedBalanceString": "0",
                "spendableBalanceString": "0",
                "transferCount": 0,
            },
            "txlm:ABC-GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L": {
                "balanceString": "0",
                "confirmedBalanceString": "0",
                "spendableBalanceString": "0",
                "transferCount": 0,
            },
            "txlm:DEF-GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L": {
                "balanceString": "0",
                "confirmedBalanceString": "0",
                "spendableBalanceString": "0",
                "transferCount": 0,
            },
        },
        "receiveAddress": {
            "id": "610834e7a6ea8c00066e77d05760823b",
            "address": "GCVUOY77ULM5PZNDSP3S7N4RAHRP6PI4TF3ZFIYDSHQPW2QWBS2KUGLM?memoId=0",
            "chain": 0,
            "index": 0,
            "coin": "txlm",
            "wallet": wallet_id,
            "coinSpecific": {
                "rootAddress": "GCVUOY77ULM5PZNDSP3S7N4RAHRP6PI4TF3ZFIYDSHQPW2QWBS2KUGLM",
                "memoId": "0",
            },
        },
        "pendingApprovals": [],
    }


def get_wallet_response(
    *,
    wallet_id: str = "",
    keys: List[str] = None,
    status_code: int = status.HTTP_200_OK,
    reason: str = "",
    url: str = "",
):
    response = requests.Response()
    response.status_code = status_code
    response.reason = reason
    response.url = url
    response.json = lambda: get_wallet_data(wallet_id=wallet_id, keys=keys)

    return response


def get_wallet_key_info_data(*, key_id: str = "key1-user"):
    return {
        "keys": [
            {
                "id": key_id,
                "pub": "GCABV25ZAOFZDRFMRHTGVVV7FMJFS2CK2XKF5WR5B475DWML4275OFLI",
                "source": "user",
                "encryptedPrv": '{"iv":"SomeIVtest==","v":1,"iter":10000,"ks":256,"ts":64,"mode":"ccm","adata":"","cipher":"aes","salt":"MySalt/tx=","ct":"DLZqoR9x3vsJmkr/l3wCdHq1zcdTlOrRbZ6bV73BVVIBzc5nt/PzanzPTbXM586/8lbyfjt8he8OvBGNEhC1bg=="}',
                "coinSpecific": {},
            },
            {
                "id": "key2-backup",
                "pub": "GBUXLQUP4URYP3G2AK2NB3BXX4A7XZJDPYN2NTQTVH3UOYTXISDT2TON",
                "source": "backup",
                "coinSpecific": {},
            },
            {
                "id": "key3-bitgo",
                "pub": "GC3Y2DC5I6EQY3SUPR4BUQRGOJWGHOMPZLV7JFOHZ76G63PTM6HWFYD6",
                "source": "bitgo",
                "isBitGo": True,
                "coinSpecific": {},
            },
        ],
        "limit": 100,
    }


def get_wallet_key_info_response(
    *,
    key_id: str = "key1-user",
    status_code: int = status.HTTP_200_OK,
    reason: str = "",
    url: str = "",
):
    response = requests.Response()
    response.status_code = status_code
    response.reason = reason
    response.url = url
    response.json = lambda: get_wallet_key_info_data(key_id=key_id)

    return response


def build_transaction_data():
    return constants.BITGO_BUILD_TRANSACTION_RESPONSE


def build_transaction_response(
    *,
    status_code: int = status.HTTP_200_OK,
    reason: str = "",
    url: str = "",
):
    response = requests.Response()
    response.status_code = status_code
    response.reason = reason
    response.url = url
    response.json = build_transaction_data

    return response


def send_transaction_data():
    return constants.BITGO_SEND_TRANSACTION_RESPONSE


def send_transaction_response(
    *,
    status_code: int = status.HTTP_201_CREATED,
    reason: str = "",
    url: str = "",
):
    response = requests.Response()
    response.status_code = status_code
    response.reason = reason
    response.url = url
    response.json = send_transaction_data

    return response
