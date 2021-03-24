import os
import sys
import json
import requests
from pathlib import Path
from importlib import import_module

defaultclientid = "DEFAULT-TWITCH.CLIENT-ID"
defaultclientsecret = "DEFAULT-TWITCH.CLIENT-SECRET"
vodbotdir = Path.home() / ".vodbot"

def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A string of where the directory structure should be made.
	"""
	os.makedirs(directory, exist_ok=True)


def make_conf(filename):
	"""
	Writes the configuration JSON that defines VodBot's operation.

	:param filename: A string of where the conf.json should be written to.
	"""

	basejson = {
		"channels": [ "46moura",
			"alkana", "batkigu", "hylianswordsman1"
			"juicibit", "michiri9", "notquiteapex",
			"pissyellowcrocs", "percy_creates", "voobo",
		],
		
		"client_id":defaultclientid,
		"client_secret":defaultclientsecret,
		
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


def load_conf(filename):
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
		make_conf(filename)
		exit_prog(2, f"Config not found. New one has been made at \"{filename}\".")
	except json.decoder.JSONDecodeError as e:
		exit_prog(98, f"Failed to decode config. \"{e.msg}\"")
		
	for key in ["channels", "client_id", "client_secret", "vod_dir", "clip_dir"]:
		if key not in conf:
			exit_prog(79, f"Missing key \"{key}\" in config, please edit your config to continue.")

	CHANNELS = conf["channels"]
	CLIENT_ID = conf["client_id"]
	CLIENT_SECRET = conf["client_secret"]
	VODS_DIR = conf["vod_dir"]
	CLIPS_DIR = conf["clip_dir"]
	
	if CLIENT_ID == defaultclientid or CLIENT_SECRET == defaultclientsecret:
		exit_prog(3, f"Please edit your config with your Client ID and Secret from the default values, located at \"{filename}\".")

	if len(CHANNELS) == 0:
		exit_prog(40, "No channels listed in config, please edit your config to continue.")

	return (CLIENT_ID, CLIENT_SECRET, CHANNELS, VODS_DIR, CLIPS_DIR)


def get_access_token(CLIENT_ID, CLIENT_SECRET):
	"""
	Uses a (blocking) HTTP request to retrieve an access token for use with Twitch's API

	:param CLIENT_ID: The associated client ID of the Twitch Application, registered at the Twitch Dev Console online and stored in the appropriate vodbot config.
	:param CLIENT_SECRET: The associate client secret, from the same as client ID.
	:returns: The string of the access token (not including the "Bearer: " prefix).
	"""

	clientsecreturl = ("https://id.twitch.tv/oauth2/token?"
					f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&"
					"grant_type=client_credentials"
					)
	accesstokenrequest = requests.post(clientsecreturl)

	accesstoken = accesstokenrequest.json()

	if "access_token" in accesstoken:
		accesstoken = accesstoken["access_token"]
	else:
		exit_prog(4, "Could not get access token! Check your Client ID/Secret.")
	
	return accesstoken


def exit_prog(code=0, errmsg=None):
	"""
	Exits the program with an error code and optional error message.

	:param code: The error code to exit with. Should be unique per exit case.
	:param errmsg: The corresponding error message to print when exiting.
	"""

	print()

	if code != 0:
		msg = f"ERROR! ({code}) "
		if errmsg != None:
			msg += errmsg
		print(msg)

	print("Exiting...")
	sys.exit(code)
