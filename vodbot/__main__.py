from . import util

import json
import os
import requests
import toml
from pathlib import Path

def main():
	# Default path
	vodbotdir = Path.home() / ".vodbot"

	# Initial error checks
	if not os.path.exists(str(vodbotdir)):
		util.make_dir(vodbotdir)
		util.make_conf(vodbotdir)
		util.exit_prog(1, f"Edit the config files in \"{vodbotdir}\" before running again.")
	
	if not os.path.isdir(str(vodbotdir)):
		util.exit_prog(54, f"Non-directory object \"{vodbotdir}\" must be removed before proceeding!")


	# Load the config and set up the access token
	(CLIENT_ID, CLIENT_SECRET, CHANNELS) = util.load_conf(vodbotdir)
	ACCESS_TOKEN = util.get_access_token(CLIENT_ID, CLIENT_SECRET)

	headers = {"Client-ID":CLIENT_ID, "Authorization": "Bearer " + ACCESS_TOKEN}


	# GET https://api.twitch.tv/helix/users: get User-IDs with this
	getidsurl = "https://api.twitch.tv/helix/users?" 
	getidsurl += "&".join(f"login={i}" for i in CHANNELS)

	response = requests.get(getidsurl, headers=headers)
	
	channelids = []
	for i in response.json()["data"]:
		channelids.append(i["id"])


	# GET https://api.twitch.tv/helix/videos: get videos using the IDs
	vodids = []
	for i in channelids:
		getvideourl = f"https://api.twitch.tv/helix/videos?user_id={i}"
		response = requests.get(getvideourl, headers=headers)

		print(json.dumps(response.json(), indent=4))

	#print(accesstokenrequest.json())


if __name__ == "__main__":
	main()
