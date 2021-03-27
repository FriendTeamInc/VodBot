#!/usr/bin/env python3

import vodbot
from setuptools import setup, find_packages

setup(
	name="VodBot",
	version=vodbot.__version__,
	description="Twitch VOD manager",
	long_description="Downloads and stores Twitch VODs and clips.",
	author="Logan \"NotQuiteApex\" Hickok-Dickson",
	author_email="self@notquiteapex.net",
	url="https://github.com/NotQuiteApex/VodBot",
	keywords="twitch vod video download",
	license="zlib/libpng",
	packages=find_packages(include=["vodbot", "vodbot.*"]),
	python_requires='>=3.5',
	install_requires=[
		"requests>=2.20",
		"m3u8>=0.8"
	],
	entry_points={
		'console_scripts': [
			'vodbot=vodbot.__main__:deffered_main',
		],
	}
)
