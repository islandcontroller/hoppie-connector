from .Messages import HoppieMessage, HoppieMessageFactory
from .Responses import ErrorResponse, SuccessResponse
from .API import HoppieAPI
import warnings

class HoppieError(Exception): pass
class HoppieWarning(UserWarning): pass

class HoppieConnector(object):
    def __init__(self, station_name: str, logon: str):
        self._f = HoppieMessageFactory(station_name)
        self._api = HoppieAPI(logon)

    def _get_data_from_response(self, response: SuccessResponse) -> list[tuple[int, HoppieMessage]]:
        result = []
        for item_data in response.items:
            try:
                id, msg = self._f.create_from_data(item_data)
                result.append((id, msg))
            except ValueError as e:
                warnings.warn(f"Unable to parse {item_data}: {e}", HoppieWarning)
        return result

    def _connect(self, message: HoppieMessage) -> list[tuple[int, HoppieMessage]]:
        response = self._api.connect(message)

        if isinstance(response, ErrorResponse): 
            raise HoppieError(response.get_reason())
        elif isinstance(response, SuccessResponse):
            return self._get_data_from_response(response)
        else:
            raise NotImplementedError()

    def peek(self) -> list[tuple[int, HoppieMessage]]:
        return self._connect(self._f.create_peek())

    def poll(self) -> list[tuple[int, HoppieMessage]]:
        return self._connect(self._f.create_poll())
    
    def send_telex(self, to_name: str, message: str) -> None:
        self._connect(self._f.create_telex(to_name, message))