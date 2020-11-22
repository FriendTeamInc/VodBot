from . import util
from .channel import Channel
from .video import Video

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
	if response.status_code != 200:
		util.exit_prog(5, "Failed to get user id's from ")
	
	channels = []
	for i in response.json()["data"]:
		channels.append(Channel(i))

	# GET https://api.twitch.tv/helix/videos: get videos using the IDs
	vods = []
	for i in channels:
		getvideourl = f"https://api.twitch.tv/helix/videos?user_id={i.id}&first=100"
		response = requests.get(getvideourl, headers=headers)
		# Some basic checks
		if response.status_code == 200:
			try:
				response = response.json()
			except ValueError:
				util.exit_prog(9, f"Could not parse response json for {i.login}'s videos.")
			
			# Add VODs to list to download later.
			for vod in response["data"]:
				if vod["thumbnail_url"] != "": # Live VODs don't have thumbnails
					vods.append(Video(vod))
	

	# Check what VODs we do and don't have.
	pass


if __name__ == "__main__":
	main()
