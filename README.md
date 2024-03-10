# hoppie-connector

[![License](https://img.shields.io/github/license/islandcontroller/armcm-devcontainer)](LICENSE) ![PyPI - Version](https://img.shields.io/pypi/v/hoppie-connector)


*A Python connector for Hoppie's ACARS service.*

## Installation

Install the module using pip:

    pip install hoppie-connector

Import it in your python script:

```python
from hoppie_connector import HoppieConnector, HoppieError

cnx = HoppieConnector('<your callsign>', '<your logon code>')

try:
    # Send telex message
    cnx.send_telex('<other callsign>', '<message>')

    # Print messages for me
    messages = cnx.peek()
    for m_id, msg in messages: 
        print(msg)
except HoppieError as e:
    print(e)
```
