from .Messages import HoppieMessage, ProgressMessage, PeekMessage, PollMessage, PingMessage, TelexMessage, AdscPeriodicContractRequestMessage, AdscContractCancellationMessage, AdscContractRejectionMessage, AdscPeriodicReportMessage, CpdlcMessage, HoppieMessageParser
from .Responses import ErrorResponse, SuccessResponse, PollSuccessResponse, PingSuccessResponse, PeekSuccessResponse
from .ADSC import AdscData
from .CPDLC import CpdlcResponseRequirement
from .API import HoppieAPI
from datetime import timedelta, time
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

    def send_adsc_periodic_request(self, to_name: str, interval: int) -> timedelta:
        """Send an ADS-C Periodic Contract Request to recipient station

        Args:
            to_name (str): Recipient station name
            interval (int): Reporting interval in seconds (0 = Demand Contract Request)

        Returns:
            timedelta: Response delay
        """
        return self._connect(AdscPeriodicContractRequestMessage(self._station, to_name, interval), SuccessResponse)[1]

    def send_adsc_periodic_report(self, to_name: str, data: AdscData) -> timedelta:
        """Send an ADS-C Periodic Report message to recipient station

        Args:
            to_name (str): Recipient station name
            data (AdscData): Report data

        Returns:
            timedelta: Response delay
        """
        return self._connect(AdscPeriodicReportMessage(self._station, to_name, data), SuccessResponse)[1]

    def send_adsc_cancel(self, to_name: str) -> timedelta:
        """Send an ADS-C Surveillance Contract cancellation message to recipient station

        Note:
            This message is sent by the ground station in order to cancel an existing ADS-C Periodic or Event contract.

        Args:
            to_name (str): Recipient station name

        Returns:
            timedelta: Response delay
        """
        return self._connect(AdscContractCancellationMessage(self._station, to_name), SuccessResponse)[1]

    def send_adsc_reject(self, to_name: str) -> timedelta:
        """Send an ADS-C Surveillance Contract rejection message to recipient station

        Note:
            This message is sent by the airborne station in order to reject an incoming ADS-C Surveillance Contract request.

        Args:
            to_name (str): Recipient station name

        Returns:
            timedelta: Response delay
        """
        return self._connect(AdscContractRejectionMessage(self._station, to_name), SuccessResponse)[1]

    def send_cpdlc(self, to_name: str, min: int, rr: CpdlcResponseRequirement, message: str, mrn: int | None = None) -> timedelta:
        """Send a CPDLC message to recipient station

        Note:
            Special restrictions regarding polling interval apply for airborne stations. See hoppie.nl docs.
            See CPDLC docs for further information about how to populate the data fields below.

        Args:
            to_name (str): Recipient station name
            min (int): Message Identification Number
            rr (CpdlcResponseRequirement): Response Requirement
            message (str): Message element
            mrn (int | None, optional): Message Reference Number. Defaults to None.

        Returns:
            timedelta: Response delay
        """
        return self._connect(CpdlcMessage(self._station, to_name, min, rr, message, mrn), SuccessResponse)[1]