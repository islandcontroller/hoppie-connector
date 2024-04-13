from hoppie_connector.Messages import HoppieMessage, AdscContractRequestMessage
import unittest

class TestAdscContractRequestMessage(unittest.TestCase):
    _EXPECTED_TYPE = HoppieMessage.MessageType.ADS_C
    _EXPECTED_CONTRACT = AdscContractRequestMessage.ContractType.PERIODIC
    
    def setUp(self) -> None:
        super().setUp()
        self._UUT = AdscContractRequestMessage('ATC', 'CALLSIGN', self._EXPECTED_CONTRACT)

    def test_get_type(self):
        self.assertEqual(self._EXPECTED_TYPE, self._UUT.get_msg_type())

    def test_get_contract_type(self):
        self.assertEqual(self._EXPECTED_CONTRACT, self._UUT.get_contract_type())

class TestAdscContractRequestMessageRepresentation(unittest.TestCase):
    def test_repr(self):
        expected = AdscContractRequestMessage('ATC', 'CALLSIGN', AdscContractRequestMessage.ContractType.PERIODIC)
        actual = eval(repr(expected))
        self.assertEqual(expected, actual)

class TestAdscContractRequestMessageComparison(unittest.TestCase):
    def test_same(self):
        value1 = AdscContractRequestMessage('ATC', 'CALLSIGN', AdscContractRequestMessage.ContractType.PERIODIC)
        value2 = value1
        self.assertEqual(value1, value2)

    def test_equal_content(self):
        value1 = AdscContractRequestMessage('ATC', 'CALLSIGN', AdscContractRequestMessage.ContractType.PERIODIC)
        value2 = AdscContractRequestMessage('ATC', 'CALLSIGN', AdscContractRequestMessage.ContractType.PERIODIC)
        self.assertEqual(value1, value2)