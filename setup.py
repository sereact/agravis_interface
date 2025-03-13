from setuptools import setup, find_packages
import codecs
import os


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="agravis_interface",
    install_requires=[
        "msgpack",
        "aiohttp",
        "aiohttp-cors",
        "requests",
        "asyncio",
        "colorlog",
    ],
    version=get_version("agravis_interface/__init__.py"),
    packages=find_packages(),
    include_package_data=True,
)
