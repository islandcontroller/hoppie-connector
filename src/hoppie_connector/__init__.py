from .Messages import HoppieMessage, HoppieMessageFactory
from .Responses import ErrorResponse, SuccessResponse, PeekSuccessResponse, PollSuccessResponse
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

    def _connect(self, message: HoppieMessage) -> SuccessResponse:
        response = self._api.connect(message)
        if isinstance(response, ErrorResponse): 
            raise HoppieError(response.get_reason())
        return response

    def peek(self) -> list[tuple[int, HoppieMessage]]:
        """Peek all messages destined to own station

        Note:
            Own station will not appear as 'online'. Peeked messages will not
            be marked as relayed. Message history is kept on the server for up 
            to 24 hours.

        Returns:
            list[tuple[int, HoppieMessage]]: List of messages (id, content)
        """
        response: PeekSuccessResponse = self._connect(self._f.create_peek())
        result = []
        for d in response.get_data():
            try:
                result.append((d['id'], self._f.create_from_data(d)))
            except ValueError as e:
                warnings.warn(f"Unable to parse {d}: {e}", HoppieWarning)
        return result

    def poll(self) -> list[HoppieMessage]:
        """Poll for new messages destined to own station and mark them as relayed.

        Note:
            Polling will make the own station name appear as 'online' and mark
            received messages as 'relayed'. Previously relayed messages will 
            not reappear in the next `poll` response.

        Returns:
            list[HoppieMessage]: List of messages
        """
        response: PollSuccessResponse = self._connect(self._f.create_poll())
        result = []
        for d in response.get_data():
            try:
                result.append(self._f.create_from_data(d))
            except ValueError as e:
                warnings.warn(f"Unable to parse {d}: {e}", HoppieWarning)
        return result

    def send_telex(self, to_name: str, message: str) -> None:
        """Send a freetext message to recipient station.

        Note:
            Message length is limited to 220 characters by ACARS specification.

        Args:
            to_name (str): Recipient station name
            message (str): Message content
        """
        self._connect(self._f.create_telex(to_name, message))