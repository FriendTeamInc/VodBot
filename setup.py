#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
	name="vodbot",
	version="1.0.0",
    
	author="Logan \"NotQuiteApex\" Hickok-Dickson",
	author_email="self@notquiteapex.net",
    
	description="Twitch VOD and Clip manager",
    long_description=long_description,
	long_description_content_type="text/markdown",
    
	url="https://github.com/NotQuiteApex/VodBot",
    project_urls={
        "Bug Tracker": "https://github.com/NotQuiteApex/VodBot/issues",
    },
    
	keywords="twitch vod video download",
	license="zlib/libpng",
    
	packages=find_packages(include=["vodbot", "vodbot.*"]),
    
	python_requires='>=3.6',
	install_requires=[
		"google-api-python-client>=2.0",
		"google-auth-httplib2>=0.1.0",
		"google-auth-oauthlib>=0.4.4",
		"requests>=2.20",
		"m3u8>=0.8",
	],
	entry_points={
		'console_scripts': ['vodbot=vodbot.__main__:deffered_main'],
	}
)
