from polaris import settings as polaris_settings


def get_stellar_network_transaction_info(transaction_id: str) -> dict:
    """
    Gets the transaction's information from the Stellar Network.

    :param transaction_id: Stellar Network transaction id.
    :return: Returns a dict with all the information about the
    transaction that is registered on Stellar Network.
    """
    return (
        polaris_settings.HORIZON_SERVER.transactions()
        .transaction(transaction_id)
        .call()
    )
