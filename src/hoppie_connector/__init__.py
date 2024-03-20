from .Messages import HoppieMessage, HoppieMessageFactory
from .Responses import ErrorResponse, SuccessResponse
from .API import HoppieAPI
import warnings

class HoppieError(Exception):
    pass
class HoppieWarning(UserWarning):
    pass

class HoppieConnector(object):
    """HoppieConnector(station_name, logon)

    Connector for interacting with Hoppie's ACARS service.
    """
    def __init__(self, station_name: str, logon: str, url: str | None = None):
        """Create a new connector

        Note:
            Station name must be a valid ICAO flight number or 3-letter org code.

        Args:
            station_name (str): Own station name
            logon (str): API logon code
            url (str, optional): API URL. Defaults to None.
        """
        self._f = HoppieMessageFactory(station_name)
        self._api = HoppieAPI(logon, url)

    def _get_data_from_response(self, response: SuccessResponse) -> list[tuple[int | None, HoppieMessage]]:
        if not isinstance(response, SuccessResponse):
            raise ValueError('Invalid response data type')
        else:
            result = []
            for item_data in response.get_items():
                try:
                    id, msg = self._f.create_from_data(item_data)
                    result.append((id, msg))
                except ValueError as e:
                    warnings.warn(f"Unable to parse {item_data}: {e}", HoppieWarning)
            return result

    def _connect(self, message: HoppieMessage) -> list[tuple[int | None, HoppieMessage]]:
        response = self._api.connect(message)

        if isinstance(response, ErrorResponse): 
            raise HoppieError(response.get_reason())
        
        return self._get_data_from_response(response)

    def peek(self) -> list[tuple[int | None, HoppieMessage]]:
        """Peek all messages destined to own station

        Note:
            Own station will not appear as 'online'. Peeked messages will not
            be marked as relayed. Message history is kept on the server for up 
            to 24 hours.

        Returns:
            list[tuple[int | None, HoppieMessage]]: List of messages (id, content)
        """
        return self._connect(self._f.create_peek())

    def poll(self) -> list[HoppieMessage]:
        """Poll for new messages destined to own station and mark them as relayed.

        Note:
            Polling will make the own station name appear as 'online' and mark
            received messages as 'relayed'. Previously relayed messages will 
            not reappear in the next `poll` response.

        Returns:
            list[HoppieMessage]: List of messages
        """
        return [data[1] for data in self._connect(self._f.create_poll())]
    
    def send_telex(self, to_name: str, message: str) -> None:
        """Send a freetext message to recipient station.

        Note:
            Message length is limited to 220 characters by ACARS specification.

        Args:
            to_name (str): Recipient station name
            message (str): Message content
        """
        self._connect(self._f.create_telex(to_name, message))