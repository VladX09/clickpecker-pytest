import pytest
import requests
import os
import pathlib

from datetime import datetime
from contextlib import contextmanager
from clickpecker.helpers.device_wrappers import DeviceWrapper
from clickpecker.models.device import Device
from clickpecker.api import BasicAPI
from clickpecker.configurations import default_config


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


def create_file_path(base_name, ext, request, output_dir):
    test_case_name = request.node.name
    file_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
    file_name = f"{base_name!s}_{test_case_name!s}_{file_time}.{ext!s}"
    file_path = output_dir / file_name
    return file_path


def save_screenshots_to_pdf(device_wrapper, request, output_dir):
    # Obtain and prepare device's screenshots
    images = list(device_wrapper.screen_history)

    if len(images) == 0:
        # TODO: replace by logger
        print("! Screen history is empty !")
        return

    for i, img in enumerate(images):
        if img.mode != "RGB":
            images[i] = img.convert("RGB")
    img = images[0]
    path = create_file_path("screenshots", "pdf", request, output_dir)
    # TODO: replace by logger
    print("Saving {} screenshots into {}".format(len(images), path))
    img.save(path, "PDF", save_all=True, append_images=images[1:])


def save_device_logs(api,
                     request,
                     output_dir,
                     logcat_options="",
                     logcat_filters=""):
    logcat_output_file = create_file_path("logcat", "txt", request, output_dir)
    logcat_device_file = f"/sdcard/{logcat_output_file.name!s}"
    api.adb(
        f"logcat -d {logcat_options!s} -f {logcat_device_file} {logcat_filters!s}"
    )
    api.adb(f"pull {logcat_device_file} {logcat_output_file!s}")


@pytest.fixture
def output_dir(request):
    rootdir = request.config.rootdir
    output_dir = pathlib.Path(rootdir) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def prepare_device(api):
    api.adb("logcat -c")
    api.adb("shell rm /sdcard/logcat*.txt")


def collect_device_logs(api, request, output_dir):
    save_device_logs(api, request, output_dir, logcat_options="-v time")
    save_screenshots_to_pdf(api.device_wrapper, request, output_dir)


@pytest.fixture
def testing_api(request, output_dir):
    @contextmanager
    def configure_api(device_specs,
                      manager_url,
                      device_url="",
                      resources=None,
                      default_config=default_config):
        device = acquire_device(device_specs, manager_url)
        try:
            device_wrapper = configure_wrapper(device, device_url)
            api = BasicAPI(device_wrapper, default_config, resources)
            prepare_device(api)
            yield api
        finally:
            collect_device_logs(api, request, output_dir)
            release_device(device, manager_url)

    return configure_api
