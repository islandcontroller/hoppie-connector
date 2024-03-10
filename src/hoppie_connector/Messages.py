import enum
import re
from datetime import datetime, timedelta, UTC

class HoppieMessage(object):
    class MessageType(enum.Enum):
        ADS_C = 'ads-c'
        PROGRESS = 'progress'
        TELEX = 'telex'
        POLL = 'poll'
        PEEK = 'peek'

    def _is_valid_station_name(self, name: str) -> bool:
        return name == 'ALL-CALLSIGNS' or re.match(r'^[A-Z0-9]{3,8}$', name)

    def __init__(self, from_name: str, to_name: str, type: MessageType):
        if type not in self.MessageType:
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
        return self._from

    def get_to_name(self) -> str:
        return self._to

    def get_msg_type(self) -> MessageType:
        return self._type

    def get_packet_content(self) -> str:
        return ''

    def get_msg_params(self) -> dict:
        return {
            'from': self._from,
            'to': self._to,
            'type': self._type.value,
            'packet': self.get_packet_content()
        }

    def __str__(self) -> str:
        return str(self.get_msg_params())

    def __repr__(self) -> str:
        return self.__str__()

class PeekMessage(HoppieMessage): 
    def __init__(self, from_name: str):
        super().__init__(from_name, 'SERVER', self.MessageType.PEEK)

class PollMessage(HoppieMessage):
    def __init__(self, from_name: str):
        super().__init__(from_name, 'SERVER', self.MessageType.POLL)

class TelexMessage(HoppieMessage):
    _TELEX_MAX_MSG_LEN: int = 220

    def __init__(self, from_name: str, to_name: str, message: str):
        if len(message) > self._TELEX_MAX_MSG_LEN: 
            raise ValueError('Message too long')
        elif not message.isascii():
            raise ValueError('Message contains non-ASCII characters')
        else:
            super().__init__(from_name, to_name, self.MessageType.TELEX)
            self._message = message

    def get_message(self) -> str:
        return self._message

    def get_packet_content(self) -> str:
        return self._message.upper()

class ProgressMessage(HoppieMessage):
    @classmethod
    def _Is_valid_aprt_icao(cls, input: str) -> bool:
        return bool(re.match(r'^[A-Z]{4}$', input))

    def __init__(self, from_name: str, to_name: str, dep: str, arr: str, time_out: datetime, time_eta: datetime | None = None, time_off: datetime | None = None, time_on: datetime | None = None, time_in: datetime | None = None):
        if not self._Is_valid_aprt_icao(dep):
            raise ValueError('Invalid departure identifier')
        elif not self._Is_valid_aprt_icao(arr):
            raise ValueError('Invalid arrival identifier')
        elif time_on and not time_off:
            raise ValueError('Missing OFF time')
        elif time_in and not time_on: 
            raise ValueError('Missing ON time')
        elif time_off and time_off < time_out:
            raise ValueError('Invalid OFF before OUT time')
        elif time_on and time_on < time_off:
            raise ValueError('Invalid ON before OFF time')
        elif time_in and time_in < time_on:
            raise ValueError('Invalid IN before ON time')
        elif time_eta and time_eta < time_out:
            raise ValueError('Invalid ETA before OUT time')
        elif time_eta and time_off and time_eta < time_off:
            raise ValueError('Invalid ETA before OFF time')
        elif time_eta and time_on:
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
        return self._dep

    def get_arrival(self) -> str:
        return self._arr

    def get_time_out(self) -> datetime:
        return self._out

    def get_time_off(self) -> datetime | None:
        return self._off

    def get_time_on(self) -> datetime | None:
        return self._on

    def get_time_in(self) -> datetime | None:
        return self._in

    def get_eta(self) -> datetime | None:
        return self._eta

    def get_packet_content(self) -> str:
        packet = f"{self._dep}/{self._arr} OUT/{self._out.astimezone(UTC):%H%M}"
        if self._off: packet += f" OFF/{self._off.astimezone(UTC):%H%M}"
        if self._on: packet += f" ON/{self._on.astimezone(UTC):%H%M}"
        if self._in: packet += f" IN/{self._in.astimezone(UTC):%H%M}"
        if self._eta: packet += f" ETA/{self._eta.astimezone(UTC):%H%M}"
        return packet

