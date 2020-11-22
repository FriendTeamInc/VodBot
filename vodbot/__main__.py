from . import util

import os
import requests
import toml
from pathlib import Path

def main():
	vodbotdir = Path.home() / ".vodbot"

	if not os.path.exists(str(vodbotdir)):
		util.make_dir(vodbotdir)

		util.make_conf(vodbotdir)
		
		util.exit_prog(1, f"Edit the config files in \"{vodbotdir}\" before running again.")
	
	if not os.path.isdir(str(vodbotdir)):
		util.exit_prog(54, f"Non-directory object \"{vodbotdir}\" must be removed before proceeding!")

	conf = None
	try:
		conf = toml.load(str(Path.home() / ".vodbot" / "conf.toml"))
	except FileNotFoundError:
		util.make_conf(vodbotdir)
		util.exit_prog(2, f"Config not found. New one has been made at \"{vodbotdir}\".")
	
	CLIENT_ID = conf["twitch"]["client-id"]
	CLIENT_SECRET = conf["twitch"]["client-secret"]
	CHANNELS = conf["twitch"]["channels"]

	if CLIENT_ID == util.defaultclientid or CLIENT_SECRET == util.defaultclientsecret:
		util.exit_prog(3, f"Please edit your config with your Client ID and Secret.")

	clientsecreturl = "https://id.twitch.tv/oauth2/token?"
	clientsecreturl += f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&"
	clientsecreturl += "grant_type=client_credentials"
	accesstokenrequest = requests.post(clientsecreturl)

	accesstoken = accesstokenrequest.json()

	if "access_token" in accesstoken:
		accesstoken = accesstoken["access_token"]
	else:
		util.exit_prog(4, "Could not get access token! Check your Client ID/Secret.")

	headers = {"Client-ID":CLIENT_ID, "Authorization": "Bearer " + accesstoken}

	userids = []
	getidsurl = "https://api.twitch.tv/helix/users?" 
	getidsurl += "&".join(f"login={i}" for i in conf["twitch"]["channels"])
	print(getidsurl)

	# GET https://api.twitch.tv/helix/videos: get videos using the IDs

	#print(accesstokenrequest.json())


if __name__ == "__main__":
	main()
