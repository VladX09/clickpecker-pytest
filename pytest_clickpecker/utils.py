import requests

from datetime import datetime
from clickpecker.helpers.device_wrappers import DeviceWrapper
from clickpecker.models.device import Device


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


def save_screenshots_to_pdf(device_wrapper,
                            request,
                            output_dir=None,
                            path=None):
    # Obtain and prepare device's screenshots
    images = list(device_wrapper.screen_history.values())

    if len(images) == 0:
        # TODO: replace by logger
        print("! Screen history is empty !")
        return

    for i, img in enumerate(images):
        if img.mode != "RGB":
            images[i] = img.convert("RGB")
    img = images[0]
    if path is None:
        path = create_file_path("screenshots", "pdf", request, output_dir)
    # TODO: replace by logger
    print(f"Saving {len(images)} screenshots into {path!s}")
    img.save(path, "PDF", save_all=True, append_images=images[1:])

    return path


def save_screen_history_tags(device_wrapper,
                             request,
                             output_dir=None,
                             path=None):
    tags = [
        f"{(i+1)!s} : {tag!s} \n"
        for i, tag in enumerate(list(device_wrapper.screen_history.keys()))
    ]
    print(tags)

    if path is None:
        path = create_file_path("screenshots", "txt", request, output_dir)

    with open(path.expanduser(), mode="w") as f:
        for tag in tags:
            f.write(tag)

    return path


def save_logcat(api, request, output_dir, logcat_options="",
                logcat_filters=""):
    logcat_output_file = create_file_path("logcat", "txt", request, output_dir)
    logcat_device_file = f"/sdcard/{logcat_output_file.name!s}"
    api.adb(
        f"logcat -d {logcat_options!s} -f {logcat_device_file} {logcat_filters!s}"
    )
    api.adb(f"pull {logcat_device_file} {logcat_output_file!s}")

    return logcat_output_file
