# Pull, downloads VODs and Clips from Twitch.tv

from typing import List
from vodbot import util, twitch
from vodbot.itd import download as itd_dl, worker as itd_work
from vodbot.printer import cprint
from vodbot.itd.gql import set_client_id

from pathlib import Path
from os import listdir
from os.path import isfile


def run(args):
	# Load the config and set up the access token
	cprint("#r#dLoading config...#r", end=" ", flush=True)
	conf = util.load_conf(args.config)
	CHANNEL_IDS = conf.channels
	VODS_DIR = conf.directories.vods
	CLIPS_DIR = conf.directories.clips
	TEMP_DIR = conf.directories.temp
	LOG_LEVEL = conf.export.ffmpeg_loglevel
	PULL_CHAT = conf.pull.save_chat
	set_client_id(conf.pull.gql_client)
	
	cprint("#r#dLoading channel data...#r", end=" ", flush=True)
	# This function is actually useless, we don't need anything from it, just the channel login name which we already have.
	# TODO: remove this useless query entirely, nothing from it is used that we don't already have.
	channels: List[twitch.Channel] = twitch.get_channels([channel.username for channel in CHANNEL_IDS])
	for i, channel in enumerate(channels):
		channel.save_vods = CHANNEL_IDS[i].save_vods
		channel.save_clips = CHANNEL_IDS[i].save_clips
		channel.save_chat = CHANNEL_IDS[i].save_chat and PULL_CHAT
	
	cprint("#r#dChecking directories...#r", end=" ", flush=True)
	# Setup directories for videos and temp
	util.make_dir(TEMP_DIR)
	util.make_dir(VODS_DIR)
	util.make_dir(CLIPS_DIR)

	cprint("#r#dPulling video lists...#r", flush=True)
	# Get list of videos using channel object ID's from Twitch API
	totalvods = 0
	totalclips = 0
	atboth = args.type == "both"
	atvods = args.type == "vods"
	atclips = args.type == "clips"

	for channel in channels:
		if not channel.save_vods and not channel.save_chat and not channel.save_clips:
			continue

		cprint(f"#fY#l{channel.display_name}#r:", end=" ", flush=True)

		newvods = []
		if (atboth or atvods) and (channel.save_vods or channel.save_chat):
			folder = VODS_DIR / channel.login
			util.make_dir(folder)

			channelvods = twitch.get_channel_vods(channel)
			newvods = compare_existant_file(folder, channelvods)

			totalvods += len(newvods)
			cprint(f"#fC#l{len(newvods)} #fM#lVODs#r", end="", flush=True)
		
		if atboth:
			cprint(" & ", end="", flush=True)
		
		newclips = []
		if (atboth or atclips) and (channel.save_clips):
			folder = CLIPS_DIR / channel.login
			util.make_dir(folder)

			channelclips = twitch.get_channel_clips(channel)
			newclips = compare_existant_file(folder, channelclips)

			totalclips += len(newclips)
			cprint(f"#fC#l{len(newclips)} #fM#lClips#r", flush=True)
		
		channel.new_vods = newvods
		channel.new_clips = newclips
	
	if atboth:
		cprint(f"Total #fMVODs#r to pull: #fC#l{totalvods}#r")
		cprint(f"Total #fMClips#r to pull: #fC#l{totalclips}#r")
		cprint(f"Total #fMvideos#r to pull: #fC#l{totalvods+totalclips}#r")
	elif atvods:
		cprint(f"Total #fMVODs#r to pull: #fC#l{totalvods}#r")
	elif atclips:
		cprint(f"Total #fMClips#r to pull: #fC#l{totalclips}#r")

	# Download all the videos we need.
	cprint("#r#dPulling videos...#r", flush=True)
	for channel in channels:
		cprint(f"Pulling videos for #fY#l{channel.display_name}#r...")

		voddir = VODS_DIR / channel.login
		for vod in channel.new_vods:
			filepath = voddir / f"{vod.created_at}_{vod.id}".replace(":", ";")
			filename = str(filepath) + ".mkv"
			metaname = str(filepath) + ".meta"
			chatname = str(filepath) + ".chat"

			# download chat
			if channel.save_chat:
				itd_dl.dl_video_chat(vod, chatname)
				vod.has_chat = True
			# download video
			if channel.save_vods:
				try:
					itd_dl.dl_video(vod, Path(TEMP_DIR), filename, 20, LOG_LEVEL)
				except itd_dl.JoiningFailed:
					cprint(f"#fR#lVOD `{vod.id}` joining failed! Skipping...#r")
					continue
				except itd_work.DownloadFailed:
					cprint(f"#fR#lVOD `{vod.id}` download failed! Skipping...#r")
					continue
				except (itd_work.DownloadCancelled, KeyboardInterrupt):
					cprint(f"\n#fR#lVOD `{vod.id}` download cancelled. Exiting...#r")
					raise KeyboardInterrupt()
			# write meta file
			vod.write_meta(metaname)
		
		clipdir = CLIPS_DIR / channel.login
		for clip in channel.new_clips:
			filepath = clipdir / f"{clip.created_at}_{clip.id}".replace(":", ";")
			filename = str(filepath) + ".mkv"
			metaname = str(filepath) + ".meta"

			# download clip
			if channel.save_clips:
				try:
					itd_dl.dl_clip(clip, filename)
				except itd_work.DownloadFailed:
					cprint(f"#fR#lClip `{clip.id}` download failed! Skipping...#r")
				except (itd_work.DownloadCancelled, KeyboardInterrupt):
					cprint(f"\n#fR#lClip `{clip.id}` download cancelled. Exiting...#r")
					raise KeyboardInterrupt()
			# write meta file
			clip.write_meta(metaname)
	
	#cprint("\n#fM#l* All done, goodbye! *#r\n")


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
