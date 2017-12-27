import pytest

from clickpecker.helpers.device_wrappers import DeviceWrapper
from clickpecker.recognition import tm_engine
from clickpecker.api import BasicAPI

pytestmark = pytest.mark.common

@pytest.mark.parametrize("android_version",["4.4.4","7.1.1"])
def test_demo(testing_api, android_version):
    device_spec = {
        "android_version":android_version
    }
    device_manager_url = "http://127.0.0.1:5000"
    with testing_api(device_spec, device_manager_url) as api:
        settings_ico = tm_engine.load_template("settings_ico.png")
        api.adb("shell pm clear com.kms.free")
        # Способ запуска приложения без указания Activity
        api.adb("shell monkey -p com.kms.free 1")
        if android_version > "5.0":
            api.tap("NEXT", crop_x_range=(0.4,0.6), crop_y_range=(0.5,0.7))
            api.tap("ALLOW")
            api.tap("ALLOW")
        api.tap("accept and continue")
        api.wait_for("activation code")
        api.scroll_for("use free version", (0.5, 0.6), (0.5, 0.2))
        api.tap("use free version")
        api.tap("run the scan")
        # Эта команда вырежет участок из нижней половины скриншота
        # Чтобы распознать злосчастную кнопку ОК
        api.tap("OK", 60 * 5, crop_x_range=(0.1, 0.9), crop_y_range=(0.4, 0.8))
        api.tap("rate later")
        api.tap(settings_ico)
        api.tap("additional")
        api.tap("get notifications about")
        api.tap("get sound")
