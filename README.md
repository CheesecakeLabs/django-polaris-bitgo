# Django Polaris BitGo

Polaris BitGo is a Django app built to extend Polaris functionalities by providing the possibility of using the BitGo's custodial wallet as the anchor's supply account.

## Dependencies

- django-polaris >= 1.4.1
- pycryptodome == 3.10.1

## Installation

```shell
$ pip install django-polaris-bitgo
```

```python
# settings.py

INSTALLED_APPS = [
    ...
    # polaris dependencies
    "rest_framework",
    "corsheaders",
    "polaris",
    # polaris bitgo dependency
    "polaris_bitgo",
    ...
]
```

## How to use

### BitGo

To use the BitGo's wallet, it is necessary to import `BitGoIntegration` class from `polaris_bitgo.bitgo.integration` package and pass it as the `custody` parameter to Polaris' `register_integrations` function.

```python
# apps.py

from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = "my_app"

    def ready(self):
        from polaris.integrations import register_integrations
        from polaris_custodial.bitgo.integration import BitGoIntegration
        from .integrations import (
            ...
            MyRailsIntegration,
        )

        register_integrations(
            ...,
            rails=MyRailsIntegration(),
            custody=BitGoIntegration(
                api_url="https://app.bitgo-test.com",
                api_key="myapikey",
                api_passphrase="myapipassphrase",
                wallet_id="mywalletid",
                stellar_coin_code="txlm",
            ),
        )
```

The `BitGoIntegration` class has the following parameters:

- **api_url**: The BitGo's API base URL. Use `https://app.bitgo.com` for the production environment and `https://app.bitgo-test.com` for the test environment.
  
- **api_key**: The API Key for the BitGo account. It can be generated on your BitGo account by navigating to "Account Settings" -> "Developer Options" -> "Access Tokens". Here, click on the "+" button to add a token. On the following screen, fill in the information about the token that will be created.
  
   **Note**: We recommend to set a high value to `Lifetime Spending Limits` (up to `9223372036854775391` - the max value at the Stellar Network) so you won't have to unlock each transaction manually after reaching the limit.

    After filling in all the information, your form should look like this:

    Upon finishing it, you should receive your `API Key`.

- **api_passphrase**: The wallet-specific password to encrypt the user key at BitGo. This password is set when creating the wallet. You can change this password by clicking on "Wallets" -> Access your wallet -> "Settings". There will be a section where you can change the password.
  
- **wallet_id**: This information can be found by accessing your wallet and going to the "Settings" tab.
  
- **stellar_coin_code**: Use `xlm` for the production environment and `txlm` for the test environment.

**Note**: For improved security, we strongly recommend to add them to **Environment Variables** to keep them separated from the code.

After this you are ready to use BitGo as the supply account for your Anchor on the Stellar Network.

#### BitGo's Stellar supported tokens (assets)

| Environment     | Coin Type                                                           | Code     | Issuer Website                             |
| --------------- | ------------------------------------------------------------------- | -------- | ------------------------------------------ |
| Stellar Testnet | `txlm:BST-GBQTIOS3XGHB7LVYGBKQVJGCZ3R4JL5E4CBSWJ5ALIJUHBKS6263644L` | **BST**  |
| Stellar Mainnet | `xlm:VELO-GDM4RQUQQUVSKQA7S6EM7XBZP3FCGH4Q7CL6TABQ7B2BEJ5ERARM2M5M` | **VELO** | [velo.org](velo.org)                       |
| Stellar Mainnet | `xlm:SLT-GCKA6K5PCQ6PNF5RQBF7PQDJWRHO6UOGFMRLK3DYHDOI244V47XKQ4GP`  | **SLT**  | [smartlands.io](smartlands.io)             |
| Stellar Mainnet | `xlm:USD-GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX`  | **USD**  | [anchorusd.com](anchorusd.com)             |
| Stellar Mainnet | `xlm:ETH-GBVOL67TMUQBGL4TZYNMY3ZQ5WGQYFPFD5VJRWXR72VA33VFNL225PL5`  | **ETH**  | [stellarport.io](stellarport.io)           |
| Stellar Mainnet | `xlm:WXT-GASBLVHS5FOABSDNW5SPPH3QRJYXY5JHA2AOA2QHH2FJLZBRXSG4SWXT`  | **WXT**  | [wxt.wirexapp.com](wxt.wirexapp.com)       |
| Stellar Mainnet | `xlm:USDC-GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` | **USDC** | [centre.io](centre.io)                     |
| Stellar Mainnet | `xlm:SIX-GDMS6EECOH6MBMCP3FYRYEVRBIV3TQGLOFQIPVAITBRJUMTI6V7A2X6Z`  | **SIX**  | [six.network](six.network)                 |
| Stellar Mainnet | `xlm:ARST-GCSAZVWXZKWS4XS223M5F54H2B6XPIIXZZGP7KEAIU6YSL5HDRGCI3DG` | **ARST** | [anchors.stablex.org](anchors.stablex.org) |
| Stellar Mainnet | `xlm:BRLT-GCHQ3F2BF5P74DMDNOOGHT5DUCKC773AW5DTOFINC26W4KGYFPYDPRSO` | **BRLT** | [anchors.stablex.org](anchors.stablex.org) |

You can read more about the supported tokens [here](https://api.bitgo.com/docs/#section/Stellar-Tokens).

## Asset Model

On Polaris standard flow, when registering your Asset on the database, it's necessary to set the `distribution_seed` with the private key from the distribution account. To ensure that the BitGo's integration works, you **must not fill `distribution_seed`**, as it would conflict with the implementation.

## Possible Issues

### BitGo's API Needs Unlock error

This error indicates that the `access token` has reached it's spending limits and needs to be unlocked. An unlock is required for protected wallet functions when the access token that you are using does not have any spending limits applied to the token.

We recommend to set a high value (up to `9223372036854775391` - the max value at the Stellar Network) so this issue does not affect the integration. For further details, see BitGo's official support documentation [here](https://bitgo.freshdesk.com/support/solutions/articles/27000051607-how-to-resolve-error-400-needs-unlock-when-trying-to-send-coins-via-the-api).

### BitGo's Trustline Error

This error indicates that a trustline was not added for the tokenized asset on the BitGo's wallet.
