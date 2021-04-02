# -*- coding: utf-8 -*-
from setuptools import setup

packages = [
    "somfy_protect_api",
    "somfy_protect_api.api",
    "somfy_protect_api.api.devices",
]

package_data = {"": ["*"]}

install_requires = ["requests-oauthlib>=1.3.0,<2.0.0"]

setup_kwargs = {
    "name": "somfy_protect_api",
    "version": "0.1.3",
    "description": "Python3 API Client for Somfy Protect (Home Alarm)",
    "author": "Minims",
    "author_email": "github@minims.fr",
    "maintainer": None,
    "maintainer_email": None,
    "license": "GNU General Public License v3.0",
    "url": "https://github.com/Minims/somfy-protect-api",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.6.1,<4.0",
}


setup(**setup_kwargs)
