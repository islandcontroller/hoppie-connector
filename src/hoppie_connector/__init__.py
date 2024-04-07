from .Messages import HoppieMessage, ProgressMessage, PeekMessage, PollMessage, PingMessage, TelexMessage, AdscMessage, HoppieMessageParser
from .Responses import ErrorResponse, SuccessResponse, PollSuccessResponse, PingSuccessResponse, PeekSuccessResponse
from .API import HoppieAPI
from datetime import timedelta, time, datetime
from typing import TypeVar
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
        self._station = station_name
        self._api = HoppieAPI(logon, url)

    _T = TypeVar('_T')
    def _connect(self, message: HoppieMessage, type: _T) -> tuple[_T, timedelta]:
        response, delay = self._api.connect(message)
        if isinstance(response, ErrorResponse): 
            raise HoppieError(response.get_reason())
        elif isinstance(response, type):
            return response, delay
        else:
            raise TypeError('Response can not be represented by requested target type')

    def peek(self) -> tuple[list[tuple[int, HoppieMessage]], timedelta]:
        """Peek all messages destined to own station

        Note:
            Own station will not appear as 'online'. Peeked messages will not
            be marked as relayed. Message history is kept on the server for up 
            to 24 hours.

        Returns:
            tuple[list[tuple[int, HoppieMessage]], timedelta]: List of messages (id, content) and reponse delay
        """
        response, delay = self._connect(PeekMessage(self._station), PeekSuccessResponse)
        result = []
        p = HoppieMessageParser(self._station)
        for d in response.get_data():
            try:
                result.append((d['id'], p.parse(d)))
            except ValueError as e:
                warnings.warn(f"Unable to parse {d}: {e}", HoppieWarning)
        return result, delay

    def poll(self) -> tuple[list[HoppieMessage], timedelta]:
        """Poll for new messages destined to own station and mark them as relayed.

        Note:
            Polling will make the own station name appear as 'online' and mark
            received messages as 'relayed'. Previously relayed messages will 
            not reappear in the next `poll` response.

        Returns:
            tuple[list[HoppieMessage], timedelta]: List of messages and response delay
        """
        response, delay = self._connect(PollMessage(self._station), PollSuccessResponse)
        result = []
        p = HoppieMessageParser(self._station)
        for d in response.get_data():
            try:
                result.append(p.parse(d))
            except ValueError as e:
                warnings.warn(f"Unable to parse {d}: {e}", HoppieWarning)
        return result, delay

    def ping(self, stations: list[str] | str | None = None) -> tuple[list[str], timedelta]:
        """Check station online status.

        Note:
            Use `stations='*'` in order to retrieve a list of all currently online stations.
            An empty argument can serve as a connection check to the API server.

        Args:
            stations (list[str] | str | None, optional): List of stations to check. Defaults to None.

        Returns:
            tuple[list[str], timedelta]: List of online stations and response delay
        """
        response, delay = self._connect(PingMessage(self._station, stations), PingSuccessResponse)
        return response.get_stations(), delay

    def send_telex(self, to_name: str, message: str) -> timedelta:
        """Send a freetext message to recipient station.

        Note:
            Message length is limited to 220 characters by ACARS specification.

        Args:
            to_name (str): Recipient station name
            message (str): Message content

        Returns:
            timedelta: Response delay
        """
        return self._connect(TelexMessage(self._station, to_name, message), SuccessResponse)[1]

    def send_progress(self, to_name: str, dep: str, arr: str, time_out: time, time_eta: time | None = None, time_off: time | None = None, time_on: time | None = None, time_in: time | None = None) -> timedelta:
        """Send an OOOI progress report to recipient station

        Note:
            ETA only available until IN time is specified.

        Args:
            to_name (str): Recipient station name
            dep (str): Departure airport ICAO code
            arr (str): Arrival airport ICAO code
            time_out (time): OUT time
            time_eta (time | None, optional): Estimated time of arrival. Defaults to None.
            time_off (time | None, optional): OFF time. Defaults to None.
            time_on (time | None, optional): ON time. Defaults to None.
            time_in (time | None, optional): IN time. Defaults to None.

        Returns:
            timedelta: Response delay
        """
        return self._connect(ProgressMessage(self._station, to_name, dep, arr, time_out, time_eta, time_off, time_on, time_in), SuccessResponse)[1]

    def send_adsc(self, to_name: str, report_time: datetime, position: tuple[float, float], altitude: float, heading: float | None = None, remark: str | None = None):
        """Send an ADS-C position report to recipient station

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            report_time (datetime): Date and time of report
            position (tuple[float, float]): Position (lat, lon)
            altitude (float): Altitude in feet
            heading (float | None, optional): Heading in degrees. Defaults to None.

        Returns:
            timedelta: Response delay
        """
        return self._connect(AdscMessage(self._station, to_name, report_time, position, altitude, heading), SuccessResponse)[1]