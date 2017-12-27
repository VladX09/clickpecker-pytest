import pytest
import requests

from contextlib import contextmanager
from clickpecker.helpers.device_wrappers import DeviceWrapper
from clickpecker.models.device import Device
from clickpecker.api import BasicAPI


@pytest.fixture
def testing_api():
    def acquire_device(device_specs, manager_url):
        acquire_url = "{}/acquire".format(manager_url)
        request_body = {"filters": device_specs}
        r = requests.post(acquire_url, json=request_body)
        if r.status_code == 200:
            device = Device.from_dict(r.json())
            return device
        else:
            # TODO: add non-free device handling
            raise ConnectionError(r.text)

    def configure_wrapper(device_model, device_url):
        wrapper = DeviceWrapper(device_model, device_url)
        return wrapper

    def release_device(device, manager_url):
        release_url = "{}/release".format(manager_url)
        request_body = {"filters": {"adb_id": device.adb_id}}
        r = requests.post(release_url, json=request_body)
        if r.status_code != 200:
            raise ConnectionError(r.text)

    @contextmanager
    def configure_api(device_specs, manager_url, device_url="",
                      resources=None):
        device = acquire_device(device_specs, manager_url)
        device_wrapper = configure_wrapper(device, device_url)
        api = BasicAPI(device_wrapper, resources)
        try:
            yield api
        finally:
            release_device(device, manager_url)

    return configure_api
