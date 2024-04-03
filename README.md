# hoppie-connector

[![License](https://img.shields.io/github/license/islandcontroller/armcm-devcontainer)](LICENSE) ![PyPI - Version](https://img.shields.io/pypi/v/hoppie-connector)

The *hoppie-connector* project is an API implementation for Jeroen Hoppenbrouwers' "*Hoppie's ACARS*" services for online multiplayer flight simulation. It can be used to create custom flight tracking and dispatch systems, or serve as a basis for airborne station implementations!

## Installation

A pre-built package is hosted on [PyPI](https://pypi.org/project/hoppie-connector/) and can be installed and updated using the [`pip`](https://pip.pypa.io/en/stable/getting-started/) utility:

```sh
pip install -U hoppie-connector
```

## Usage Example

```python
from hoppie_connector import HoppieConnector, HoppieError

cnx = HoppieConnector('<your callsign>', '<your logon code>')

try:
    # Send a telex message
    cnx.send_telex('<other callsign>', '<message>')

    # Fetch and print incoming messages
    messages, delay = cnx.peek()
    for m_id, msg in messages: 
        print(f"Message {m_id}: {msg}")
except HoppieError as e:
    print(e)
```

> [!NOTE]
> In order to minimize unnecessary server load, keep the idle polling rate to at most **once every 60 seconds**. During active communication, the polling rate may be temporarily increased to once every 20 seconds.[^1]

## Documentation

A more comprehensive documentation is currently in development on this project's [GitHub Wiki](https://github.com/islandcontroller/hoppie-connector/wiki).

## Acknowledgements

Great thanks to Jeroen Hoppenbrouwers for creating and maintaining the "*Hoppie's ACARS*" services.

## Licensing

The contents of this repository are licensed under the MIT License. The full license text is provided in the [`LICENSE`](LICENSE) file.

    SPDX-License-Identifier: MIT

[^1]: ["ACARS Server API"](https://www.hoppie.nl/acars/system/tech.html). *www.hoppie.nl*. Retrieved April 3, 2024.