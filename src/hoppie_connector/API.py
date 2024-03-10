from .Messages import HoppieMessage
from .Responses import HoppieResponse, HoppieResponseParser
import requests

class HoppieAPI(object):
    def __init__(self, logon: str, url: str = 'http://www.hoppie.nl/acars/system/connect.html'):
        self._url = url
        self._logon = logon

    def connect(self, msg: HoppieMessage) -> HoppieResponse:
        params = { 'logon': self._logon }
        params.update(msg.get_msg_params())

        req = requests.get(self._url, params)
        if not req.ok: raise ConnectionError(f"Error {req.status_code}: {req.reason}")

        response = req.content.decode('ascii')
        return HoppieResponseParser().parse(response)
