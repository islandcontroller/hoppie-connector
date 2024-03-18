from .Messages import HoppieMessage
from .Responses import HoppieResponse, HoppieResponseParser
import requests

class HoppieAPI(object):
    """HoppieAPI(logon[, url])
    
    Hoppie API connection
    """
    _DEFAULT_URL: str = 'https://www.hoppie.nl/acars/system/connect.html'

    def __init__(self, logon: str, url: str | None = None):
        """Prepare new API connection

        Args:
            logon (str): Logon code
            url (str, optional): API URL. Defaults to None.
        """
        self._url = url if url is not None else self._DEFAULT_URL
        self._logon = logon

    def connect(self, msg: HoppieMessage) -> HoppieResponse:
        """Issue "connect" call to the API

        Args:
            msg (HoppieMessage): Message data

        Returns:
            HoppieResponse: Response data (ASCII string encoding)
        """
        match msg.get_msg_type():
            case HoppieMessage.MessageType.TELEX:
                params = msg.get_msg_params()
                data = params.pop('packet')
                response = requests.post(self._url, params={'logon': self._logon, **params}, data={'packet': data})
            case _:
                response = requests.get(self._url, params={'logon': self._logon, **msg.get_msg_params()})
        if not response.ok: raise ConnectionError(f"Error {response.status_code}: {response.reason}")
        
        content = response.content.decode('ascii')
        return HoppieResponseParser().parse(content)
