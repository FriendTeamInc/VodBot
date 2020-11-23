from . import util
from .channel import Channel
from .video import Video

import subprocess
import json
import os
import requests
from pathlib import Path
from distutils.spawn import find_executable


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

	if find_executable("streamlink") is None:
		util.exit_prog(28, "Streamlink not found. Did you forget to install it?")


	# Load the config and set up the access token
	(CLIENT_ID, CLIENT_SECRET, CHANNELS) = util.load_conf(vodbotdir / "conf.json")
	ACCESS_TOKEN = util.get_access_token(CLIENT_ID, CLIENT_SECRET)
	HEADERS = {"Client-ID":CLIENT_ID, "Authorization": "Bearer " + ACCESS_TOKEN}


	# GET https://api.twitch.tv/helix/users: get User-IDs with this
	getidsurl = "https://api.twitch.tv/helix/users?" 
	getidsurl += "&".join(f"login={i}" for i in CHANNELS)
	response = requests.get(getidsurl, headers=HEADERS)
	# Some basic checks
	if response.status_code != 200:
		util.exit_prog(5, f"Failed to get user ID's from Twitch. Status: {response.status_code}")
	try:
		response = response.json()
	except ValueError:
		util.exit_prog(12, f"Could not parse response json for user ID's.")
	
	channels = []
	for i in response["data"]:
		channels.append(Channel(i))


	# GET https://api.twitch.tv/helix/videos: get videos using the IDs
	vods = []
	for i in channels:
		getvideourl = f"https://api.twitch.tv/helix/videos?user_id={i.id}&first=100"
		response = requests.get(getvideourl, headers=HEADERS)
		# Some basic checks
		if response.status_code != 200:
			util.exit_prog(5, f"Failed to get video data from Twitch. Status: {response.status_code}")
		try:
			response = response.json()
		except ValueError:
			util.exit_prog(9, f"Could not parse response json for {i.login}'s videos.")
			
		# Add VODs to list to download later.
		for vod in response["data"]:
			if vod["thumbnail_url"] != "": # Live VODs don't have thumbnails
				vods.append(Video(vod))
	

	# Check what VODs we do and don't have.
	voddir = vodbotdir / "vods"
	existingvods = []
	
	for channel in channels:
		channeldir = voddir / channel.login
		os.makedirs(str(channeldir), exist_ok=True)
		for _, _, files in os.walk(str(channeldir)):
			for file in files:
				filename = file.split(".")
				if len(filename) > 1 and filename[len(filename) - 1] == "meta":
					existingvods.append(filename[0])
	

	# Compare vods that do and don't exist, and add the non-existant ones to a list to download
	vodstodownload = []
	for vod1 in vods:
		exists = False
		for vod2 in existingvods:
			if vod1.id == vod2:
				exists = True
				break
		if not exists:
			vodstodownload.append(vod1)

	for vod in vodstodownload:
		filename = str(voddir / vod.user_name / f"{vod.created_at}_{vod.id}.mp4.temp")
		filename = filename.replace(":", ".")
		streamlinkcmd = [
			"streamlink",
			"--hls-segment-threads", str(10),
			("twitch.tv/videos/" + vod.id), "best",
			"-o", filename, "-f"
		]
		subprocess.run(streamlinkcmd)
		vod.write_meta(str(voddir / vod.user_name / (vod.id + ".meta")))
	
	print("Done!")
	

if __name__ == "__main__":
	try:
		main()
	except requests.exceptions.ConnectionError:
		util.exit_prog(-2, "Failed to connect to Twitch.")
	except KeyboardInterrupt:
		util.exit_prog(-1, "Interrupted.")
