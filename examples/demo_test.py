import pytest
import time

from packaging import version
from clickpecker.recognition import tm_engine
from clickpecker.processing.boxes_processing import filter_postprocessing
from clickpecker.processing.image_processing import check_ssim_similar, check_mse_similar

pytestmark = pytest.mark.common

ssim = check_ssim_similar(0.9, multichannel=True)
mse = check_mse_similar(50)
device_manager_url = "http://127.0.0.1:5000"


@pytest.mark.demo
@pytest.mark.parametrize("android_version", ["4.4.4"])
def test_demo(preconfigured_testing_api, android_version):
    device_spec = {"android_version": android_version}
    with preconfigured_testing_api(device_spec, device_manager_url) as api:
        settings_ico = tm_engine.load_template("resources/settings_ico.png")
        api.adb("shell pm clear com.kms.free")
        # Способ запуска приложения без указания Activity
        api.adb("shell monkey -p com.kms.free 1")
        if version.parse(android_version) >= version.parse("5.0"):
            api.tap(
                "next",
                config=dict(crop_x_range=(0.4, 0.6), crop_y_range=(0.7, 0.9)))
            for i in range(0, 2):
                time.sleep(5)
                api.tap(
                    "allow",
                    config=dict(
                        ocr_postprocessing=filter_postprocessing,
                        api_tap_index=-1))
        api.tap("accept and continue")
        api.wait_for("activation code")
        api.scroll_for("use free version", (0.5, 0.6), (0.5, 0.2))
        api.tap("use free version")
        api.tap("run the scan")
        # Эта команда вырежет участок из нижней половины скриншота
        # Чтобы распознать злосчастную кнопку ОК
        api.tap(
            "OK",
            config=dict(
                api_tap_timeout=60 * 5,
                crop_x_range=(0.1, 0.9),
                crop_y_range=(0.4, 0.8)))
        api.tap("rate later")
        api.tap(settings_ico)
        api.tap("additional")
        with api.assert_screen_change():
            api.tap("get notifications about")
            api.tap("get sound")
