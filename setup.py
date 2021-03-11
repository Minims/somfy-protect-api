from distutils.core import setup

setup(
    name="somfy-protect-api",
    packages=["somfy_protect_api"],
    version="0.1.1",
    description="Python3 API Client for Somfy Protect (Home Alarm)",
    author="Minims",
    author_email="github@minims.fr",
    url="https://github.com/Minims/somfy-protect-api",
    keywords=["somfy", "protect", "home_alarm"],
    install_requires=["requests"],
    license="GNU General Public License v3.0",
    classifiers=["Programming Language :: Python :: 3.7",],
)
