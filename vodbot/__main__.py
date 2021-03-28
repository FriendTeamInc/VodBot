from . import util, __project__, __version__
from .channel import Channel
from .video import Video
from .clip import Clip
from .itd import download as itd_dl, worker as itd_work
from .printer import cprint, colorize

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

	titletext = colorize(f"#fM#l* VodBot {__version__} (c) 2020-21 Logan \"NotQuiteApex\" Hickok-Dickson *#r")

	# Process arguments
	parser = argparse.ArgumentParser(
		description="Downloads and processes VODs and clips from Twitch.tv channels.",
		epilog=titletext)
	parser.add_argument("-v","--version", action="version", version=titletext)
	parser.add_argument("type", type=str, default="vods", nargs="?",
		help="content type flag, can be \"vods\" or \"clips\"; defaults to \"vods\"")
	parser.add_argument("channels", metavar="channel", type=str, default=[], nargs="*",
		help="twitch.tv channel name to pull VODs from; optional, defaults to config")
	parser.add_argument("-c", type=str, dest="config",
		help="location of the Twitch config file", default=str(vodbotdir / "conf.json"))
	parser.add_argument("-yt", type=str, dest="yt_config",
		help="location of the YouTube config file (CURRENTLY UNUSED)",
		default=str(vodbotdir / "youtube-conf.json"))
	parser.add_argument("-d", type=str, dest="directory",
		help="directory location to store the content files in", default=None)
	
	args = parser.parse_args()

	print(titletext)

	# Initial error checks
	if not os.path.exists(args.config):
		util.make_twitch_conf(args.config)
		util.exit_prog(39,  f"Edit the config file at \"{args.config}\" before running again.")
	
	if args.directory is not None and not os.path.isdir(args.directory):
		util.exit_prog(54, f"Non-directory object \"{args.directory}\" must be removed before proceeding!")


	# Load the config and set up the access token
	cprint("#dLoading config...", end=" ")
	(CLIENT_ID, CLIENT_SECRET, CHANNELS, VODS_DIR, CLIPS_DIR) = util.load_twitch_conf(args.config)
	cprint("Logging in to Twitch.tv...", end=" ")
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
	voddir = Path(args.directory)
	util.make_dir(str(vodbotdir))
	util.make_dir(str(vodbotdir / "temp"))

	# GET https://api.twitch.tv/helix/users: get User-IDs with this
	cprint("Getting User ID's...#r")
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
	vodcount = 0
	
	# Switch between the two API endpoints.
	getvideourl = None
	if args.type == "vods":
		getvideourl = "https://api.twitch.tv/helix/videos?user_id={video_id}&first=100&type=archive"
	elif args.type == "clips":
		getvideourl = "https://api.twitch.tv/helix/clips?broadcaster_id={video_id}&first=100"

	for channel in channels:
		cprint(f"Getting #fM#l{contentnoun}#r list for #fY#l{channel.display_name}#r...", end=" ")

		allvods = []

		# Deal with pagination
		pagination = ""
		while True:
			# generate URL
			url = getvideourl.format(video_id=channel.id)
			if pagination != "":
				url += "&after=" + pagination
			response = requests.get(url, headers=HEADERS)

			# Some basic checks
			if response.status_code != 200:
				util.exit_prog(5, f"Failed to get {contentnoun} data from Twitch. Status: {response.status_code}")
			try:
				response = response.json()
			except ValueError:
				util.exit_prog(9, f"Could not parse response json for {channel.display_name}'s {contentnoun}s.")
			
			# Break out if we went through all the clips
			if len(response["data"]) == 0:
				break

			# Add VODs to list to download later.
			for vod in response["data"]:
				# We need to ignore live VOD's
				# Live VODs don't have thumbnails
				if vod["thumbnail_url"] != "":
					if args.type == "vods":
						allvods.append(Video(vod))
					elif args.type == "clips":
						allvods.append(Clip(vod))
			
			# If there's no other cursors, let's break.
			if "cursor" in response["pagination"]:
				pagination = response["pagination"]["cursor"]
			else:
				break
		
		# Check for existing videos
		existingvods = []
		channel_dir = voddir / channel.display_name.lower()
		util.make_dir(channel_dir)
		for _, _, files in os.walk(str(channel_dir)):
			for file in files:
				filename = file.split(".")
				if len(filename) > 1 and filename[1] == "meta":
					if any(filename[0] == x.id for x in allvods):
						existingvods.append(filename[0])
		
		for vod in allvods:
			if not any(vod.id == x for x in existingvods):
				vods.append(vod)

		# Print videos found
		cprint(f"#fC#l{len(vods) - vodcount} #fM#l{contentnoun}s#r")
		vodcount = len(vods)

	cprint(f"Total #fM#l{contentnoun}s#r: #fC#l{len(vods)}#r")

	# Download all the VODs we need.
	previouschannel = None
	for vod in vods:
		# Print if we're on to a new user.
		if previouschannel != vod.user_id:
			previouschannel = vod.user_id
			cprint(f"\nDownloading #fY#l{vod.user_name}#r's #fM#l{contentnoun}s#r...")

		# Generate path for video
		pogdir = voddir / vod.user_name.lower()
		filename = str(pogdir / f"{vod.created_at}_{vod.id}.mkv".replace(":", ";"))

		# Write video data and handle exceptions
		# If successful, write the meta file
		failed = False
		try:
			if isinstance(vod, Video): # Download video
				itd_dl.dl_video(vod.id, filename, 20)
			elif isinstance(vod, Clip): # Download clip
				itd_dl.dl_clip(vod.id, filename)
		except itd_dl.JoiningFailed:
			cprint(f"#fR#lVOD `{vod.id}` joining failed! Preserving files...#r")
			failed = True
		except itd_work.DownloadFailed:
			cprint(f"Download failed! Skipping...#r")
			failed = True
		except itd_work.DownloadCancelled:
			cprint(f"\n#fR#l{contentnoun} download cancelled.#r")
			raise KeyboardInterrupt()
		
		if not failed:
			vod.write_meta(str(pogdir / (vod.id + ".meta")))
	
	print("\n\nAll done, goodbye!")
	

if __name__ == "__main__":
	deffered_main()
