#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# "imports" project and version number
# https://stackoverflow.com/a/16084844/13977827
exec(open("vodbot/__init__.py").read())

setup(
	name=__project__,
	version=__version__,
    
	author="Logan \"NotQuiteApex\" Hickok-Dickson",
	author_email="self@notquiteapex.net",
    
	description="Twitch VOD and Clip manager",
    long_description=long_description,
	long_description_content_type="text/markdown",
    
	url="https://github.com/FriendTeamInc/VodBot",
    project_urls={
		"Homepage": "https://github.com/FriendTeamInc/VodBot",
        "Bug Tracker": "https://github.com/FriendTeamInc/VodBot/issues",
    },
    
	keywords="twitch youtube vod video clip download",
	license="MIT",
    
	packages=find_packages(include=["vodbot", "vodbot.*"]),
    
	python_requires='>=3.7',
	install_requires=[
		"Pillow>=9.4.0",
		
		"argcomplete>=2.0.0",

		"dataclasses-json>=0.5.7",

		"discord-webhook>=1.0.0",

		"google-api-python-client>=2.70.0",
		"google-auth-httplib2>=0.1.0",
		"google-auth-oauthlib>=0.8.0",

		"m3u8>=3.3.0",
		
		"requests>=2.28.1",
	],
	entry_points={
		'console_scripts': ['vodbot=vodbot.__main__:deffered_main'],
	}
)
