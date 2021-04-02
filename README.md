<p align=center>
    <img src="./img/somfy_protect_logo.png"/>
</p>

# somfy-protect-api
Python3 API Client for Somfy Protect (Home Alarm)

This library is an attempt to implement the Somfy Protect API used on mobile in Python 3.
## Identification

You just need your email and password used on Somfy Protect Mobile App.
## Supported devices
This Somfy Protect currently exposes the following type of devices:
  - Key Fob
  - IntelliTag
  - Link
  - Motion Sensors
  - InDoor Camera
  - OutDoor Camera (Not Tested)
  - InDoor Siren
  - OutDoor Siren

## Supported Action
Currently you can:
 - Get the state of a device like battery sate, link state, température, ...
 - Set the alarm security level (disarmed, armed, partial).


## TODO
 - Manage Roller Shuter on Indoor Camera
 - Update a Device.
 - TBD..

## Installation
```
pip install somfy-protect-api
```

## Example usage

```python
"""Usage Example"""
import json
import os

from somfy_protect_api.api.devices.category import Category
from somfy_protect_api.api.devices.outdoor_siren import OutDoorSiren
from somfy_protect_api.api.somfy_protect_api import SomfyProtectApi

USERNAME = "email@address.com"
PASSWORD = "********"
CACHE_PATH = "token.json"


def get_token():
    """Retrieve a token from a file
    """
    try:
        with open(CACHE_PATH, "r") as cache:
            return json.loads(cache.read())
    except IOError:
        pass


def set_token(token) -> None:
    """WWrite a toek into a file
    """
    with open(CACHE_PATH, "w") as cache:
        cache.write(json.dumps(token))


if __name__ == "__main__":

    api = SomfyProtectApi(
        username=USERNAME, password=PASSWORD, token=get_token(), token_updater=set_token
    )

    # Check if we already have a token
    if not os.path.isfile(CACHE_PATH):
        set_token(api.request_token())

    # List Sites
    sites = api.get_sites()

    # Retieve Alarm Status
    print(f"Alarm Status for {sites[0].label} is {sites[0].security_level}")

    # Set Alarm Status
    disarmed = api.update_site(site_id=sites[0].id, security_level="disarmed")
    print(f"Task: {disarmed}")

    # Get Data from a Device.
    devices = api.get_devices(site_id=sites[0].id, category=Category.OUTDOOR_SIREN)
    sirens = [OutDoorSiren(site=sites[0], device=d, api=api) for d in devices]
    for siren in sirens:
        print(
            f"Device {siren.device.label} return a Temperature of {siren.get_temperature()} °C"
        )
        print(
            f"Device {siren.device.label} return a Link Quality of {siren.get_rlink_quality()} %"
        )
        print(
            f"Device {siren.device.label} return a Battery Level of {siren.get_battery_level()} %"
        )

```