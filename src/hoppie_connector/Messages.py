from .ADSC import AdscData, BasicGroup, FlightIdentGroup, EarthRefGroup, MeteoGroup
from .CPDLC import CpdlcResponseRequirement
from .Utilities import is_valid_station_name, is_valid_airport_code, get_fixed_width_float_str, ICAO_AIRPORT_REGEX, STATION_NAME_REGEX
from datetime import datetime, time, UTC
from typing import Self
import enum
import re

class HoppieMessage(object):
    """HoppieMessage(from_name, to_name, type)
    
    Abstract base message object
    """
    class MessageType(enum.StrEnum):
        ADS_C = 'ads-c'
        PROGRESS = 'progress'
        TELEX = 'telex'
        POLL = 'poll'
        PEEK = 'peek'
        PING = 'ping'
        CPDLC = 'cpdlc'

        def __repr__(self) -> str:
            return f"HoppieMessage.MessageType.{self.name}"

    def __init__(self, from_name: str, to_name: str, type: MessageType):
        """Create base message object

        Note:
            `from_name` and `to_name` must be valid station names (ICAO flight
            number, 3-letter org code or special station names)

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            type (MessageType): Message type code
        """
        if not isinstance(type, self.MessageType):
            raise ValueError('Invalid message type')
        elif not is_valid_station_name(from_name):
            raise ValueError('Invalid FROM station name')
        elif not is_valid_station_name(to_name):
            raise ValueError('Invalid TO station name')
        else:
            self._from = from_name
            self._to = to_name
            self._type = type

    def get_from_name(self) -> str:
        """Return sender station name
        """
        return self._from

    def get_to_name(self) -> str:
        """Return recipient station name
        """
        return self._to

    def get_msg_type(self) -> MessageType:
        """Return message type code
        """
        return self._type

    def get_packet_content(self) -> str:
        """Return encoded packet content
        """
        return ''

    def get_msg_params(self) -> dict:
        """Return collated metadata
        """
        return {
            'from': self.get_from_name(),
            'to': self.get_to_name(),
            'type': self.get_msg_type().value,
            'packet': self.get_packet_content()
        }

    def __str__(self) -> str:
        return f"{self.get_from_name()} -> {self.get_to_name()} [{self.get_msg_type().name}] {self.get_packet_content()}"

    def __repr__(self) -> str:
        return f"HoppieMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, type={self.get_msg_type()!r})"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, HoppieMessage) and (self.get_msg_params() == __value.get_msg_params())

class PeekMessage(HoppieMessage): 
    """PeekMessage()
    
    Retrieve messages without appearing online or marking them as relayed.
    """
    def __init__(self, from_name: str):
        """Create "peek"-message

        Args:
            from_name (str): Sender station name
        """
        super().__init__(from_name, 'SERVER', self.MessageType.PEEK)

    def __repr__(self) -> str:
        return f"PeekMessage(from_name={self.get_from_name()!r})"

class PollMessage(HoppieMessage):
    """PollMessage()
    
    Retrieve unread messages and mark station as 'online'.
    """
    def __init__(self, from_name: str):
        """Create "poll"-message

        Args:
            from_name (str): Sender station name
        """
        super().__init__(from_name, 'SERVER', self.MessageType.POLL)

    def __repr__(self) -> str:
        return f"PollMessage(from_name={self.get_from_name()!r})"

class TelexMessage(HoppieMessage):
    """TelexMessage(from_name, to_name, message)

    Freetext ACARS message
    """
    _TELEX_MAX_MSG_LEN: int = 220

    @classmethod
    def from_packet(cls, from_name: str, to_name: str, packet: str) -> Self:
        """Parse freetext message from packet string

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            packet (str): Packet string
        """
        return TelexMessage(from_name, to_name, packet)

    def __init__(self, from_name: str, to_name: str, message: str):
        """Create a freetext message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            message (str): Message content
        """
        if len(message) > self._TELEX_MAX_MSG_LEN: 
            raise ValueError('Message too long')
        elif not message.isascii():
            raise ValueError('Message contains non-ASCII characters')
        else:
            super().__init__(from_name, to_name, self.MessageType.TELEX)
            self._message = message

    def get_message(self) -> str:
        """Return freetext message content
        """
        return self._message

    def get_packet_content(self) -> str:
        return self._message.upper()

    def __repr__(self) -> str:
        return f"TelexMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, message={self.get_message()!r})"

