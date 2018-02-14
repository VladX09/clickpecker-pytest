import pytest
import time

from packaging import version
from clickpecker.recognition import tm_engine
from clickpecker.processing.boxes_processing import filter_postprocessing

# Mark whloe module to divide different groups of tests
pytestmark = pytest.mark.common

device_manager_url = "http://127.0.0.1:5000"

# You can mark a function
@pytest.mark.demo
# You can launch one case several times with different parameters
@pytest.mark.parametrize("android_version", ["4.4.4"])
def test_demo(preconfigured_testing_api, android_version):

    # Load necessary resources
    settings_ico = tm_engine.load_template("resources/settings_ico.png")

    # Create a dictionary with filters to find specific device
    device_spec = {"android_version": android_version}

    with preconfigured_testing_api(device_spec, device_manager_url) as api:
        api.adb("shell pm clear com.kms.free")
        # Launch an app without specifying Activity
        api.adb("shell monkey -p com.kms.free 1")

        # Use packaging.version to compare different versions
        if version.parse(android_version) >= version.parse("5.0"):
            api.tap(
                "next",
                config=dict(crop_x_range=(0.4, 0.6), crop_y_range=(0.7, 0.9)))

            # We need to allow permissions
            for i in range(0, 2):
                time.sleep(5)

                # Some special cases needs special configuration
                api.tap("allow",
                        config=dict(
                            ocr_postprocessing=filter_postprocessing,
                            api_tap_index=-1))

        # But most of cases are simple
        api.tap("accept and continue")
        api.wait_for("activation code")

        # Scroll down (move your "finger"" from the lowest point to the highest one)
        # Untill you find the text (maximum number of screens is adjustable)
        api.scroll_for("use free version", (0.5, 0.6), (0.5, 0.2))
        api.tap("use free version")
        api.tap("run the scan")

        api.tap(
            "OK",
            config=dict(
                api_tap_timeout=60 * 5,
                crop_x_range=(0.1, 0.9),
                crop_y_range=(0.4, 0.8)))
        api.tap("rate later")
        api.tap(settings_ico)
        api.tap("additional")

        # Some checkboxes should change their state
        with api.assert_screen_change():
            api.tap("get notifications about")
            api.tap("get sound")
