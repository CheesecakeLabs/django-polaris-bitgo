BITGO_BUILD_TRANSACTION_RESPONSE = {
    "txBase64": "AAAAAKtHY/+i2dflo5P3L7eRAeL/PRyZd5KjA5Hg+2oWDLSqAAABLAAL4mwAAAAOAAAAAAAAAAAAAAABAAAAAAAAAAEAAAAAeS007fjRCo55xuCKNGWvV5a53iy692muFDbApFWiAlkAAAABQlNUAAAAAABhNDpbuY4frrgwVQqkws7jxK+k4IMrJ6BaE0OFUva9vwAAAAAAACcQAAAAAAAAAAA=",
    "txInfo": {
        "_networkPassphrase": "Test SDF Network ; September 2015",
        "source": "GCVUOY77ULM5PZNDSP3S7N4RAHRP6PI4TF3ZFIYDSHQPW2QWBS2KUGLM",
        "fee": 300,
        "sequence": "3345178228162574",
        "operations": [
            {
                "type": "payment",
                "destination": "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3",
                "asset": {
                    "code": "BST",
                    "issuer": "GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
                },
                "amount": "0.0010000",
            }
        ],
        "signatures": [],
    },
    "feeInfo": {
        "date": "2021-08-20T15:51:51.177Z",
        "height": 1073182,
        "baseReserve": "5000000",
        "baseFee": "100",
        "fee": 300,
        "feeString": "300",
        "payGoFee": 0,
        "payGoFeeString": "0",
    },
    "coin": "txlm",
    "token": "txlm:BST-GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L",
}

BITGO_SEND_TRANSACTION_RESPONSE = {
    "transfer": {
        "id": "bitgo_id",
        "coin": "txlm",
        "wallet": "key1-user",
        "walletType": "hot",
        "txid": "c189b2b1a0386eaf4a9f7d393d5a295dfb0efaf5671b1f418f06c2215a1418bc",
        "height": 999999999,
        "heightId": "999999999-bitgo_id",
        "date": "2021-08-16T20:00:30.670Z",
        "type": "send",
        "value": -310,
        "valueString": "-310",
        "baseValue": -10,
        "baseValueString": "-10",
        "feeString": "300",
        "payGoFee": 0,
        "payGoFeeString": "0",
        "usd": -1.178e-05,
        "usdRate": 0.38,
        "state": "signed",
        "instant": False,
        "isReward": False,
        "isFee": False,
        "tags": ["key1-user"],
        "history": [
            {"date": "2021-08-16T20:00:30.669Z", "action": "signed"},
            {
                "date": "2021-08-16T20:00:29.643Z",
                "user": "user_id",
                "action": "created",
            },
        ],
        "signedDate": "2021-08-16T20:00:30.669Z",
        "entries": [
            {
                "address": "GD3BNTO5WL3PAFWLXMK2YOFGLBACXQE27SJ6LSUYS253PMGD47EH2WKO",
                "wallet": "key1-user",
                "value": -310,
                "valueString": "-310",
            },
            {
                "address": "GB4S2NHN7DIQVDTZY3QIUNDFV5LZNOO6FS5PO2NOCQ3MBJCVUIBFTJH3",
                "value": 10,
                "valueString": "10",
            },
        ],
        "signedTime": "2021-08-16T20:00:30.669Z",
        "createdTime": "2021-08-16T20:00:29.643Z",
    },
    "txid": "c189b2b1a0386eaf4a9f7d393d5a295dfb0efaf5671b1f418f06c2215a1418bc",
    "tx": "AAAAAPYWzd2y9vAWy7sVrDimWEArwJr8k+XKmJa7t7DD58h9AAABLAAL5REAAAAEAAAAAAAAAAAAAAABAAAAAAAAAAEAAAAAeS007fjRCo55xuCKNGWvV5a53iy692muFDbApFWiAlkAAAAAAAAAAAAAAAoAAAAAAAAAAotHJsAAAABAr7M8+msGsqA9S8T8HBAv7w8u59vr0aW2U1MME4dUjpqnZrCTf7Ll9rj/go9RCK+BR2UJw0idlQyT7bTgCHPFC6NklT8AAABAPGt0Afb9QvT0QjY72ynzsK2ElWpQBQHnPq/b2tik6LRkd5fE7Bc8imKKjcnWobVJUvSf7f9RVSaucrLUZBSsDQ==",
    "status": "signed",
}
