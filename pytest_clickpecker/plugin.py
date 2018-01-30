import pytest
import pathlib

from contextlib import contextmanager
from clickpecker.api import BasicAPI
from clickpecker.configurations import default_config
from pytest_clickpecker import utils

# -------------------------------------------------------------------------
# pytest hooks
# -------------------------------------------------------------------------


def pytest_addoption(parser):
    parser.addoption("--output-dir", default=None)


# -------------------------------------------------------------------------
# pytest fixtures
# -------------------------------------------------------------------------


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
        device = utils.acquire_device(device_specs, manager_url)
        try:
            device_wrapper = utils.configure_wrapper(device, device_url)
            api = BasicAPI(device_wrapper, default_config, resources)
            yield api
        finally:
            utils.release_device(device, manager_url)

    return configure_basic_api
