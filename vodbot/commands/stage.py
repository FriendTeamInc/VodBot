# Staging, where videos get staged and set up with metadata to upload

import vodbot.util as util
from vodbot.printer import cprint, colorize

import json
import pytz
from datetime import datetime
from pathlib import Path
from os import walk as os_walk
from os import listdir
from os.path import isfile, isdir


class StageData():
	def __init__(self, title, description, ss, to, filename):
		self.title = title
		self.desc = description
		self.ss = ss
		self.to = to
		self.filename = filename
		self.hash = str(hex(hash(self)))[2:][:8]
	
	def __hash__(self):
		return hash((self.title, self.desc, self.ss, self.to, self.filename))


class CouldntFindVideo(Exception):
	pass

def find_video_by_id(vid_id, VODS_DIR, CLIPS_DIR):
	"""
	Check where a video is by its ID

	:param vid_id: ID of the video.
	:returns: A tuple containing the path to the video file and the meta file.
	"""
	
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
			if vid_id in metas:
				metajson = None
				try:
					with open(str(folder / (vid_id+".meta"))) as f:
						metajson = json.load(f)
					filename = folder / f"{metajson['created_at']}_{vid_id}.mkv".replace(":", ";")
					return (filename, metajson, "VOD" if dir_t[1] == VODS_DIR_PATH else "Clip")
				except FileNotFoundError:
					pass
				except ValueError:
					pass
	
	raise CouldntFindVideo()

def check_time(prefix, inputstring, resp):
	output = resp
	checkedonce = False

	while True:
		if checkedonce or output == None:
			output = input(colorize(inputstring))
		checkedonce = True

		if output == "":
			if prefix == "Start time":
				return "0:0:0"
			elif prefix == "End time":
				return "EOF"

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
		else:
			timelist.insert(0, "0")
		
		if len(intime) == 3:
			hours = intime[-3]
			try:
				hours = int(hours)
			except ValueError:
				cprint(f"#fR{prefix}: Hours does not appear to be a number.#r")
				continue
			timelist.insert(0, str(hours))
		else:
			timelist.insert(0, "0")
		
		output = ":".join(timelist)
		break

	return output

def run(args):
	if args.action == "add":
		conf = util.load_twitch_conf(args.config)
		VODS_DIR = conf["vod_dir"]
		CLIPS_DIR = conf["clip_dir"]

		filename = None
		metadata = None
		videotype = None

		try:
			(filename, metadata, videotype) = find_video_by_id(args.id, VODS_DIR, CLIPS_DIR)
		except CouldntFindVideo:
			util.exit_prog(13, f'Could not find video with ID "{args.id}"')
		
		cprint(f"Found #fM#l{videotype}#r #fM{args.id}#r from #fY#l{metadata['user_name']}#r.")

		# Get any necessary input
		if args.title == None:
			args.title = ""
			while args.title == "":
				args.title = input(colorize("#fW#lTitle of the Video#r #d(--title)#r: "))
				if args.title == "":
					cprint("#fRTitle cannot be blank.#r")

		args.ss = check_time("Start time", "#fW#lStart time of the Video#r #d(--ss, default 0:0:0)#r: ", args.ss)
		args.to = check_time("End time", "#fW#lEnd time of the Video#r #d(--to, default EOF)#r: ", args.to)

		if args.desc == None:
			args.desc = ""
			while args.desc == "":
				args.desc = input(colorize("#fW#lDescription of Video#r #d(--desc)#r: "))
				if args.desc == "":
					cprint("#fRDescription cannot be blank.#r")

		# Generate dict to use for formatting
		est = pytz.timezone("US/Eastern") # TODO: allow config to change this
		utc = pytz.utc
		date = datetime.strptime(metadata["created_at"], "%Y-%m-%dT%H:%M:%SZ")
		date.replace(tzinfo=utc)
		date.astimezone(est)
		formatdict = {
			"date": date.astimezone(est).strftime("%Y/%m/%d"),
			"link": f"https://twitch.tv/{metadata['user_name']}",
			"streamer": metadata["user_name"],
		}
		formatdict["twatch"] = f"-- Watch live at {formatdict['link']}"

		# Format the description
		args.desc = args.desc.format(**formatdict).replace("\\n", "\n")

		shortfilename = str(filename).replace(VODS_DIR, "...").replace(CLIPS_DIR, "...")

		stage = StageData(args.title, args.desc, args.ss, args.to, str(filename))
		shortfile = stage.filename.replace(VODS_DIR, "...").replace(CLIPS_DIR, "...")

		print()
		cprint(f"#r`#fY{stage.title}#r` #d({stage.ss} - {stage.to})#r")
		cprint(f"#d''' {shortfile}#r\n#fY{stage.desc}#r\n#d''' {stage.hash}#r")

	elif args.action == "edit":
		pass
	elif args.action == "rm":
		pass
	elif args.action == "list":
		pass