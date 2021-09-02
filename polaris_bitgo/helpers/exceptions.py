from requests.exceptions import HTTPError


class BitGoAPIError(HTTPError):
    pass


class BitGoKeyInfoNotFound(Exception):
    pass