class ProgressMessage(HoppieMessage):
    """ProgressMessage(from_name, to_name, dep, arr, time_out[, time_eta[, time_off[, time_on[, time_in]]]])
    
    ACARS OOOI (Out-off-on-in) Report
    """

    @classmethod
    def from_packet(cls, from_name: str, to_name: str, packet: str) -> Self:
        """Parse progress message from packet string

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            packet (str): Packet string
        """
        def _get_aprt(packet: str) -> tuple[str, str] | None:
            m = re.match(r'^(' + ICAO_AIRPORT_REGEX + r')\/(' + ICAO_AIRPORT_REGEX + r')', packet)
            if not m:
                raise ValueError('Invalid dep/arr value')
            else:
                return m.group(1), m.group(2)

        def _get_time(timestr: str) -> time:
            return datetime.strptime(timestr, '%H%M').replace(tzinfo=UTC).timetz()

        def _get_time_out(packet: str) -> time | None:
            m = re.search(r'OUT\/(\d{4})Z?', packet)
            if not m:
                raise ValueError('Invalid OUT value')
            else:
                return _get_time(m.group(1))

        def _get_time_off(packet: str) -> time | None:
            m = re.search(r'OFF\/(\d{4})Z?', packet)
            if not m:
                return None
            else:
                return _get_time(m.group(1))

        def _get_eta(packet: str) -> time | None:
            m = re.search(r'ETA\/(\d{4})Z?', packet)
            if not m:
                return None
            else:
                return _get_time(m.group(1))

        def _get_time_on(packet: str) -> time | None:
            m = re.search(r'ON\/(\d{4})Z?', packet)
            if not m:
                return None
            else: 
                return _get_time(m.group(1))

        def _get_time_in(packet: str) -> time | None:
            m = re.search(r'IN\/(\d{4})Z?', packet)
            if not m:
                return None
            else:
                return _get_time(m.group(1))

        dep, arr = _get_aprt(packet)
        time_out = _get_time_out(packet)
        time_off = _get_time_off(packet)
        time_on = _get_time_on(packet)
        time_in = _get_time_in(packet)
        time_eta = _get_eta(packet)

        return ProgressMessage(from_name, to_name, dep, arr, time_out, time_eta, time_off, time_on, time_in)

    def __init__(self, from_name: str, to_name: str, dep: str, arr: str, time_out: time, time_eta: time | None = None, time_off: time | None = None, time_on: time | None = None, time_in: time | None = None):
        """Create a progress message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            dep (str): Departure airport ICAO code
            arr (str): Destination/Arrival airport ICAO code
            time_out (time): OUT time
            time_eta (time | None, optional): Estimated time of arrival. Defaults to None.
            time_off (time | None, optional): OFF time. Defaults to None.
            time_on (time | None, optional): ON time. Defaults to None.
            time_in (time | None, optional): IN time. Defaults to None.
        """
        if not is_valid_airport_code(dep):
            raise ValueError('Invalid departure identifier')
        elif not is_valid_airport_code(arr):
            raise ValueError('Invalid arrival identifier')
        elif not time_out:
            raise ValueError('Missing OUT time')
        elif time_on and not time_off:
            raise ValueError('Missing OFF time')
        elif time_in and not time_on: 
            raise ValueError('Missing ON time')
        elif time_eta and time_in:
            raise ValueError('Invalid ETA after arrival specified')
        else:
            super().__init__(from_name, to_name, self.MessageType.PROGRESS)
            self._dep = dep
            self._arr = arr
            self._out = time_out
            self._off = time_off
            self._on = time_on
            self._in = time_in
            self._eta = time_eta

    def get_departure(self) -> str:
        """Return departure airport code
        """
        return self._dep

    def get_arrival(self) -> str:
        """Return arrival airport code
        """
        return self._arr

    def get_time_out(self) -> time:
        """Return OUT time
        """
        return self._out

    def get_time_off(self) -> time | None:
        """Return OFF time if specified
        """
        return self._off

    def get_time_on(self) -> time | None:
        """Return ON time if specified
        """
        return self._on

    def get_time_in(self) -> time | None:
        """Return IN time if specified
        """
        return self._in

    def get_eta(self) -> time | None:
        """Return ETA if specified
        """
        return self._eta

    def get_packet_content(self) -> str:
        def _get_utc(t: time) -> time: 
            offset = t.utcoffset()
            if not offset:
                return t
            else:
                adjusted = datetime.combine(datetime.today(), t) - offset
                return adjusted.time()

        packet = f"{self._dep}/{self._arr} OUT/{_get_utc(self._out):%H%M}"
        if self._off: 
            packet += f" OFF/{_get_utc(self._off):%H%M}"
        if self._on: 
            packet += f" ON/{_get_utc(self._on):%H%M}"
        if self._in: 
            packet += f" IN/{_get_utc(self._in):%H%M}"
        if self._eta: 
            packet += f" ETA/{_get_utc(self._eta):%H%M}"
        return packet

    def __repr__(self) -> str:
        return f"ProgressMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, dep={self.get_departure()!r}, arr={self.get_arrival()!r}, time_out={self.get_time_out()!r}, time_eta={self.get_eta()!r}, time_off={self.get_time_off()!r}, time_on={self.get_time_on()!r}, time_in={self.get_time_in()!r})"

