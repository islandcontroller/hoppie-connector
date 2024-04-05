from hoppie_connector.Messages import HoppieMessage
import enum
import re

class HoppieResponse(object):
    """HoppieResponse(code)
    
    Base response data object.
    """
    class ResponseCode(enum.StrEnum):
        OK = 'ok'
        ERROR = 'error'

        def __repr__(self) -> str:
            return f"HoppieResponse.ResponseCode.{self.name}"

    def __init__(self, code: ResponseCode):
        """Create a new base response object

        Args:
            code (ResponseCode): Response type code
        """
        if not isinstance(code, HoppieResponse.ResponseCode):
            raise ValueError('Invalid response code')
        else:
            self._code = code

    def get_code(self):
        """Return response type code
        """
        return self._code

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, HoppieResponse) and (self.get_code() == __value.get_code())

    def __str__(self) -> str:
        return f"[{self.get_code().name}]"

    def __repr__(self) -> str:
        return f"HoppieResponse(code={self.get_code()!r})"

class ErrorResponse(HoppieResponse):
    """ErrorResponse(reason)

    Error indication issued by the Hoppie API server.
    """
    def __init__(self, reason: str):
        """Create error response

        Args:
            reason (str): Reason text
        """
        super().__init__(HoppieResponse.ResponseCode.ERROR)
        self._reason = reason

    def get_reason(self):
        """Return reason text
        """
        return self._reason

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ErrorResponse) and super().__eq__(__value) and (self.get_reason() == __value.get_reason())

    def __str__(self) -> str:
        return f"{super().__str__()} {self.get_reason()}"

    def __repr__(self) -> str:
        return f"ErrorResponse(reason={self.get_reason()!r})"

class SuccessResponse(HoppieResponse):
    """SuccessResponse()
    
    Success indication issued by the Hoppie API server.
    """
    def __init__(self):
        """Create success response
        """
        super().__init__(HoppieResponse.ResponseCode.OK)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, SuccessResponse) and super().__eq__(__value)

    def __str__(self) -> str:
        return f"{super().__str__()}"

    def __repr__(self) -> str:
        return 'SuccessResponse()'

class PollSuccessResponse(SuccessResponse):
    """PollSuccessResponse(msg_data)
    
    Success indication issued by the Hoppie API server in response to a poll request
    """
    def __init__(self, msg_data: list[dict]):
        """Create success response

        Args:
            msg_data (list[dict]): List of message data objects
        """
        super().__init__()
        self._data = msg_data

    def get_data(self) -> list[dict]:
        """Return contained message data
        """
        return self._data

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PollSuccessResponse) and super().__eq__(__value) and (self.get_data() == __value.get_data())

    def __str__(self) -> str:
        return f"{super().__str__()} {self.get_data()}"

    def __repr__(self) -> str:
        return f"PollSuccessResponse(msg_data={self.get_data()!r})"

class PeekSuccessResponse(SuccessResponse):
    """PeekSuccessResponse(msg_data)
    
    Success indication issued by the Hoppie API server in response to a peek request
    """
    def __init__(self, msg_data: list[dict]):
        """Create success response

        Args:
            msg_data (list[dict]): List of message data objects
        """
        super().__init__()
        self._data = msg_data

    def get_data(self) -> list[dict]:
        """Return contained message data
        """
        return self._data

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PeekSuccessResponse) and super().__eq__(__value) and (self.get_data() == __value.get_data())

    def __str__(self) -> str:
        return f"{super().__str__()} {self.get_data()}"

    def __repr__(self) -> str:
        return f"PeekSuccessResponse(msg_data={self.get_data()!r})"

class PingSuccessResponse(SuccessResponse):
    """PingSuccessResponse(stations)
    
    Success indication issued by the Hoppie API server in response to a ping request
    """
    def __init__(self, stations: list[str]):
        """Create success response

        Args:
            msg_data (list[dict]): List of message data objects
        """
        super().__init__()
        self._stations = stations

    def get_stations(self) -> list[str]:
        """Return list of stations
        """
        return self._stations

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PingSuccessResponse) and super().__eq__(__value) and (self.get_stations() == __value.get_stations())

    def __str__(self) -> str:
        return f"{super().__str__()} {self.get_stations()}"

    def __repr__(self) -> str:
        return f"PingSuccessResponse(stations={self.get_stations()!r})"

