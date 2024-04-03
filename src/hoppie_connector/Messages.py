import enum
import re
from datetime import datetime, time, UTC

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

        def __repr__(self) -> str:
            return f"HoppieMessage.MessageType.{self.name}"

    def _is_valid_station_name(self, name: str) -> bool:
        return bool(re.match(r'^[A-Z0-9]{3,8}$', name))

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
        elif not self._is_valid_station_name(from_name):
            raise ValueError('Invalid FROM station name')
        elif not self._is_valid_station_name(to_name):
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
    def _Is_valid_aprt_icao(cls, input: str) -> bool:
        return bool(re.match(r'^[A-Z]{4}$', input))

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
        if not self._Is_valid_aprt_icao(dep):
            raise ValueError('Invalid departure identifier')
        elif not self._Is_valid_aprt_icao(arr):
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
    """AdscMessage(from_name, to_name, report_time, posotion, altitude[, heading[, remark]])
    
    ADC-C Position Report
    """
    def __init__(self, from_name: str, to_name: str, report_time: datetime, position: tuple[float, float], altitude: float, heading: float | None = None, remark: str | None = None):
        """Create ADS-C position report

        Args:
            from_name (str): Sender station name
            to_name (str): Recipient station name
            report_time (datetime): Date and time of report
            position (tuple[float, float]): Position (lat, lon)
            altitude (float): Altitude in feet
            heading (float | None, optional): Heading in degrees. Defaults to None.
            remark (str | None, optional): Remark text. Defaults to None.
        """
        if position[0] < -90.0 or position[0] > 90.0:
            raise ValueError('Latitude out of range')
        elif position[1] < -180.0 or position[1] > 180.0:
            raise ValueError('Longitude out of range')
        elif altitude < -1000.0 or altitude > 66000.0:
            raise ValueError('Altitude out of range')
        elif heading and (heading < 0.0 or heading > 360.0):
            raise ValueError('Heading out of range')
        elif remark:
            raise NotImplementedError('Remark field not yet implemented')
        else:
            super().__init__(from_name, to_name, self.MessageType.ADS_C)
            self._time = report_time
            self._position = position
            self._altitude = altitude
            self._heading = heading

    def get_report_time(self) -> datetime:
        """Return time and day(!) of report

        Note:
            Month and year information must be ignored for received messages
        """
        return self._time

    def get_position(self) -> tuple[float, float]:
        """Return position information (lat, lon)
        """
        return self._position

    def get_altitude(self) -> float:
        """Return altitude information (feet)
        """
        return self._altitude

    def get_heading(self) -> float | None:
        """Return heading information
        """
        return self._heading

    def get_remark(self) -> str | None:
        """Return remark section contents
        """
        return None

    def get_packet_content(self) -> str:
        def _coord_to_string(coord: float) -> str:
            # Extra space for negative numbers
            leading = 1 if coord < 0 else 0
            if abs(coord) < 10:
                # Single leading digit
                leading += 1
            elif abs(coord) < 100:
                # Two leading digits
                leading += 2
            else:
                # Three leading digits
                leading += 3
            return f"{coord:{leading}.{7-leading}f}"

        packet = f"REPORT {self.get_from_name()}" \
                 f" {self._time.astimezone(UTC):%d%H%M}" \
                 f" {_coord_to_string(self._position[0])}" \
                 f" {_coord_to_string(self._position[1])}" \
                 f" {(self._altitude):.0f}"
        if self._heading:
            packet += f" {self._heading:.0f}"
        return packet

    def __repr__(self) -> str:
        return f"AdscMessage(from_name={self.get_from_name()!r}, to_name={self.get_to_name()!r}, report_time={self.get_report_time()!r}, position={self.get_position()!r}, altitude={self.get_altitude()!r}, heading={self.get_heading()!r}, remark={self.get_remark()!r})"

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
                if not self._is_valid_station_name(s):
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