class AdscMessage(HoppieMessage):
    """AdscMessage(from_name, to_name, adsc_msg_type)
    
    ADS-C message base class
    """
    
    class AdscMessageType(enum.StrEnum):
        REQUEST_PERIODIC = 'REQUEST PERIODIC'
        REQUEST_CANCEL = 'REQUEST CANCEL'
        REPORT_PERIODIC = 'REPORT'
        REJECT = 'REJECT'

        def __repr__(self) -> str:
            return f"AdscMessage.AdscMessageType({self.value!r})"

    def __init__(self, from_name: str, to_name: str, adsc_msg_type: AdscMessageType):
        """Create base Surveillance Contract Request message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            adsc_msg_type (AdscMessageType): ADS-C message subtype
        """
        super().__init__(from_name, to_name, HoppieMessage.MessageType.ADS_C)
        self._adsc_msg_type = adsc_msg_type

    def get_adsc_msg_type(self) -> AdscMessageType:
        """Return message subtype
        """
        return self._adsc_msg_type
    
    def get_adsc_data_packet(self) -> str:
        """Get encoded ADS-C data part of the packet
        """
        return ''

    def get_packet_content(self) -> str:
        return self.get_adsc_msg_type() + (f" {self.get_adsc_data_packet()}" if len(self.get_adsc_data_packet()) > 0 else '')

    def __repr__(self) -> str:
        return f"AdscMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, adsc_msg_type={self.get_adsc_msg_type()!r})"

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value) and isinstance(__value, AdscMessage) and (__value.get_adsc_msg_type() == self.get_adsc_msg_type())

class AdscPeriodicContractRequestMessage(AdscMessage):
    """AdscPeriodicContractRequestMessage(from_name, to_name, interval)

    ADS-C Periodic Contract Request message
    """

    @classmethod
    def from_packet(cls, from_name: str, to_name: str, packet: str) -> Self:
        """Parse Periodic Contract Request message from packet string

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            packet (str): Packet string
        """
        m = re.match(AdscMessage.AdscMessageType.REQUEST_PERIODIC + r'\s(\d+)', packet)
        if not m:
            raise ValueError('Invalid ADS-C contract request format')
        
        interval = int(m.group(1), base=10)
        return AdscPeriodicContractRequestMessage(from_name, to_name, interval)

    def __init__(self, from_name: str, to_name: str, interval: int):
        """Create Periodic Contract Request message

        Note:
            Reporting interval should be greater than minimum polling interval.

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            interval (int): Reporting interval in seconds (0 = Demand Contract Request)
        """
        if interval < 0:
            raise ValueError('Report interval must be a positive integer')
        super().__init__(from_name, to_name, AdscMessage.AdscMessageType.REQUEST_PERIODIC)
        self._interval = interval

    def is_demand_contract_request(self) -> bool:
        """Check if this request is a Demand Contract Request

        Note:
            Interval value returned by `get_interval()` should be ignored for Demand Contract Requests.
        """
        return self._interval == 0

    def get_interval(self) -> int:
        """Return reporting interval in unit of seconds

        Note:
            Value must be ignored for Demand Contract Requests. See: `is_demand_contract_request()`.
            In general, the reporting intervall should not be shorter than the minimum polling interval.
        """
        return self._interval

    def get_adsc_data_packet(self) -> str:
        return f"{self.get_interval():0d}"

    def __repr__(self) -> str:
        return f"AdscPeriodicContractRequestMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, interval={self.get_interval()!r})"

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value) and isinstance(__value, AdscPeriodicContractRequestMessage) and (__value.get_interval() == self.get_interval())

