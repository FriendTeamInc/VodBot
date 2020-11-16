#!/usr/bin/env python3

from setuptools import setup

long_description = """
Downloads, stores, and reuploads Twitch VODs.
"""

setup(
    name="VodBot",
    version="0.1.0",
    description="Twitch VOD manager",
    long_description="Downloads, stores, and reuploads Twitch VODs.",
    author="Logan \"NotQuiteApex\" Hickok-Dickson",
    author_email="self@notquiteapex.net",
    url="https://github.com/NotQuiteApex/VodBot",
    keywords="twitch vod video download",
    license="zlib/libpng",
    packages=["vodbot"],
    python_requires='>=3.9',
    install_requires=[
        "requests>=2.25",
    ],
    entry_points={
        'console_scripts': [
            'vodbot=vodbot.__main__:main',
        ],
    }
)