class AdscMessage(HoppieMessage):
    def __init__(self, from_name: str, to_name: str, report_time: datetime, position: tuple[float, float], altitude: float, heading: float | None = None, remark: str | None = None):
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
            self._remark = remark

    def get_report_time(self) -> datetime:
        return self._time

    def get_position(self) -> tuple[float, float]:
        return self._position

    def get_altitude(self) -> float:
        return self._altitude

    def get_heading(self) -> float | None:
        return self._heading

    def get_remark(self) -> str | None:
        return self._remark

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
                 f" {(self._altitude / 100):.0f}"
        if self._heading: packet += f" {self._heading:.0f}"
        if self._remark: packet += self._remark
        return packet

class HoppieMessageFactory(object):
    def __init__(self, station: str):
        self._station = station

    def _create_telex_from_data(self, from_name: str, packet: str) -> TelexMessage:
        return TelexMessage(from_name, self._station, packet)

    def _create_progress_from_data(self, from_name: str, packet: str) -> ProgressMessage:
        def _get_aprt(packet: str) -> tuple[str, str] | None:
            m = re.match(r'^([A-Z]{4})\/([A-Z]{4})', packet)
            if not m: raise ValueError('Invalid dep/arr value')
            else:     return m.group(1), m.group(2)

        def _get_time(now: datetime, timestr: str) -> datetime:
            time = datetime.strptime(timestr, '%H%M').replace(tzinfo=UTC)
            if time.time() > now.time():
                yest = now + timedelta(days=-1)
                return time.replace(yest.year, yest.month, yest.day)
            else:
                return time.replace(now.year, now.month, now.day)

        def _get_time_out(now: datetime, packet: str) -> datetime | None:
            m = re.match(r'^[A-Z]{4}\/[A-Z]{4}\sOUT\/(\d{4})Z?', packet)
            if not m: raise ValueError('Invalid OUT value')
            else:     return _get_time(now, m.group(1))

        def _get_time_off(now: datetime, packet: str) -> datetime | None:
            m = re.match(r'^[A-Z]{4}\/[A-Z]{4}\sOUT\/\d{4}Z?\sOFF\/(\d{4})Z?', packet)
            if not m: return None
            else:     return _get_time(now, m.group(1))

        def _get_eta(now: datetime, packet: str) -> datetime | None:
            m = re.match(r'^[A-Z]{4}\/[A-Z]{4}\sOUT\/\d{4}Z?\s(?:OFF\/\d{4}Z?\s)?ETA\/(\d{4})Z?', packet)
            if not m: return None
            else:     return _get_time(now, m.group(1))

        def _get_time_on(now: datetime, packet: str) -> datetime | None:
            m = re.match(r'^[A-Z]{4}\/[A-Z]{4}\sOUT\/\d{4}Z?\sOFF\/\d{4}Z?\sON\/(\d{4})Z?', packet)
            if not m: return None
            else:     return _get_time(now, m.group(1))

        def _get_time_in(now: datetime, packet: str) -> datetime | None:
            m = re.match(r'^[A-Z]{4}\/[A-Z]{4}\sOUT\/\d{4}Z?\sOFF\/\d{4}Z?\sON\/\d{4}Z?\sIN\/(\d{4})Z?', packet)
            if not m: return None
            else:     return _get_time(now, m.group(1))

        now = datetime.now()
        dep, arr = _get_aprt(packet)
        time_out = _get_time_out(now, packet)
        time_off = _get_time_off(now, packet)
        time_on = _get_time_on(now, packet)
        time_in = _get_time_in(now, packet)
        time_eta = _get_eta(now, packet)

        return ProgressMessage(from_name, self._station, dep, arr, time_out, time_eta, time_off, time_on, time_in)

    def create_from_data(self, data: dict) -> tuple[int, HoppieMessage]:
        id = data['id']
        from_name = data['from']
        type_name = data['type']
        packet = data['packet']

        match HoppieMessage.MessageType(type_name):
            case HoppieMessage.MessageType.TELEX:    msg = self._create_telex_from_data(from_name, packet)
            case HoppieMessage.MessageType.PROGRESS: msg = self._create_progress_from_data(from_name, packet)
            case _: raise ValueError(f"Message type '{type_name}' not yet implemented")

        return id, msg

    def create_peek(self) -> PeekMessage:
        return PeekMessage(self._station)

    def create_poll(self) -> PollMessage:
        return PollMessage(self._station)

    def create_telex(self, to_name: str, message: str) -> TelexMessage:
        return TelexMessage(self._station, to_name, message)