class AdscPeriodicReportMessage(AdscMessage):
    """AdscPeriodicReportMessage(from_name, to_name, data)
    
    ADC-C Periodic Report message
    """

    @classmethod
    def from_packet(cls, from_name: str, to_name: str, packet: str) -> Self:
        """Parse ADS-C periodic report from packet string

        Args:
            from_name (str): Sender station name
            to_name (str): Recipipent station name
            packet (str): Packet string
        """
        m = re.match(AdscMessage.AdscMessageType.REPORT_PERIODIC + r'\s(' + STATION_NAME_REGEX + r')\s(\d{6})\s(\-?\d{1,2}\.\d{4,6})\s(\-?\d{1,3}\.\d{3,6})\s(\d{1,5})' + \
                     r'(?:\s(\d{3})\s(\d{1,3})' + \
                        r'(?:\s(\d{3})\/(\d{1,3})\s(\-?\d{1,3})' + \
                            r'(?:\s(DES|LVL|CLB))?' + \
                        r')?' + \
                     r')?', 
                     packet)
        if not m:
            raise ValueError('Invalid ADS-C Periodic Report message format')

        # Parse fields and create groups
        acft_ident = m.group(1)
        flight_ident_group = FlightIdentGroup(acft_ident)

        timestamp = datetime.strptime(m.group(2), r'%d%H%M').replace(tzinfo=UTC)
        position = (float(m.group(3)), float(m.group(4)))
        altitude = 1.0 * int(m.group(5), base=10)
        basic_group = BasicGroup(timestamp, position, altitude)

        meteo_group = None
        earth_ref_group = None

        if (m.group(6) is not None) and (m.group(7) is not None):
            true_track = 1.0 * int(m.group(6), base=10)
            ground_speed = 1.0 * int(m.group(7), base=10)
            earth_ref_group = EarthRefGroup(true_track, ground_speed, None)

            if (m.group(8) is not None) and (m.group(9) is not None) and (m.group(10) is not None):
                wind_dir = 1.0 * int(m.group(8), base=10)
                wind_spd = 1.0 * int(m.group(9), base=10)
                temperature = 1.0 * int(m.group(10), base=10)
                meteo_group = MeteoGroup((wind_dir, wind_spd), temperature)

                if m.group(11) is not None:
                    vertical_rate = m.group(11)
                    earth_ref_group.vertical_rate = vertical_rate

        data = AdscData(basic_group, flight_ident_group, earth_ref_group, meteo_group)
        return AdscPeriodicReportMessage(from_name, to_name, data)

    def __init__(self, from_name: str, to_name: str, data: AdscData):
        """Create ADS-C Periodic Report message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            data (AdscGroupCollection): ADS-C data groups
        """
        super().__init__(from_name, to_name, AdscMessage.AdscMessageType.REPORT_PERIODIC)
        self._data = data

    def get_data(self) -> AdscData:
        """Return ADS-C group data

        Note:
            Month and year information of BasicGroup must be ignored
        """
        return self._data

    def get_adsc_data_packet(self) -> str:
        # REPORT <acft_ident> <timestamp> <latitude> <longitude> <altitude> [<true_track> <ground_speed> [<wind_dir/wind_speed> <temperature> [<vertical_rate>]]]
        packet = f"{self._data.flight_ident.acft_ident}" \
                 f" {self._data.basic.timestamp.astimezone(UTC):%d%H%M}" \
                 f" {get_fixed_width_float_str(self._data.basic.position[0], 8)}" \
                 f" {get_fixed_width_float_str(self._data.basic.position[1], 8)}" \
                 f" {(self._data.basic.altitude):.0f}"
        if self._data.earth_ref is not None:
            packet += f" {self._data.earth_ref.true_track:03.0f}" \
                      f" {self._data.earth_ref.ground_speed:.0f}"
            if self._data.meteo is not None:
                packet += f" {self._data.meteo.wind[0]:03.0f}/{self._data.meteo.wind[1]:.0f}" \
                          f" {self._data.meteo.temperature:.0f}"
                if self._data.earth_ref.vertical_rate is not None:
                    packet += f" {self._data.earth_ref.vertical_rate}"
        return packet

    def __repr__(self) -> str:
        return f"AdscPeriodicReportMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, data={self.get_data()!r})"

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value) and isinstance(__value, AdscPeriodicReportMessage) and (__value.get_data() == self.get_data())

