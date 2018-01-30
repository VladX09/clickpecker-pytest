import pytest

from contextlib import contextmanager, ExitStack
from clickpecker.configurations import default_config
from pytest_clickpecker import utils

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
    utils.save_logcat(api, request, output_dir, logcat_options="-v time")
    save_stack_traces(api, output_dir)
    save_anr_traces(api, output_dir)
    pdf_path = utils.save_screenshots_to_pdf(api.device_wrapper, request,
                                             output_dir)
    utils.save_screen_history_tags(
        api.device_wrapper, request, path=pdf_path.with_suffix(".txt"))


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
            try:
                prepare_device(api)
                yield api
            finally:
                api.save_current_screen("LAST")
                collect_device_logs(api, request, output_dir)

    return configure_custom_api
