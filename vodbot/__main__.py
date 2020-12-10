from . import util, __project__, __version__
from .channel import Channel
from .video import Video

import argparse
import subprocess
import json
import os
import requests
from pathlib import Path
from distutils.spawn import find_executable


def deffered_main():
	# Catch KeyboardInterrupts or connection failures, and report them cleanly
	try:
		main()
	except requests.exceptions.ConnectionError:
		util.exit_prog(-2, "Failed to connect to Twitch.")
	except KeyboardInterrupt:
		util.exit_prog(-1, "Interrupted by user.")


def main():
	# Default path
	vodbotdir = util.vodbotdir

	# Process arguments
	parser = argparse.ArgumentParser(
		description="Downloads and processes VODs from Twitch.tv channels.",
		epilog="VodBot (c) 2020 Logan \"NotQuiteApex\" Hickok-Dickson")
	parser.add_argument("-v","--version", action="version",
		version=__project__ + " " + __version__)
	parser.add_argument("channels", metavar="channel",
		type=str, default=[], nargs="*",
		help="Twitch.tv channel name to pull VODs from (optional, overrides config setting)")
	parser.add_argument("-c", type=str, dest="config",
		help="location of the config file",
		default=str(vodbotdir / "conf.json"))
	parser.add_argument("-d", type=str, dest="directory",
		help="directory location to store VOD files in",
		default=None)
	
	args = parser.parse_args()

	# Initial error checks
	if not os.path.exists(args.config):
		util.make_conf(args.config)
		util.exit_prog(39,  f"Edit the config file at \"{args.config}\" before running again.")
	
	if args.directory is not None and not os.path.isdir(args.directory):
		util.exit_prog(54, f"Non-directory object \"{args.directory}\" must be removed before proceeding!")

	if find_executable("streamlink") is None:
		util.exit_prog(28, "Streamlink not found. Did you forget to install it?")


	# Load the config and set up the access token
	(CLIENT_ID, CLIENT_SECRET, CHANNELS, VODS_DIR) = util.load_conf(args.config)
	ACCESS_TOKEN = util.get_access_token(CLIENT_ID, CLIENT_SECRET)
	HEADERS = {"Client-ID": CLIENT_ID, "Authorization": "Bearer " + ACCESS_TOKEN}

	# If command line has channels to watch instead, use those instead of the config ones.
	if len(args.channels) != 0:
		CHANNELS = args.channels
	
	# If argparse has a specific directory for vods, use that. otherwise default to conf.
	if args.directory is None:
		args.directory = VODS_DIR
	
	util.make_dir(args.directory)


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
	
	# Make channel objects and store them in a list
	channels = []
	for i in response["data"]:
		channels.append(Channel(i))

	# GET https://api.twitch.tv/helix/videos: get videos using the channel IDs
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
	voddir = Path(args.directory)
	existingvods = []
	
	for channel in channels:
		channeldir = voddir / channel.login.lower()
		os.makedirs(str(channeldir), exist_ok=True)
		for _, _, files in os.walk(str(channeldir)):
			for file in files:
				filename = file.split(".")
				if len(filename) > 1 and filename[1] == "meta":
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

	# Download all the VODs we need.
	previouschannel = None
	for vod in vodstodownload:
		if previouschannel != vod.user_id:
			previouschannel = vod.user_id
			print(f"\n\nDownloading {vod.user_name}'s Vods\n")

		pogdir = voddir / vod.user_name.lower()
		filename = str(pogdir / f"{vod.created_at}_{vod.id}.mkv".replace(":", ";"))
		
		streamlinkcmd = [
			"streamlink",
			"--hls-segment-threads", str(10),
			("twitch.tv/videos/" + vod.id), "best",
			"-o", filename, "-f"
		]
		subprocess.run(streamlinkcmd)

		vod.write_meta(str(pogdir / (vod.id + ".meta")))
	
	print("Done!")
	

if __name__ == "__main__":
	deffered_main()