class AdscContractCancellationMessage(AdscMessage):
    """AdscContractCancellationMessage(from_name, to_name)
    
    ADS-C Surveillance Contract Cancellation message.
    """

    @classmethod
    def from_packet(cls, from_name: str, to_name: str) -> Self:
        """Create new cancellation message from packet

        Args:
            from_name (str): Sender station name
            to_name (str): Reqipient station name
        """
        return AdscContractCancellationMessage(from_name, to_name)

    def __init__(self, from_name: str, to_name: str):
        """Create new cancellation message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
        """
        super().__init__(from_name, to_name, AdscMessage.AdscMessageType.REQUEST_CANCEL)

    def __repr__(self) -> str:
        return f"AdscContractCancellationMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r})"

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value) and isinstance(__value, AdscContractCancellationMessage)

class AdscContractRejectionMessage(AdscMessage):
    """AdscContractRejectionMessage(from_name, to_name)
    
    ADS-C Surveillance Contract Rejection message.
    """

    @classmethod
    def from_packet(cls, from_name: str, to_name: str) -> Self:
        """Create new rejection message from packet

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
        """
        return AdscContractRejectionMessage(from_name, to_name)

    def __init__(self, from_name: str, to_name: str):
        """Create new rejection message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
        """
        super().__init__(from_name, to_name, AdscMessage.AdscMessageType.REJECT)

    def __repr__(self) -> str:
        return f"AdscContractRejectionMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r})"

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value) and isinstance(__value, AdscContractRejectionMessage)

class CpdlcMessage(HoppieMessage):
    """CpdlcMessage(from_name, to_name, min, rr, message[, mrn])

    CPDLC message
    """
    _EXCHG_FORMAT_PREFIX: str = 'data2'
    _MSG_CHARS: re.Pattern = r'[A-Z0-9\.\_\@ ]'

    @classmethod
    def from_packet(cls, from_name: str, to_name: str, packet: str) -> Self:
        """Parse CPDLC message from packet string

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            packet (str): Packet string
        """
        m = re.match(r'^/' + cls._EXCHG_FORMAT_PREFIX + r'/(\d+)/(\d*)/(WU|AN|R|NE|N|Y)/(' + cls._MSG_CHARS + r'*)$', packet)
        if not m:
            raise ValueError('Invalid CPDLC message format')
        
        min = int(m.group(1), base=10)
        mrn = int(m.group(2), base=10) if m.group(2) != '' else None
        rr = m.group(3)
        message = m.group(4)

        return CpdlcMessage(from_name, to_name, min, rr, message, mrn)

    def __init__(self, from_name: str, to_name: str, min: int, rr: CpdlcResponseRequirement, message: str, mrn: int | None = None):
        """Create a CPDLC message

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            min (int): Message Identification Number (MIN)
            rr (ResponseRequirement): Response Requirement
            message (str): Message element
            mrn (int, optional): Message Reference Number. Defaults to None.
        """
        if min is None or min < 0:
            raise ValueError('Invalid MIN')
        elif mrn is not None and mrn < 0:
            raise ValueError('Invalid MRN')
        elif not re.match(r'^' + self._MSG_CHARS + r'+$', message):
            raise ValueError('Message contains invalid characters')
        else:
            super().__init__(from_name, to_name, self.MessageType.CPDLC)
            self._min = min
            self._rr = CpdlcResponseRequirement(rr)
            self._message = message
            self._mrn = mrn

    def get_min(self) -> int:
        """Return Message Identification Number (MIN)
        """
        return self._min

    def get_rr(self) -> CpdlcResponseRequirement:
        """Return Response Requirement
        """
        return self._rr

    def get_message(self) -> str:
        """Return message element
        """
        return self._message

    def get_mrn(self) -> int | None:
        """Return Message Reference Number (MRN)
        """
        return self._mrn

    def get_packet_content(self) -> str:
        return f"/{self._EXCHG_FORMAT_PREFIX}" \
               f"/{self._min}" \
               f"/{self._mrn if self._mrn is not None else ''}" \
               f"/{self._rr.value}" \
               f"/{self._message}"

    def __repr__(self) -> str:
        return f"CpdlcMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, min={self.get_min()!r}, rr={self.get_rr()!r}, message={self.get_message()!r}, mrn={self.get_mrn()!r})"

