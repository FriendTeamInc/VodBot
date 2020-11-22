import os
import sys
import toml
import requests
from pathlib import Path

defaultclientid = "TWITCH.CLIENT-ID"
defaultclientsecret = "TWITCH.CLIENT-SECRET"

def make_dir(directory):
	os.mkdir(str(directory))


def make_conf(directory):
	basetoml = {
		"twitch": {
			"client-id":defaultclientid,
			"client-secret":defaultclientsecret,
			"channels":["notquiteapex","juicibox","batkigu"]
		}
	}

	filedata = toml.dumps(basetoml)

	with open(str(directory / "conf.toml"), "w") as f:
		f.write(filedata)


def load_conf(directory):
	conf = None
	try:
		conf = toml.load(str(Path.home() / ".vodbot" / "conf.toml"))
	except FileNotFoundError:
		make_conf(directory)
		exit_prog(2, f"Config not found. New one has been made at \"{directory}\".")
	
	CLIENT_ID = conf["twitch"]["client-id"]
	CLIENT_SECRET = conf["twitch"]["client-secret"]
	CHANNELS = conf["twitch"]["channels"]

	if CLIENT_ID == defaultclientid or CLIENT_SECRET == defaultclientsecret:
		exit_prog(3, f"Please edit your config with your Client ID and Secret.")
	
	return (CLIENT_ID, CLIENT_SECRET, CHANNELS)


def get_access_token(CLIENT_ID, CLIENT_SECRET):
	clientsecreturl = "https://id.twitch.tv/oauth2/token?"
	clientsecreturl += f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&"
	clientsecreturl += "grant_type=client_credentials"
	accesstokenrequest = requests.post(clientsecreturl)

	accesstoken = accesstokenrequest.json()

	if "access_token" in accesstoken:
		accesstoken = accesstoken["access_token"]
	else:
		exit_prog(4, "Could not get access token! Check your Client ID/Secret.")
	
	return accesstoken


def exit_prog(code=0, errmsg=None):
	if code != 0:
		msg = f"ERROR! ({code}) "
		if errmsg != None:
			msg += errmsg
		print(msg)

	print("Exiting...")
	sys.exit(code)