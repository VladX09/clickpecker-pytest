import pytest
import requests
import os
import pathlib

from datetime import datetime
from contextlib import contextmanager, ExitStack
from clickpecker.helpers.device_wrappers import DeviceWrapper
from clickpecker.models.device import Device
from clickpecker.api import BasicAPI
from clickpecker.configurations import default_config


# =============== Pytest hooks ===============
def pytest_addoption(parser):
    parser.addoption("--output-dir", default=None)


# ============= Service functions ============
def acquire_device(device_specs, manager_url):
    acquire_url = f"{manager_url!s}/acquire"
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
    release_url = f"{manager_url!s}/release"
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
    # TODO: Add saving tags
    images = list(device_wrapper.screen_history.values())

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
    print(f"Saving {len(images)} screenshots into {path!s}")
    img.save(path, "PDF", save_all=True, append_images=images[1:])


def save_logcat(api, request, output_dir, logcat_options="",
                logcat_filters=""):
    logcat_output_file = create_file_path("logcat", "txt", request, output_dir)
    logcat_device_file = f"/sdcard/{logcat_output_file.name!s}"
    api.adb(
        f"logcat -d {logcat_options!s} -f {logcat_device_file} {logcat_filters!s}"
    )
    api.adb(f"pull {logcat_device_file} {logcat_output_file!s}")


# ============== Plugin fixtures =============
@pytest.fixture
def output_dir(request):
    outdir = request.config.getoption("--output-dir")
    if outdir is None:
        rootdir = request.config.rootdir
        outdir = pathlib.Path(rootdir) / "output"
    else:
        outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


@pytest.fixture
def testing_api():
    @contextmanager
    def configure_basic_api(device_specs,
                            manager_url,
                            device_url="",
                            resources=None,
                            default_config=default_config):
        device = acquire_device(device_specs, manager_url)
        try:
            device_wrapper = configure_wrapper(device, device_url)
            api = BasicAPI(device_wrapper, default_config, resources)
            yield api
        finally:
            release_device(device, manager_url)

    return configure_basic_api


# =============== User fixtures ==============
def save_stack_traces(api, output_dir):
    traces_mask = "/sdcard/stack_trace*.txt"
    traces_folder = "/sdcard/stack_traces"
    api.adb(f"shell mkdir {traces_folder}")
    api.adb(f"shell mv {traces_mask} {traces_folder}")
    api.adb(f"pull {traces_folder} {output_dir!s}")


def save_anr_traces(api, output_dir):
    anr_traces_folder = "/data/anr"
    api.adb(f"pull {anr_traces_folder} {output_dir!s}")


def prepare_device(api):
    api.adb("logcat -c")
    api.adb("shell rm /sdcard/logcat*.txt")
    api.adb("shell rm /sdcard/stack_trace*.txt")


def collect_device_logs(api, request, output_dir):
    save_logcat(api, request, output_dir, logcat_options="-v time")
    save_stack_traces(api, output_dir)
    save_anr_traces(api, output_dir)
    save_screenshots_to_pdf(api.device_wrapper, request, output_dir)


@pytest.fixture
def preconfigured_testing_api(testing_api, request, output_dir):
    @contextmanager
    def configure_custom_api(device_specs,
                             manager_url,
                             device_url="",
                             resources=None,
                             default_config=default_config):
        with ExitStack() as stack:
            api = stack.enter_context(
                testing_api(device_specs, manager_url, device_url, resources,
                            default_config))
            prepare_device(api)
            yield api
            api.save_current_screen("LAST")
            collect_device_logs(api, request, output_dir)

    return configure_custom_api
