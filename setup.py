import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="saltclient",
    version="0.1.0",
    author="cizixs",
    author_email="cizixs@163.com",
    description=("A simple salt client for official salt-api."),
    license="MIT",
    keywords="salt api client",
    url="https://github.com/cizixs/saltclient",
    packages=["saltclient"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
)
