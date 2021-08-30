# Django Polaris Custodial

Polaris Custodial is a Django app built to extend Polaris functionalities by providing the possibility of using a custodial wallet as the anchor's supply account. By default, it deliveries a full integration with BitGo's wallet, and at the same time, offers you ways to add and customize other custodial solutions.

## Dependencies

- django-polaris >= 1.4.1
- pycryptodome == 3.10.1

## Installation

```shell
$ pip install django-polaris django-polaris-custodial
```

```python
INSTALLED_APPS = [
    ...
    # polaris dependencies
    "rest_framework",
    "corsheaders",
    "polaris",
    # polaris custodial dependency
    "polaris_custodial",
    ...
]
```

## How to use

### BitGo

To use the BitGo's wallet, it is necessary to import Polaris Custodial from the package and pass it as an argument to the `custodial` parameter in the Polaris' `register_integrations` function.

```python
# apps.py

from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = "my_app"

    def ready(self):
        from polaris.integrations import register_integrations
        from polaris_custodial.bitgo import BitGoIntegration
        from .integrations import (
            ...
            MyRailsIntegration,
        )

        register_integrations(
            ...,
            rails=MyRailsIntegration(),
            custodial=BitGoIntegration(),
        )
```

On your `settings.py` file you'll need to add the following configuration variables. For improved security, we strongly recommend to add them to Environment Variables to keep them separated from the code.

- **BITGO_API_URL**: Refers to the BitGo's API base URL. Use `https://app.bitgo.com` for production environment and `https://app.bitgo-test.com` for the test environment.
  
- **BITGO_API_KEY**: Refers to the API Key for the BitGo account. It can be generated on your BitGo account by navigating to "Account Settings" -> "Developer Options" -> "Access Tokens". Here, click on the "+" button to add a token. On the following screen, fill in the information about the token that will be created.
  
   **Note**: We recommend to set a high value to `Lifetime Spending Limits` (up to `9223372036854775391` - the max value from Stellar Network) so you won't have to unlock each transaction manually after reaching the limit.

    After filling in all the information, your form should look like this:

    Upon finishing it, you should receive your `API Key`.

- **BITGO_API_PASSPHRASE**: The specific password for the wallet, to encrypt the user key on BitGo. This password is set when creating the wallet. You can change this password clicking on "Wallets" -> Access your wallet -> "Settings". There you will have a section where you can change the password.
  
- **BITGO_WALLET_ID**: This information can be found by accessing your wallet and going to the "Settings" tab.
  
- **BITGO_STELLAR_COIN_CODE**: Use `xlm` for production environment and `txlm` for test environment.

```python
# settings.py
...

BITGO_API_URL = "https://app.bitgo-test.com"
BITGO_API_KEY = "my_bitgo_api_key"
BITGO_API_PASSPHRASE = "my_bitgo_api_passphrase"
BITGO_WALLET_ID = "my_wallet_id"
BITGO_STELLAR_COIN_CODE = "xlm"
```

After this you are ready to use BitGo as the supply account for your Anchor on Stellar Network.

#### BitGo's Stellar supported tokens (assets)

Environment | Coin Type | Code | Issuer Website
--- | --- | --- | ---
Stellar Testnet	| `txlm:BST-GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L` | **BST** |
Stellar Mainnet	| `xlm:VELO-GDM4RQUQQUVSKQA7S6EM7XBZP3FCGH4Q7CL6TABQ7B2BEJ5ERARM2M5M` | **VELO** | [velo.org](velo.org)
Stellar Mainnet	| `xlm:SLT-GCKA6K5PCQ6PNF5RQBF7PQDJWRHO6UOGFMRLK3DYHDOI244V47XKQ4GP` | **SLT** | [smartlands.io](smartlands.io)
Stellar Mainnet	| `xlm:USD-GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX` | **USD** | [anchorusd.com](anchorusd.com)
Stellar Mainnet	| `xlm:ETH-GBVOL67TMUQBGL4TZYNMY3ZQ5WGQYFPFD5VJRWXR72VA33VFNL225PL5` | **ETH** | [stellarport.io](stellarport.io)
Stellar Mainnet	| `xlm:WXT-GASBLVHS5FOABSDNW5SPPH3QRJYXY5JHA2AOA2QHH2FJLZBRXSG4SWXT` | **WXT** | [wxt.wirexapp.com](wxt.wirexapp.com)
Stellar Mainnet	| `xlm:USDC-GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` | **USDC** | [centre.io](centre.io)
Stellar Mainnet	| `xlm:SIX-GDMS6EECOH6MBMCP3FYRYEVRBIV3TQGLOFQIPVAITBRJUMTI6V7A2X6Z` | **SIX** | [six.network](six.network)
Stellar Mainnet	| `xlm:ARST-GCSAZVWXZKWS4XS223M5F54H2B6XPIIXZZGP7KEAIU6YSL5HDRGCI3DG` | **ARST** | [anchors.stablex.org](anchors.stablex.org)
Stellar Mainnet	| `xlm:BRLT-GCHQ3F2BF5P74DMDNOOGHT5DUCKC773AW5DTOFINC26W4KGYFPYDPRSO` | **BRLT** | [anchors.stablex.org](anchors.stablex.org)

