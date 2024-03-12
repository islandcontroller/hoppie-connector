from .Messages import HoppieMessage, HoppieMessageFactory
from .Responses import ErrorResponse, SuccessResponse
from .API import HoppieAPI
import warnings

class HoppieError(Exception): pass
class HoppieWarning(UserWarning): pass

class HoppieConnector(object):
    """HoppieConnector(station_name, logon)

    Connector for interacting with Hoppie's ACARS service.
    """
    def __init__(self, station_name: str, logon: str):
        """Create a new connector

        Note:
            Station name must be a valid ICAO flight number or 3-letter org code.

        Args:
            station_name (str): Own station name
            logon (str): API logon code
        """
        self._f = HoppieMessageFactory(station_name)
        self._api = HoppieAPI(logon)

    def _get_data_from_response(self, response: SuccessResponse) -> list[tuple[int, HoppieMessage]]:
        result = []
        for item_data in response.get_items():
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
        """Peek all messages destined to own station

        Note:
            Own station will not appear as 'online'. Peeked messages will not
            be marked as relayed. Message history is kept on the server for up 
            to 24 hours.

        Returns:
            list[tuple[int, HoppieMessage]]: List of messages (id, content)
        """
        return self._connect(self._f.create_peek())

    def poll(self) -> list[tuple[int, HoppieMessage]]:
        """Poll for new messages destined to own station and mark them as relayed.

        Note:
            Polling will make the own station name appear as 'online' and mark
            received messages as 'relayed'. Previously relayed messages will 
            not reappear in the next `poll` response.

        Returns:
            list[tuple[int, HoppieMessage]]: List of messages (id, content)
        """
        return self._connect(self._f.create_poll())
    
    def send_telex(self, to_name: str, message: str) -> None:
        """Send a freetext message to recipient station.

        Note:
            Message length is limited to 220 characters by ACARS specification.

        Args:
            to_name (str): Recipient station name
            message (str): Message content
        """
        self._connect(self._f.create_telex(to_name, message))