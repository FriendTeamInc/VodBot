from . import util, twitch, __project__, __version__
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
	parser = argparse.ArgumentParser(description="Downloads and processes VODs and clips from Twitch.tv channels.",
		epilog=titletext)
	parser.add_argument("-v","--version", action="version", version=titletext)
	parser.add_argument("-c", type=str, dest="config",
		help="location of the Twitch config file",
		default=str(vodbotdir / "conf.json"))

	# Subparsers for different commands
	subparsers = parser.add_subparsers(title="command", help="command to run.", dest="command")

	# vodbot init
	initparse = subparsers.add_parser("init", description="Runs the setup process for VodBot", epilog=titletext)

	# vodbot pull <vods/clips/both> [channel ...]
	download = subparsers.add_parser("pull", description="Downloads VODs and/or clips.", epilog=titletext)
	download.add_argument("type", type=str, default="both", nargs="?",
		help='content type flag, can be "vods", "clips", or "both"; defaults to "both"')
	download.add_argument("channels", metavar="channel", type=str, default=[], nargs="*",
		help="twitch.tv channel name to pull VODs from; optional, defaults to config")

	# vodbot stage
	stager = subparsers.add_parser("stage", description="Stages sections of video to upload", epilog=titletext)
	stager_subparser = stager.add_subparsers(title="action", description='action for staging the video')
	# vodbot stage add <id> [--ss="0:0:0"] [--to="99:59:59"] [--title="Apex - BBT"] [--desc="PogChamp {streamer}\n{link}"]
	stager_add = stager_subparser.add_parser("add", description="adds a VOD or Clip to the staging area", epilog=titletext)
	stager_add.add_argument("id", type=str, help="id of the VOD or Clip to stage")
	# vodbot stage rm <id>
	stager_rm = stager_subparser.add_parser("rm", description="removes a VOD or Clip from the staging area", epilog=titletext)
	stager_rm.add_argument("id", type=str, help="id of the staged video data")
	# vodbot stage list [id]
	stager_list = stager_subparser.add_parser("list", description="lists info on staging area or staged items", epilog=titletext)
	stager_list.add_argument("id", type=str, help="id of the staged video data")
	
	args = parser.parse_args()

	print(args)

	# Initial error checks
	if not os.path.exists(args.config):
		util.make_twitch_conf("conf.json")
		util.exit_prog(39,  f"Edit the config file at \"{args.config}\" before running again.")

	
	# Handle commands
	if args.command == "init":
		pass
	elif args.command == "pull":
		download_twitch_video(args)
	elif args.command == "stage":
		pass
	elif args.command == "upload":
		pass

def download_twitch_video(args):
	# Load the config and set up the access token
	cprint("#dLoading config...", end=" ", flush=True)
	(CLIENT_ID, CLIENT_SECRET, CHANNEL_IDS, VODS_DIR, CLIPS_DIR) = util.load_twitch_conf(args.config)
	cprint("Logging in to Twitch.tv...", end=" ", flush=True)
	HEADERS = twitch.get_access_token(CLIENT_ID, CLIENT_SECRET)

	# If command line has channels to watch instead, use those instead of the config ones.
	if len(args.channels) != 0:
		CHANNELS = args.channels
	
	contentnoun = "video" # temp contentnoun until the rest is reworked
	
	# Setup directories for videos, config, and temp
	util.make_dir(args.directory)
	voddir = Path(args.directory)
	util.make_dir(str(vodbotdir))
	util.make_dir(str(vodbotdir / "temp"))

	# GET https://api.twitch.tv/helix/users: get User-IDs with this
	cprint("Getting User ID's...#r", flush=True)
	channels = twitch.get_channels(CHANNEL_IDS, HEADERS)

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
		cprint(f"Pulling #fM#l{contentnoun}#r list: #fY#l{channel.display_name}#r...", end=" ")

		allvods = twitch.get_channel_vods(channel, HEADERS)
		
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

	cprint(f"Total #fM#l{contentnoun}s#r to download: #fC#l{len(vods)}#r")

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
	
	cprint("\n#fM#l* All done, goodbye! *#r\n")
	

if __name__ == "__main__":
	deffered_main()