You can read more about the supported tokens [here](https://api.bitgo.com/docs/#section/Stellar-Tokens).

### Other Custodial Wallet

Using this approach you will need to implement a class which inherits from `polaris.integrations.CustodialIntegration` and override three functions:

- **get_distribution_account**: This function must return your wallet's public key.

- **get_distribution_seed**: This function must return your wallet's private key. **Note**: This is the private key used to sign the transaction on the Anchor side. Depending on your custodial solution it might be the private key of the supply account or the private key from a signer's account.

- **submit_transaction**: This function will submit the transaction to your Custodial Wallet provider. It must return `True` in case of success otherwise `False`. Also, you will need update some fields from the `Transaction` that you receive as a parameter. These fields are: 
  
  - **envelope_xdr**: [External Data Representation (XDR)](https://developers.stellar.org/docs/glossary/xdr/) is a standardized protocol that the Stellar network uses to encode data. After the transaction be sent to Stellar Network it generates a envelope XDR.
  - **paging_token**: A cursor value to use [pagination](https://developers.stellar.org/api/introduction/pagination/).
  - **stellar_transaction_id**: The transaction id from Stellar Network.
  - **status**: Depending on the state of the transaction, you can update it. But, we recommend after finishing everything, you must update to `completed` status.
  - **completed_at**: The moment when the transaction is finished.
  - **amount_out**: Amount that was sent to the user.
  - **pending_execution_attempt**: A boolean that identifies if the transaction was already processed.

  You can see how it was done for `BitGo`'s integration [here](). You can read more about transactions [here](https://developers.stellar.org/api/resources/transactions/object/)

```python
# integrations.py

from polaris.models import Asset, Transaction
from polaris.integrations.custodial import CustodialIntegration


class MyCustodialWalletIntegration(CustodialIntegration):
    def __init__(self):
        super().__init__()
        self.custodial_enabled = True
    
    def get_distribution_account(self, asset: Asset) -> str:
        # Here you will request your Custodial Wallet API to get the Wallet's Public Key.
        # This is the Public Key that will be shown as the supply account.
        # For example: GDBWZJVRRULO23HJQC7LXEZVAPR2OAR2BX2ZGV7QMV5H662H3UA7EQFZ
        ...
        return my_wallet_public_key

    def get_distribution_seed(self, asset: Asset) -> str:
        # Here you will request your Custodial Wallet API to get the Wallet's Private Key.
        # For example: SAZXK7VFNMCUCOA4V6PVXMRXBKJ3LWX7MRXPZINDO33U6MAMR4JHS3HH
        ...
        return my_wallet_public_key

    def submit_transaction(self, transaction: Transaction):
        # Here you will request your Custodial Wallet API to send the transaction to them.
        ...
        if not response.ok:
            return False

        # Proccess everything and update the transaction instance
        ...
        return True
```

After implementing your Custodial Wallet integration, you must register it to the `custodial` parameter on `register_integration` function. See the snippet below as an example:

```python
# apps.py

from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = "my_app"

    def ready(self):
        from polaris.integrations import register_integrations
        from .integrations import (
            ...
            MyCustodialWalletIntegration,
            MyRailsIntegration,
        )

        register_integrations(
            ...,
            rails=MyRailsIntegration(),
            custodial=MyCustodialWalletIntegration(),
        )
```

With this, you are to go to use your preferred Custodial Wallet as the anchor's supply account.

## Asset Model

On Polaris standard flow, when registering  your Asset on the database, its necessary to set the `distribution_seed` with the private key from the distribution account. To ensure that the integration works, you **must not fill `distribution_seed`**, as it would conflict with the implementation.

## Possible Issues

### BitGo's API Needs Unlock error

This error indicates the `access token` has reached it's spending limits and needs to be unlock. An unlock is required for protected wallet functions when the access token that you are using does not have any spending limits applied to the token.

We recommend to set a high value (up to `9223372036854775391` - the max value from Stellar Network) so this issue does not affect the integration. For further details see BitGo's official support documentation [here](https://bitgo.freshdesk.com/support/solutions/articles/27000051607-how-to-resolve-error-400-needs-unlock-when-trying-to-send-coins-via-the-api).

### BitGo's Trustline Error

This error indicates a trustline was not added for the tokenized asset on the BitGo's wallet.
