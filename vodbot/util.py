import os
import sys
import json
import requests
from pathlib import Path
from importlib import import_module

defaultclientid = "TWITCH.CLIENT-ID"
defaultclientsecret = "TWITCH.CLIENT-SECRET"

def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A pathlib.Path directory object of where the directory structure should be made.
	"""
	os.makedirs(str(directory / "vods"))


def make_conf(directory):
	"""
	Writes the configuration JSON that defines VodBot's operation.

	:param directory: A pathlib.Path directory object of where the conf.json should be written to.
	"""

	basejson = {
		"twitch": {
			"client-id":defaultclientid,
			"client-secret":defaultclientsecret,
			"channels":["notquiteapex","juicibit","batkigu"]
		}
	}

	filedata = json.dumps(basejson, indent=4, sort_keys=True)

	with open(str(directory / "conf.json"), "w") as f:
		f.write(filedata)


def make_encode_json(directory):
	"""
	Writes the JSON preset data for HandBrakeCLI to use.

	:param directory: A pathlib.Path directory object of where the preset should be written to.
	"""

	encode_json = import_module(".encode_json", "vodbot")

	with open(str(directory / "vodbot-hbcli-encode.json"), "w") as f:
		f.write(encode_json.json)


def init_dir(directory):
	"""
	Initializes all the necessary directory structures and files for VodBot.

	:param directory: A pathlib.Path directory object of where everthing goes.
	"""
	make_dir(directory)
	make_conf(directory)
	make_encode_json(directory)


def load_conf(directory):
	"""
	Loads the config of VodBot at a specific directory.

	:param directory: Directory that houses the conf.json configuration file.
	:returns: Tuple containing the strings of the application's Twitch client ID, secret, and list of channel string names to watch for VODs, respectively.
	"""

	filename = directory / "conf.json"

	conf = None
	try:
		with open(str(filename)) as f:
			conf = json.load(f)
	except FileNotFoundError:
		make_conf(filename)
		exit_prog(2, f"Config not found. New one has been made at \"{str(filename)}\".")
	
	CLIENT_ID = conf["twitch"]["client-id"]
	CLIENT_SECRET = conf["twitch"]["client-secret"]
	CHANNELS = conf["twitch"]["channels"]

	if CLIENT_ID == defaultclientid or CLIENT_SECRET == defaultclientsecret:
		exit_prog(3, f"Please edit your config with your Client ID and Secret.")
	
	return (CLIENT_ID, CLIENT_SECRET, CHANNELS)


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

	if code != 0:
		msg = f"ERROR! ({code}) "
		if errmsg != None:
			msg += errmsg
		print(msg)

	print("Exiting...")
	sys.exit(code)
