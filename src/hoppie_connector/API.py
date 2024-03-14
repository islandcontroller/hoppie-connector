from .Messages import HoppieMessage
from .Responses import HoppieResponse, HoppieResponseParser
import requests

class HoppieAPI(object):
    """HoppieAPI(logon[, url])
    
    Hoppie API connection
    """
    def __init__(self, logon: str, url: str = 'https://www.hoppie.nl/acars/system/connect.html'):
        """Prepare new API connection

        Args:
            logon (str): Logon code
            url (str, optional): API URL. Defaults to 'https://www.hoppie.nl/acars/system/connect.html'.
        """
        self._url = url
        self._logon = logon

    def connect(self, msg: HoppieMessage) -> HoppieResponse:
        """Issue "connect" call to the API

        Args:
            msg (HoppieMessage): Message data

        Returns:
            HoppieResponse: Response data (ASCII string encoding)
        """
        params = { 'logon': self._logon }
        params.update(msg.get_msg_params())

        req = requests.get(self._url, params)
        if not req.ok: raise ConnectionError(f"Error {req.status_code}: {req.reason}")

        response = req.content.decode('ascii')
        return HoppieResponseParser().parse(response)
