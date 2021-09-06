from polaris import settings as polaris_settings
from requests import Session
from requests.adapters import DEFAULT_POOLSIZE, HTTPAdapter
from rest_framework import status
from stellar_sdk.server import Server
from stellar_sdk.client.requests_client import (
    DEFAULT_BACKOFF_FACTOR,
    IDENTIFICATION_HEADERS,
    RequestsClient,
    USER_AGENT,
)
from urllib3.util import Retry


def get_stellar_network_transaction_info(
    transaction_id: str, num_retries: int = 5
) -> dict:
    """
    Gets the transaction's information from the Stellar Network.

    :param transaction_id: Stellar Network transaction id.
    :return: Returns a dict with all the information about the
    transaction that is registered on Stellar Network.
    """
    client = create_stellar_sdk_request_client(num_retries)
    with Server(horizon_url=polaris_settings.HORIZON_URI, client=client) as server:
        return server.transactions().transaction(transaction_id).call()


def create_stellar_sdk_request_client(num_retries: int = 5) -> RequestsClient:
    """
    Create a request client that should be used as the client
    for the Stellar SDK :class:`Server` instance.

    :param num_retries: The number of retries that the client
    should do when the response return the configured status
    codes
    :returns: Returns :class:`RequestsClient` instance.
    """
    # Adding 404 and 504 status code to force list.
    status_forcelist = tuple(Retry.RETRY_AFTER_STATUS_CODES) + (
        status.HTTP_404_NOT_FOUND,
        status.HTTP_504_GATEWAY_TIMEOUT,
    )
    retry = Retry(
        total=num_retries,
        backoff_factor=DEFAULT_BACKOFF_FACTOR,
        redirect=0,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET", "POST"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        pool_connections=DEFAULT_POOLSIZE,
        pool_maxsize=DEFAULT_POOLSIZE,
        max_retries=retry,
    )

    session = _create_request_session(adapter)

    return RequestsClient(session=session)


def _create_request_session(adapter: HTTPAdapter) -> Session:
    """
    Create a :class:`Session` instance for the given adapter.

    :param adapter: The request adapter with its configuration.
    :returns: Returns :class:`Session` instance.
    """
    headers = {**IDENTIFICATION_HEADERS, "User-Agent": USER_AGENT}

    session = Session()
    session.headers.update(headers)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