class HoppieResponseParser(object):
    """HoppieResponseParser()
    
    Parser of Hoppie's custom-format data items, encoded in plain text
    """
    def _parse_error(self, content: str) -> ErrorResponse:
        m = re.search(r'\{(.*)\}', content, flags=re.DOTALL)
        if not m:
            raise ValueError('Invalid error message format')
        else:
            return ErrorResponse(m.group(1))

    def _parse_success(self, content: str) -> SuccessResponse:
        return SuccessResponse()

    def parse(self, response: str) -> HoppieResponse:
        """Parse response from API response text

        Args:
            response (str): Response text

        Returns:
            HoppieResponse: Parsed response
        """
        m = re.match(r'^(ok|error)\s?(.*)$', response, flags=re.DOTALL)
        if not m:
            raise ValueError('Invalid response format')
        
        content = m.group(2).strip() if m.group(2) else ''
        if m.group(1) == 'ok':
            return self._parse_success(content)
        else:
            return self._parse_error(content)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, HoppieResponseParser)

    def __repr__(self) -> str:
        return 'HoppieResponseParser()'

class PollResponseParser(HoppieResponseParser):
    """PollResponseParser()
    
    Parser of Hoppie's custom-format data items, encoded in plain text
    """
    def _parse_message_data_item(self, content: str) -> dict | None:
        m = re.match(r'\{([A-Z0-9]+)\s([a-z\s\-]+)\s\{([^\}]*)\}\}', content)
        from_name = m.group(1)
        type_name = m.group(2)
        packet_content = m.group(3)
        return {
            'from': from_name,
            'type': type_name,
            'packet': packet_content
        }

    def _parse_success(self, content: str) -> SuccessResponse:
        msg_data = []
        for m in re.findall(r'(\{[A-Z0-9]+\s[a-z\s\-]+\s\{[^\}]*\}\})', content, flags=re.DOTALL):
            msg_data.append(self._parse_message_data_item(m))
        return PollSuccessResponse(msg_data)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PollResponseParser)

    def __repr__(self) -> str:
        return 'PollResponseParser()'

class PeekResponseParser(HoppieResponseParser):
    """PeekResponseParser()
    
    Parser of Hoppie's custom-format data items, encoded in plain text
    """
    def _parse_message_data_item(self, content: str) -> dict | None:
        m = re.match(r'\{(\d+)\s([A-Z0-9]+)\s([a-z\s\-]+)\s\{([^\}]*)\}\}', content)
        id = int(m.group(1), base=10)
        from_name = m.group(2)
        type_name = m.group(3)
        packet_content = m.group(4)
        return {
            'id': id,
            'from': from_name,
            'type': type_name,
            'packet': packet_content
        }

    def _parse_success(self, content: str) -> SuccessResponse:
        msg_data = []
        for m in re.findall(r'(\{\d+\s[A-Z0-9]+\s[a-z\s\-]+\s\{[^\}]*\}\})', content, flags=re.DOTALL):
            msg_data.append(self._parse_message_data_item(m))
        return PeekSuccessResponse(msg_data)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PeekResponseParser)

    def __repr__(self) -> str:
        return 'PeekResponseParser()'

class PingResponseParser(HoppieResponseParser):
    """PingResponseParser()
    
    Parser of Hoppie's custom-format data items, encoded in plain text
    """
    def _parse_success(self, content: str) -> SuccessResponse:
        return PingSuccessResponse(re.findall(r'\s?([A-Z0-9]{3,9})', content))

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, PingResponseParser)

    def __repr__(self) -> str:
        return 'PingResponseParser()'

class HoppieResponseParserFactory(object):
    """HoppieResponseParserFactory()

    Factory class to create the corresponding parser for a given message type
    """
    def create_parser(self, request_type: HoppieMessage.MessageType) -> HoppieResponseParser:
        """Create parser for given request type

        Args:
            request_type (HoppieMessage.MessageType): Message type of the request

        Returns:
            HoppieResponseParser: Corresponding parser for request type
        """
        match HoppieMessage.MessageType(request_type):
            case HoppieMessage.MessageType.POLL:
                return PollResponseParser()
            case HoppieMessage.MessageType.PEEK:
                return PeekResponseParser()
            case HoppieMessage.MessageType.PING:
                return PingResponseParser()
            case _:
                return HoppieResponseParser()