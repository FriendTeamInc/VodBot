# Module to pull and create different files and directories on the OS

from .printer import cprint

import os
import sys
import json
import argparse
from pathlib import Path
from collections import OrderedDict


vodbotdir = Path.home() / ".vodbot"
DEFAULT_CONF_PATH = vodbotdir / "conf.json"
DEFAULT_CONF = OrderedDict([
	("twitch_channels", []),

	("stage_timezone", "+0000"),

	("stage_format", {
		"watch": "-- Watch live at {links}",
		"discord": "-- Join the Discord at https://discord.gg/v2t6uag",
		"credits": "\n{watch}\n{discord}"
	}),
	
	("youtube_client_path", str(vodbotdir / "yt-client.json")),
	("youtube_pickle_path", str(vodbotdir / "yt-api-keys.pkl")),
	
	("vod_dir", str(vodbotdir / "vods")),
	("clip_dir", str(vodbotdir / "clips")),
	("temp_dir", str(vodbotdir / "temp")),
	("stage_dir", str(vodbotdir / "stage"))
])


def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A string of where the directory structure should be made.
	"""
	os.makedirs(str(directory), exist_ok=True)


def load_conf(filename):
	"""
	Loads the config of VodBot at a specific directory.

	:param filename: File name of the JSON formatted configuration file.
	:returns: Dictionary created from the conf file.
	"""

	conf = None
	try:
		with open(filename) as f:
			conf = json.load(f)
	except FileNotFoundError:
		exit_prog(2, f"Config not found. You can configure VodBot with the init command.")
	except json.decoder.JSONDecodeError as e:
		exit_prog(98, f"Failed to decode config. \"{e.msg}\"")
		
	for key in DEFAULT_CONF:
		if key not in conf:
			exit_prog(79, f"Missing key \"{key}\" in config, please edit your config to continue.")
	
	if conf["youtube_client_path"] == "":
		cprint("Please edit your config with your Youtube Client ID and Secret to use the upload command.")

	if len(conf["twitch_channels"]) == 0:
		exit_prog(40, "No channels listed in config, please edit your config to continue.")

	return conf


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

	cprint("#r#dExiting...#r")
	sys.exit(code)
