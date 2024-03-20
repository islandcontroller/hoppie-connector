import enum
import re

class HoppieResponse(object):
    """HoppieResponse(code)
    
    Base response data object.
    """
    class ResponseCode(enum.Enum):
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
    """SuccessResponse(items)
    
    Success indication issued by the Hoppie API server.
    """
    def __init__(self, items: list[dict]):
        """Create success response

        Args:
            items (list[dict]): Response data
        """
        super().__init__(HoppieResponse.ResponseCode.OK)
        self._items = items

    def get_items(self) -> list[dict]:
        """Return response data items
        """
        return self._items

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, SuccessResponse) and super().__eq__(__value) and (self.get_items() == __value.get_items())

    def __str__(self) -> str:
        return f"{super().__str__()} {self.get_items()}"

    def __repr__(self) -> str:
        return f"SuccessResponse(items={self.get_items()!r})"

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

    def _parse_message_data_item(self, content: str) -> dict | None:
        m = re.match(r'\{(\d+\s)?([A-Z0-9]+)\s([a-z\s\-]+)\s\{([^\}]*)\}\}', content)
        if not m:
            return None

        id = None if m.group(1) is None else int(m.group(1), base=10)
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
        items = []
        for m in re.findall(r'(\{(?:\d+\s)?[A-Z0-9]+\s[a-z\s\-]+\s\{[^\}]*\}\})', content, flags=re.DOTALL):
            items.append(self._parse_message_data_item(m))
        return SuccessResponse(items)

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
        match HoppieResponse.ResponseCode(m.group(1)):
            case HoppieResponse.ResponseCode.ERROR:
                return self._parse_error(content)
            case HoppieResponse.ResponseCode.OK:
                return self._parse_success(content)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, HoppieResponseParser)

    def __repr__(self) -> str:
        return 'HoppieResponseParser()'