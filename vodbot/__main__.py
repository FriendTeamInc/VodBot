from . import util, __project__, __version__
from .channel import Channel
from .video import Video
from .clip import Clip
from .itd import download as itd_dl, worker as itd_work

import argparse
import subprocess
import json
import os
import requests
from pathlib import Path


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
		description="Downloads and processes VODs and clips from Twitch.tv channels.",
		epilog="VodBot (c) 2020-2021 Logan \"NotQuiteApex\" Hickok-Dickson")
	parser.add_argument("-v","--version", action="version",
		version=__project__ + " " + __version__)
	parser.add_argument("type", type=str, default="vods", nargs="?",
		help="Content type flag, can be \"vods\" or \"clips\".")
	parser.add_argument("channels", metavar="channel",
		type=str, default=[], nargs="*",
		help="Twitch.tv channel name to pull VODs from (optional, overrides config setting)")
	parser.add_argument("-c", type=str, dest="config",
		help="Location of the Twitch config file",
		default=str(vodbotdir / "conf.json"))
	parser.add_argument("-yt", type=str, dest="yt_config",
		help="Location of the YouTube config file (CURRENTLY UNUSED)",
		default=str(vodbotdir / "youtube-conf.json"))
	parser.add_argument("-d", type=str, dest="directory",
		help="Directory location to store VOD files in",
		default=None)
	
	args = parser.parse_args()

	# Initial error checks
	if not os.path.exists(args.config):
		util.make_twitch_conf(args.config)
		util.exit_prog(39,  f"Edit the config file at \"{args.config}\" before running again.")
	
	if args.directory is not None and not os.path.isdir(args.directory):
		util.exit_prog(54, f"Non-directory object \"{args.directory}\" must be removed before proceeding!")


	# Load the config and set up the access token
	print("Loading config...")
	(CLIENT_ID, CLIENT_SECRET, CHANNELS, VODS_DIR, CLIPS_DIR) = util.load_twitch_conf(args.config)
	print("Logging in to Twitch.tv...")
	ACCESS_TOKEN = util.get_access_token(CLIENT_ID, CLIENT_SECRET)
	HEADERS = {"Client-ID": CLIENT_ID, "Authorization": "Bearer " + ACCESS_TOKEN}

	# If command line has channels to watch instead, use those instead of the config ones.
	if len(args.channels) != 0:
		CHANNELS = args.channels
	
	# If argparse has a specific directory for vods, use that. Otherwise default to conf.
	# Also select "contentnoun" for making certain prints make sense.
	contentnoun = ""
	if args.directory is None:
		if args.type == "vods":
			args.directory = VODS_DIR
			contentnoun = "VOD"
		elif args.type == "clips":
			args.directory = CLIPS_DIR
			contentnoun = "Clip"
		else:
			util.exit_prog(85, f"Unknown content type \"{args.type}\".")
	
	# Setup directories for videos, config, and temp
	util.make_dir(args.directory)
	util.make_dir(str(vodbotdir))
	util.make_dir(str(vodbotdir / "temp"))

	print()

	# GET https://api.twitch.tv/helix/users: get User-IDs with this
	print("Getting User ID's...")
	getidsurl = "https://api.twitch.tv/helix/users?" 
	getidsurl += "&".join(f"login={i}" for i in CHANNELS)
	resp = requests.get(getidsurl, headers=HEADERS)
	# Some basic checks
	if resp.status_code != 200:
		util.exit_prog(5, f"Failed to get user ID's from Twitch. Status: {response.status_code}")
	try:
		resp = resp.json()
	except ValueError:
		util.exit_prog(12, f"Could not parse response json for user ID's.")
	
	# Make channel objects and store them in a list
	channels = []
	for i in resp["data"]:
		channels.append(Channel(i))

	# GET https://api.twitch.tv/helix/videos: get list of videos using the channel IDs
	vods = []
	
	# Switch between the two API endpoints.
	getvideourl = None
	if args.type == "vods":
		getvideourl = "https://api.twitch.tv/helix/videos?user_id={video_id}&first=100&type=archive"
	elif args.type == "clips":
		getvideourl = "https://api.twitch.tv/helix/clips?broadcaster_id={video_id}&first=100"

	for i in channels:
		print(f"Getting {contentnoun} list for {i.display_name}...")

		pagination = ""

		while True:
			# generate URL
			url = getvideourl.format(video_id=i.id)
			if pagination != "":
				url += "&after=" + pagination
			response = requests.get(url, headers=HEADERS)

			# Some basic checks
			if response.status_code != 200:
				util.exit_prog(5, f"Failed to get {contentnoun} data from Twitch. Status: {response.status_code}")
			try:
				response = response.json()
			except ValueError:
				util.exit_prog(9, f"Could not parse response json for {i.display_name}'s {contentnoun}s.")
			
			# Break out if we went through all the clips
			if len(response["data"]) == 0:
				break

			# Add VODs to list to download later.
			for vod in response["data"]:
				# We need to ignore live VOD's
				# Live VODs don't have thumbnails
				if vod["thumbnail_url"] != "":
					if args.type == "vods":
						vods.append(Video(vod))
					elif args.type == "clips":
						vods.append(Clip(vod))
			
			# If there's no other cursors, let's break.
			if "cursor" in response["pagination"]:
				pagination = response["pagination"]["cursor"]
			else:
				break

	print()
	print(f"Checking for existing {contentnoun}...")
	print()

	# Check what VODs we do and don't have.
	voddir = Path(args.directory)
	existingvods = []
	
	for channel in channels:
		channeldir = voddir / channel.display_name.lower()
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
	print(f"Total number of {contentnoun}s to download: {len(vodstodownload)}.")
	for vod in vodstodownload:
		# Print if we're on to a new user.
		if previouschannel != vod.user_id:
			previouschannel = vod.user_id
			print(f"\n\nDownloading {vod.user_name}'s {contentnoun}s")

		# Generate path for video
		pogdir = voddir / vod.user_name.lower()
		filename = str(pogdir / f"{vod.created_at}_{vod.id}.mkv".replace(":", ";"))

		# Write video data and handle exceptions
		# If successful, write the meta file
		try:
			if isinstance(vod, Video): # Download video
				itd_dl.dl_video(vod.id, filename, 20)
			elif isinstance(vod, Clip): # Download clip
				itd_dl.dl_clip(vod.id, filename)
		except itd_dl.JoiningFailed:
			print(f"VOD `{vod.id}` joining failed! Preserving files...")
		except itd_work.DownloadFailed:
			print(f"Clip `{vod.id}` download failed!")
		else:
			vod.write_meta(str(pogdir / (vod.id + ".meta")))
	
	print("\n\nAll done, goodbye!")
	

if __name__ == "__main__":
	deffered_main()
