import os
import sys
import json
import requests
from pathlib import Path

defaultclientid = "TWITCH.CLIENT-ID"
defaultclientsecret = "TWITCH.CLIENT-SECRET"

def make_dir(directory):
	os.makedirs(str(directory / "vods"))


def make_conf(filename):
	basejson = {
		"twitch": {
			"client-id":defaultclientid,
			"client-secret":defaultclientsecret,
			"channels":["notquiteapex","juicibox","batkigu"]
		}
	}

	filedata = json.dumps(basejson, indent=4, sort_keys=True)

	with open(str(filename), "w") as f:
		f.write(filedata)


def load_conf(filename):
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
