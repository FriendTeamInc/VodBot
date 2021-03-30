# Staging, where videos get staged and set up with metadata to upload

import vodbot.util as util
from vodbot.printer import cprint

import json
import pytz
from datetime import datetime
from pathlib import Path
from os import walk as os_walk
from os import listdir
from os.path import isfile, isdir


class StageData():
	def __init__(self, ):
		pass
	
	def __hash__(self):
		return hash(())


class CouldntFindVideo(Exception):
	pass

def find_video_by_id(id, config):
	"""
	Check where a video is by its ID

	:param id: ID of the video.
	:returns: A tuple containing the path to the video file and the meta file.
	"""
	# Check where the video is by ID
	(CLIENT_ID, CLIENT_SECRET, CHANNEL_IDS, VODS_DIR, CLIPS_DIR) = util.load_twitch_conf(config)

	VODS_DIR_PATH = Path(VODS_DIR)
	CLIPS_DIR_PATH = Path(CLIPS_DIR)
	vod_dirs = [d for d in listdir(VODS_DIR) if isdir(str(VODS_DIR_PATH / d))]
	clip_dirs = [d for d in listdir(CLIPS_DIR) if isdir(str(CLIPS_DIR_PATH / d))]

	filename = None
	metaname = None
	
	directories = [(vod_dirs, VODS_DIR_PATH), (clip_dirs, CLIPS_DIR_PATH)]

	for dir_t in directories:
		for channel in dir_t[0]:
			folder = dir_t[1] / Path(channel)
			metas = [m[:-5] for m in listdir(str(folder)) if isfile(str(folder / Path(m))) and m[-4:]=="meta"]
			if id in metas:
				metajson = None
				try:
					with open(str(folder / (id+".meta"))) as f:
						metajson = json.load(f)
					filename = folder / f"{metajson['created_at']}_{id}".replace(":", ";")
					return (filename, metajson, "VOD" if dir_t[0] == VODS_DIR_PATH else "Clip")
				except FileNotFoundError:
					pass
				except ValueError:
					pass
	
	raise CouldntFindVideo()

def check_time(prefix, inputstring, resp):
	output = resp
	checkedonce = False

	while True:
		if checkedonce:
			output = input(inputstring)
		checkedonce = True

		if output == "":
			return "0:0:0"

		intime = output.split(":")
		timelist = []
		seconds = None
		minutes = None
		hours = None

		if len(intime) > 3:
			cprint(f"#fR{prefix}: Time cannot have more than 3 units.#r")
			continue
		
		if len(intime) >= 1:
			seconds = intime[-1]
			try:
				seconds = int(seconds)
			except ValueError:
				cprint(f"#fR{prefix}: Seconds does not appear to be a number.#r")
				continue
			if seconds > 59 or seconds < 0:
				cprint(f"#fR{prefix}: Seconds must be in the range of 0 to 59.#r")
				continue
			timelist.insert(0, str(seconds))
		
		if len(intime) >= 2:
			minutes = intime[-2]
			try:
				minutes = int(minutes)
			except ValueError:
				cprint(f"#fR{prefix}: Minutes does not appear to be a number.#r")
				continue
			if minutes > 59 or minutes < 0:
				cprint(f"#fR{prefix}: Minutes must be in the range of 0 to 59.#r")
				continue
			timelist.insert(0, str(minutes))
		
		if len(intime) == 3:
			hours = intime[-3]
			try:
				hours = int(hours)
			except ValueError:
				cprint(f"#fR{prefix}: Hours does not appear to be a number.#r")
				continue
			timelist.insert(0, str(hours))
		
		output = ":".join(timelist)
		break

	return output

def run(args):
	if args.action == "add":
		filename = None
		metadata = None
		videotype = None

		try:
			(filename, metadata, videotype) = find_video_by_id(args.id, args.config)
		except CouldntFindVideo:
			util.exit_prog(13, f'Could not find video with ID "{args.id}"')
		
		cprint(f"Found #fM#l{videotype}#r #fM{args.id}#r from #fY#l{metadata['user_name']}#r.")

		# Get any necessary input
		if args.title == "":
			args.title = ""
			while args.title == "":
				args.title = input("Title of the Video (--title): ")
				if args.title == "":
					cprint("#fRTitle cannot be blank.#r")

		args.ss = check_time("Start time", "Start time of the Video (--ss, default 0:0:0): ", args.ss)
		args.to = check_time("End time", "End time of the Video (--to, default EOF): ", args.to)

		if args.desc == "":
			args.desc = ""
			while args.desc == "":
				args.desc = input("Description of Video (--desc): ")
				if args.desc == "":
					cprint("#fRDescription cannot be blank.#r")
		
		print(args)

		# Generate dict to use for formatting

		# Format the description


	elif args.action == "edit":
		pass
	elif args.action == "rm":
		pass
	elif args.action == "list":
		pass