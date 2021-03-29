from .printer import cprint

import os
import sys
import json
import requests
from pathlib import Path
from importlib import import_module

default_twitch_clientid = "INSERT-TWITCH.CLIENT-ID.HERE"
default_twitch_clientsecret = "INSERT-TWITCH.CLIENT-SECRET.HERE"
default_youtube_clientid = "INSERT-YOUTUBE.CLIENT-ID.HERE"
default_youtube_clientsecret = "INSERT-YOUTUBE.CLIENT-SECRET.HERE"
vodbotdir = Path.home() / ".vodbot"

def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A string of where the directory structure should be made.
	"""
	os.makedirs(str(directory), exist_ok=True)


def make_twitch_conf(filename):
	"""
	Writes the configuration JSON that defines VodBot's Twitch.tv operation.

	:param filename: A string of where the configuration json should be written to.
	"""

	basejson = {
		"channels": [ "46moura",
			"alkana", "batkigu", "hylianswordsman1"
			"juicibit", "michiri9", "notquiteapex",
			"pissyellowcrocs", "percy_creates", "voobo",
		],
		
		"twitch_client_id": default_twitch_clientid,
		"twitch_client_secret": default_twitch_clientsecret,
		
		"vod_dir": str(vodbotdir / "vods"),
		"clip_dir": str(vodbotdir / "clips"),
	}

	filedata = json.dumps(basejson, indent=4, sort_keys=True)

	try:
		make_dir(Path(filename).parent)
		with open(filename, "w") as f:
			f.write(filedata)
	except FileNotFoundError:
		exit_prog(67, f"Cannot create file at \"{filename}\".")


def make_youtube_conf(filename):
	"""
	Writes the configuration JSON used by the Google API. Must be a separate
	file due to how Google's API operates. See this page for details:
	https://developers.google.com/youtube/v3/guides/uploading_a_video

	:param filename: A string of where the configuration json should be written to.
	"""

	basejson = {
		"web": {
			"client_id": default_youtube_clientid,
			"client_secret": default_youtube_clientsecret,
			"auth_uri": "https://accounts.google.com/o/oauth2/auth",
			"token_uri": "https://accounts.google.com/o/oauth2/token",
			"redirect_uris": []
		}
	}

	filedata = json.dumps(basejson, indent=4, sort_keys=True)

	try:
		make_dir(Path(filename).parent)
		with open(filename, "w") as f:
			f.write(filedata)
	except FileNotFoundError:
		exit_prog(67, f"Cannot create file at \"{filename}\".")


def load_twitch_conf(filename):
	"""
	Loads the config of VodBot at a specific directory.

	:param filename: File name of the JSON formatted configuration file.
	:returns: Tuple containing the strings of the application's Twitch client ID, secret, and list of channel string names to watch for VODs, respectively.
	"""

	conf = None
	try:
		with open(filename) as f:
			conf = json.load(f)
	except FileNotFoundError:
		make_twitch_conf(filename)
		exit_prog(2, f"Config not found. New one has been made at \"{filename}\".")
	except json.decoder.JSONDecodeError as e:
		exit_prog(98, f"Failed to decode config. \"{e.msg}\"")
		
	for key in ["channels", "twitch_client_id", "twitch_client_secret", "vod_dir", "clip_dir"]:
		if key not in conf:
			exit_prog(79, f"Missing key \"{key}\" in config, please edit your config to continue.")

	CHANNELS = conf["channels"]
	CLIENT_ID = conf["twitch_client_id"]
	CLIENT_SECRET = conf["twitch_client_secret"]
	VODS_DIR = conf["vod_dir"]
	CLIPS_DIR = conf["clip_dir"]
	
	if CLIENT_ID == default_twitch_clientid or CLIENT_SECRET == default_twitch_clientsecret:
		exit_prog(3, f"Please edit your config with your Client ID and Secret from the default values, located at \"{filename}\".")

	if len(CHANNELS) == 0:
		exit_prog(40, "No channels listed in config, please edit your config to continue.")

	return (CLIENT_ID, CLIENT_SECRET, CHANNELS, VODS_DIR, CLIPS_DIR)


def exit_prog(code=0, errmsg=None):
	"""
	Exits the program with an error code and optional error message.

	:param code: The error code to exit with. Should be unique per exit case.
	:param errmsg: The corresponding error message to print when exiting.
	"""

	print()

	if code != 0:
		msg = f"#r#fR#lERROR! #fY#l({code})#r"
		if errmsg != None:
			msg += " #fR#l" + errmsg + "#r"
		cprint(msg, end=" ")

	cprint("#dExiting...#r")
	sys.exit(code)
