from vodbot import util, twitch
from vodbot.itd import download as itd_dl, worker as itd_work
from vodbot.twitch import Vod, Clip

from pathlib import Path
from os import listdir
from os.path import isfile


# Default path
vodbotdir = util.vodbotdir


def run(args):
	download_twitch_video(args)


def download_twitch_video(args):
	# Load the config and set up the access token
	print("Loading config...", end=" ", flush=True)
	conf = util.load_conf(args.config)
	CHANNEL_IDS = conf["twitch_channels"]
	VODS_DIR = conf["vod_dir"]
	CLIPS_DIR = conf["clip_dir"]
	TEMP_DIR = conf["temp_dir"]
	LOG_LEVEL = conf["ffmpeg_loglevel"]
	PULL_CHAT = conf["pull_chat_logs"]

	# If channel arguments are provided, override config
	if args.channels:
		CHANNEL_IDS = args.channels
	
	print("Loading channel data...", flush=True)
	channels = twitch.get_channels(CHANNEL_IDS)
	
	contentnoun = "video" # temp contentnoun until the rest is reworked
	
	# Setup directories for videos and temp
	util.make_dir(TEMP_DIR)
	voddir = Path(VODS_DIR)
	util.make_dir(voddir)
	clipdir = Path(CLIPS_DIR)
	util.make_dir(clipdir)

	# Get list of videos using channel object ID's from Twitch API
	videos = []
	totalvods = 0
	totalclips = 0

	channel_print = None
	if args.type == "both":
		channel_print = "Pulling VOD & Clip list: {}..."
	elif args.type == "vods":
		channel_print = "Pulling VOD list: {}..."
	elif args.type == "clips":
		channel_print = "Pulling Clip list: {}..."

	for channel in channels:
		vods = None
		clips = None
		print(channel_print.format(channel.display_name), end=" ")

		# Grab list of VODs and check against existing VODs
		if args.type == "both" or args.type == "vods":
			folder = voddir / channel.login
			util.make_dir(folder)
			allvods = twitch.get_channel_vods(channel)
			vods = compare_existant_file(folder, allvods)
			totalvods += len(vods)

		# Grab list of Clips and check against existing Clips
		if args.type == "both" or args.type == "clips":
			folder = clipdir / channel.login
			util.make_dir(folder)
			allclips = twitch.get_channel_clips(channel)
			clips = compare_existant_file(folder, allclips)
			totalclips += len(clips)

		# Print content found and save it
		if args.type == "both":
			print(f"{len(vods)} VODs & {len(clips)} Clips")
			videos += vods
			videos += clips
		elif args.type == "vods":
			print(f"{len(vods)} VODs")
			videos += vods
		elif args.type == "clips":
			print(f"{len(clips)} Clips")
			videos += clips
			
	if args.type == "both":
		print(f"Total VODs to download: {totalvods}")
		print(f"Total Clips to download: {totalclips}")
		print(f"Total videos to download: {len(videos)}")
	elif args.type == "vods":
		print(f"Total VODs to download: {totalvods}")
	elif args.type == "clips":
		print(f"Total Clips to download: {totalclips}")

	# Download all the videos we need.
	previouschannel = None
	for vod in videos:
		# Print if we're on to a new user.
		if previouschannel != vod.user_id:
			previouschannel = vod.user_id
			print(f"\nDownloading {vod.user_name}'s {contentnoun}s...")

		# Generate path for video
		viddir = None
		contentnoun = None

		if isinstance(vod, Vod):
			viddir = voddir / vod.user_name.lower()
			contentnoun = "VOD"
		elif isinstance(vod, Clip):
			viddir = clipdir / vod.user_name.lower()
			contentnoun = "Clip"
		
		filepath = viddir / f"{vod.created_at}_{vod.id}".replace(":", ";")
		filename = str(filepath) + ".mkv"
		metaname = str(filepath) + ".meta"
		chatname = str(filepath) + ".chat"

		# Write video data and handle exceptions
		try:
			if isinstance(vod, Vod):
				# download chat
				if PULL_CHAT:
					itd_dl.dl_video_chat(vod, chatname)
					vod.has_chat = True
				# download video
				itd_dl.dl_video(vod, Path(TEMP_DIR), filename, 20, LOG_LEVEL)
				# write meta file
				vod.write_meta(metaname)
			elif isinstance(vod, Clip):
				# download clip
				itd_dl.dl_clip(vod, filename)
				# write meta file
				vod.write_meta(metaname)
		except itd_dl.JoiningFailed:
			print(f"VOD `{vod.id}` joining failed! Preserving files...")
		except itd_work.DownloadFailed:
			print(f"Download failed. Skipping...")
		except itd_work.DownloadCancelled:
			print(f"\n{contentnoun} download cancelled. Quiting...")
			raise KeyboardInterrupt()
	
	print("\nAll done, goodbye!\n")


def compare_existant_file(path, allvods):
	# Check for existing videos by finding the meta files
	existingvods = [f[:-5] for f in listdir(str(path)) if isfile(str(path/f)) and f[-4:]=="meta"]
	# Compare vods, if they arent downloaded (meta is missing) then we need to queue them
	result = [
		vod 
			for vod in allvods
			# we use two methods of detection, one for the new format and one for the old
			# this is so old archives don't get overwritten unecessarily
			# TODO: remove this in a future update after deprecation
			if not any(
				f"{vod.created_at}_{vod.id}".replace(":", ";") == x
				or vod.id == x for x in existingvods
					for x in existingvods
			)
		]
	return result