class HoppieMessageFactory(object):
    """HoppieMessageFactory(station)
    
    Factory class for creating `HoppieMessage` objects from data or user input
    """
    def __init__(self, station: str):
        self._station = station

    def _create_telex_from_data(self, from_name: str, packet: str) -> TelexMessage:
        return TelexMessage(from_name, self._station, packet)

    def _create_progress_from_data(self, from_name: str, packet: str) -> ProgressMessage:
        def _get_aprt(packet: str) -> tuple[str, str] | None:
            m = re.match(r'^([A-Z]{4})\/([A-Z]{4})', packet)
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

        return ProgressMessage(from_name, self._station, dep, arr, time_out, time_eta, time_off, time_on, time_in)

    def _create_adsc_from_data(self, from_name: str, packet: str) -> AdscMessage:
        m = re.match(r'REPORT\s([A-Z0-9]{3,8})\s(\d{6})\s(\-?\d{1,2}\.\d{4,6})\s(\-?\d{1,3}\.\d{3,6})\s(\d{1,3})(?:\s(\d{1,3}))?', packet)
        if not m:
            raise ValueError('Invalid ADS-C message format')

        callsign = m.group(1)
        if callsign != from_name:
            raise ValueError('Report flight number does not match sender station name')

        report_time = datetime.strptime(m.group(2), r'%d%H%M').replace(tzinfo=UTC)
        position = (float(m.group(3)), float(m.group(4)))
        altitude = 1.0 * int(m.group(5), base=10)
        heading = None if m.group(6) is None else 1.0 * int(m.group(6), base=10)

        return AdscMessage(from_name, self._station, report_time, position, altitude, heading)

    def create_from_data(self, data: dict) -> HoppieMessage:
        """Create `HoppieMessage` object from API response data

        Args:
            data (dict): API response data
        """
        from_name = data['from']
        type_name = data['type']
        packet = data['packet']

        match HoppieMessage.MessageType(type_name):
            case HoppieMessage.MessageType.TELEX:
                return self._create_telex_from_data(from_name, packet)
            case HoppieMessage.MessageType.PROGRESS:
                return self._create_progress_from_data(from_name, packet)
            case HoppieMessage.MessageType.ADS_C:
                return self._create_adsc_from_data(from_name, packet)
            case _:
                raise ValueError(f"Message type '{type_name}' not yet implemented")

    def create_peek(self) -> PeekMessage:
        """Create a "peek"-message
        """
        return PeekMessage(self._station)

    def create_poll(self) -> PollMessage:
        """Create "poll"-message
        """
        return PollMessage(self._station)

    def create_ping(self, stations: list[str] | str | None = None) -> PingMessage:
        """Create "ping" message
        """
        return PingMessage(self._station, stations)

    def create_telex(self, to_name: str, message: str) -> TelexMessage:
        """Create freetext message from user input

        Args:
            to_name (str): Recipient station name
            message (str): Message content
        """
        return TelexMessage(self._station, to_name, message)

    def create_progress(self, to_name: str, dep: str, arr: str, time_out: time, time_eta: time | None = None, time_off: time | None = None, time_on: time | None = None, time_in: time | None = None) -> ProgressMessage:
        """Create OOOI progress message from user imput

        Args:
            to_name (str): Recipient station name
            dep (str): Departure airport ICAO code
            arr (str): Arrival airport ICAO code
            time_out (time): OUT time
            time_eta (time | None, optional): Estimated time of arrival. Defaults to None.
            time_off (time | None, optional): OFF time. Defaults to None.
            time_on (time | None, optional): ON time. Defaults to None.
            time_in (time | None, optional): IN time. Defaults to None.
        """
        return ProgressMessage(self._station, to_name, dep, arr, time_out, time_eta, time_off, time_on, time_in)

    def __repr__(self) -> str:
        return f"HoppieMessageFactory(station={self._station!r})"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, HoppieMessageFactory) and (self._station == __value._station)