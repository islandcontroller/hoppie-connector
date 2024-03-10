import enum
import re

class HoppieResponse(object):
    class ResponseCode(enum.Enum):
        OK = 'ok'
        ERROR = 'error'

    def __init__(self, code: ResponseCode):
        self.code = code

    def get_code(self):
        return self.code

class ErrorResponse(HoppieResponse):
    def __init__(self, reason: str):
        super().__init__(HoppieResponse.ResponseCode.ERROR)
        self.reason = reason

    def get_reason(self):
        return self.reason

class SuccessResponse(HoppieResponse):
    def __init__(self, items: list[dict]):
        super().__init__(HoppieResponse.ResponseCode.OK)
        self.items = items

class HoppieResponseParser(object):
    def _parse_error(self, content: str) -> ErrorResponse:
        m = re.match(r'^\{(.*)\}$', content, flags=re.DOTALL)
        if not m: raise ValueError('Invalid error message format')
        return ErrorResponse(m.group(1))

    def _parse_message_data_item(self, content: str) -> dict | None:
        m = re.match(r'\{(\d+)\s([A-Z0-9]+)\s([a-z\s]+)\s\{([^\}]*)\}\}', content)
        if not m: return None

        id = m.group(1)
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
        for m in  re.findall(r'(\{\d+\s[A-Z0-9]+\s[a-z\s]+\s\{[^\}]*\}\})', content, flags=re.DOTALL):
            items.append(self._parse_message_data_item(m))
        return SuccessResponse(items)

    def parse(self, response: str) -> HoppieResponse:
        m = re.match(r'^(ok|error)\s?(.*)$', response, flags=re.DOTALL)
        if not m: raise ValueError('Invalid response format')
        
        content = m.group(2).strip() if m.group(2) else ''
        match HoppieResponse.ResponseCode(m.group(1)):
            case HoppieResponse.ResponseCode.ERROR: return self._parse_error(content)
            case HoppieResponse.ResponseCode.OK:    return self._parse_success(content)
            case _: raise NotImplementedError()