class PingMessage(HoppieMessage):
    """PingMessage([stations])

    Station online check
    """
    _PING_MAX_STATION_COUNT: int = 24
    
    def __init__(self, from_name=str, stations: list[str] | str | None = None):
        """Create a ping message.

        A ping message is used to check the online status of a station. A single station or a list of stations can be supplied.
        To retrieve a list of all online stations, use `stations='*'`.

        Args:
            from_name (str): Sender station name
            stations (list[str] | str | None, optional): Station or list of stations to check. Defaults to None.
        """
        if stations is None:
            stations = []
        elif stations == '*':
            # Retrieve list of all online stations if left empty
            stations = ['ALL-CALLSIGNS']
        else:
            if isinstance(stations, str):
                stations = [stations]
            elif len(stations) > self._PING_MAX_STATION_COUNT:
                raise ValueError('Too many stations requested')
            for s in stations:
                if not is_valid_station_name(s):
                    raise ValueError(f"Invalid station name {s}")
        super().__init__(from_name, 'SERVER', HoppieMessage.MessageType.PING)
        self._stations = stations

    def get_stations(self) -> list[str]:
        """Return list of stations to check
        """
        return self._stations

    def get_packet_content(self) -> str:
        return ' '.join(self.get_stations())

    def __repr__(self) -> str:
        return f"PingMessage(from_name={self.get_from_name()!r}, stations={self.get_stations()!r})"

class AdscMessageParser(object):
    """AdscMessageParser()
    
    Pre-processing parser for received ADS-C data.
    """
    @classmethod
    def from_packet(cls, from_name: str, to_name: str, packet: str) -> HoppieMessage:
        """Parse ADS-C message from data

        Note:
            Delegates parsing to specific message class.

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            packet (str): Packet string

        Returns:
            HoppieMessage: Parsed message object
        """
        if packet.startswith(AdscMessage.AdscMessageType.REQUEST_PERIODIC):
            return AdscPeriodicContractRequestMessage.from_packet(from_name, to_name, packet)
        elif packet.startswith(AdscMessage.AdscMessageType.REQUEST_CANCEL):
            return AdscContractCancellationMessage.from_packet(from_name, to_name)
        elif packet.startswith(AdscMessage.AdscMessageType.REPORT_PERIODIC):
            return AdscPeriodicReportMessage.from_packet(from_name, to_name, packet)
        elif packet.startswith(AdscMessage.AdscMessageType.REJECT):
            return AdscContractRejectionMessage.from_packet(from_name, to_name)
        else:
            raise ValueError('Unknown ADS-C message format')

class HoppieMessageParser(object):
    """HoppieMessageParser(station)
    
    Parser for creating `HoppieMessage` objects from received response data
    """
    def __init__(self, station: str):
        """Instantiate message parser

        Args:
            station (str): Recipient station name
        """
        self._station = station

    def parse(self, data: dict) -> HoppieMessage:
        """Parse `HoppieMessage` object from API response data

        Args:
            data (dict): API response data
        """
        from_name = data['from']
        type_name = data['type']
        packet = data['packet']

        match HoppieMessage.MessageType(type_name):
            case HoppieMessage.MessageType.TELEX:
                return TelexMessage.from_packet(from_name, self._station, packet)
            case HoppieMessage.MessageType.CPDLC:
                return CpdlcMessage.from_packet(from_name, self._station, packet)
            case HoppieMessage.MessageType.PROGRESS:
                return ProgressMessage.from_packet(from_name, self._station, packet)
            case HoppieMessage.MessageType.ADS_C:
                return AdscMessageParser.from_packet(from_name, self._station, packet)
            case _:
                raise ValueError(f"Message type '{type_name}' not yet implemented")

    def __repr__(self) -> str:
        return f"HoppieMessageParser(station={self._station!r})"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, HoppieMessageParser) and (self._station == __value._station)