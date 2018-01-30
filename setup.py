from setuptools import setup

setup(
    name="pytest-clickpecker",
    version="0.1",
    packages=["pytest_clickpecker"],
    install_requires=["clickpecker", "pytest", "packaging"],
    entry_points={
        'pytest11': [
            'pytest-clickpecker = pytest_clickpecker.plugin',
        ]
    },
    classifiers=[
        "Framework :: Pytest",
    ],
)
