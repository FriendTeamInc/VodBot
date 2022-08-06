# Staging, where videos get staged and set up with metadata to upload

import vodbot.util as util
from vodbot.printer import cprint, colorize

import re
import sys
import json
import string
import random
import datetime
from datetime import datetime, timezone, timedelta
from pathlib import Path
from os import remove as os_remove, listdir as os_listdir
from os.path import isfile, isdir
from typing import List, Tuple


# Default path
vodbotdir = util.vodbotdir

DISALLOWED_CHARACTERS = [chr(x) for x in range(10)] + [chr(x) for x in range(11,32)] # just in case...


class VideoSlice():
	def __init__(self, video_id: str, ss: str, to: str, filepath: str):
		self.video_id = video_id
		self.ss = ss
		self.to = to
		self.filepath = filepath
	
	def get_as_dict(self):
		return {"id":self.video_id, "ss":self.ss, "to":self.to, "path":str(self.filepath)}


class StageData():
	def __init__(self, streamers: List[str], title: str, desc: str, slices: List[VideoSlice], datestring: str, cid=None):
		for x in DISALLOWED_CHARACTERS:
			title = title.replace(x, "_")
		self.title = title
		self.desc = desc
		self.streamers = streamers
		self.datestring = datestring
		self.slices = slices

		if cid is None:
			self.gen_new_id()
		else:
			self.id = cid
	
	def __repr__(self):
		return f"StageData(\"{self.title}\", {self.id})"
	
	def write_stage(self, filename):
		with open(filename, "w") as f:
			jsondump = {
				"streamers": self.streamers,
				"title": self.title,
				"desc": self.desc,
				"datestring": self.datestring,
				"id": self.id,
				"slices": []
			}

			for vid in self.slices:
				jsondump["slices"] += [vid.get_as_dict()]

			json.dump(jsondump, f)
	
	def gen_new_id(self):
		self.id = ""
		for _ in range(4):
			self.id += random.choice(string.ascii_lowercase + string.digits)
	
	@staticmethod
	def load_from_json(data: dict) -> 'StageData':
		slices = [VideoSlice(v["id"], v["ss"], v["to"], v["path"]) for v in data["slices"]]
		streamers = data["streamers"]
		title = data["title"]
		desc = data["desc"]
		datestr = data["datestring"]
		_id = data["id"]

		new_data = StageData(streamers=streamers, title=title, desc=desc, datestring=datestr, slices=slices)
		new_data.id = _id

		return new_data
	
	@staticmethod
	def load_from_id(stagedir: Path, sid: str) -> 'StageData':
		jsonread = None
		try:
			with open(str(stagedir / (sid+".stage"))) as f:
				jsonread = json.load(f)
		except FileNotFoundError:
			util.exit_prog(46, f'Could not find stage "{sid}". (FileNotFound)')
		except KeyError:
			util.exit_prog(46, f'Could not parse stage "{sid}" as JSON. Is this file corrupted?')
		
		return StageData.load_from_json(jsonread)
	
	@staticmethod
	def load_all_stages(stagedir: Path) -> List['StageData']:
		stages = []
		for d in os_listdir(str(stagedir)):
			if isfile(str(stagedir / d)) and d[-5:] == "stage":
				stages.append(StageData.load_from_id(stagedir, d[:-6]))
		
		return stages


class CouldntFindVideo(Exception):
	pass


def create_format_dict(conf, streamers, utcdate=None, truedate=None):
	thistz = None
	datestring = None
	if truedate == None:
		try:
			# https://stackoverflow.com/a/37097784/13977827
			sign, hours, minutes = re.match('([+\-]?)(\d{2})(\d{2})', conf['stage_timezone']).groups()
			sign = -1 if sign == '-' else 1
			hours, minutes = int(hours), int(minutes)

			thistz = timezone(sign * timedelta(hours=hours, minutes=minutes))
		except:
			util.exit_prog(73, f"Unknown timezone {conf['stage_timezone']}")
		date = datetime.strptime(utcdate, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
		datestring = date.astimezone(thistz).strftime("%Y/%m/%d")
	else:
		datestring = truedate
	
	formatdict = {
		"date": datestring,
		"link": f"https://twitch.tv/{streamers[0]}",
		"streamer": streamers[0],
		"links": " ".join([f"https://twitch.tv/{s}" for s in streamers]),
		"streamers": streamers,
	}

	# first and second pass format
	for x in range(2):
		for item, fmtstring in conf["stage_format"].items():
			try:
				fmtstring = fmtstring.format(**formatdict)
				if "<" in fmtstring or ">" in fmtstring:
					util.exit_prog(80, "Format strings cannot contain angled brackets (\"<\", \">\").")
				if any((c in DISALLOWED_CHARACTERS) for c in fmtstring):
					util.exit_prog(82, "Format strings cannot contain control characters.")

				formatdict[item] = fmtstring
			except KeyError as err:
				# ignore errors on first pass
				if x == 1:
					util.exit_prog(81, f"Format failed: `{err}`.")

	return formatdict, datestring


def find_video_by_id(vid_id, VODS_DIR, CLIPS_DIR):
	"""
	Check where a video is by its ID

	:param vid_id: ID of the video.
	:returns: A tuple containing the path to the video file and the meta file.
	"""
	
	VODS_DIR_PATH = Path(VODS_DIR)
	CLIPS_DIR_PATH = Path(CLIPS_DIR)
	vod_dirs = [d for d in os_listdir(VODS_DIR) if isdir(str(VODS_DIR_PATH / d))]
	clip_dirs = [d for d in os_listdir(CLIPS_DIR) if isdir(str(CLIPS_DIR_PATH / d))]

	filename = None
	
	directories = [(vod_dirs, VODS_DIR_PATH), (clip_dirs, CLIPS_DIR_PATH)]

	for dir_t in directories:
		for channel in dir_t[0]:
			folder = dir_t[1] / Path(channel)
			metas = [m[:-5] for m in os_listdir(str(folder)) if isfile(str(folder / Path(m))) and m[-4:]=="meta"]
			metas = [m for m in metas if vid_id in m] # multiple types of id's exist, so we have to soft match
			if len(metas) > 0:
				vid_id = metas[0] # use first result of matching
				metajson = None
				try:
					with open(str(folder / (vid_id+".meta"))) as f:
						metajson = json.load(f)
					filename = folder / f"{metajson['created_at']}_{metajson['id']}.mkv".replace(":", ";")
					return (filename, metajson, "VOD" if dir_t[1] == VODS_DIR_PATH else "Clip")
				except FileNotFoundError:
					pass
				except ValueError:
					pass
	
	raise CouldntFindVideo()


def check_stage_id(stage_id, STAGE_DIR):
	STAGE_DIR_PATH = Path(STAGE_DIR)

	stages = [m[:-6] for m in os_listdir(STAGE_DIR) if isfile(str(STAGE_DIR_PATH / Path(m))) and m[-5:]=="stage"]

	return stage_id in stages


def check_time(prefix, resp, default=None):
	output = resp
	checkedonce = False

	while True:
		if checkedonce or not output:
			a = 'ss' if prefix=='Start' else 'to'
			t = '0:0:0' if prefix=='Start' else 'EOF'
			f = f"#fW#l{prefix} time of the Video#r #d(--{a}, default {t})#r: "
			output = input(colorize(f))
		checkedonce = True

		if output == "":
			if prefix == "Start":
				return default if default != None else "0:0:0"
			elif prefix == "End":
				return default if default != None else "EOF"

		intime = output.split(":")
		timelist = []
		seconds = None
		minutes = None
		hours = None

		if len(intime) > 3:
			cprint(f"#fR{prefix} time: Time cannot have more than 3 units.#r")
			continue
		
		if len(intime) >= 1:
			seconds = intime[-1]
			try:
				seconds = int(seconds)
			except ValueError:
				cprint(f"#fR{prefix} time: Seconds does not appear to be a number.#r")
				continue
			if seconds > 59 or seconds < 0:
				cprint(f"#fR{prefix} time: Seconds must be in the range of 0 to 59.#r")
				continue
			timelist.insert(0, str(seconds))
		
		if len(intime) >= 2:
			minutes = intime[-2]
			try:
				minutes = int(minutes)
			except ValueError:
				cprint(f"#fR{prefix} time: Minutes does not appear to be a number.#r")
				continue
			if minutes > 59 or minutes < 0:
				cprint(f"#fR{prefix} time: Minutes must be in the range of 0 to 59.#r")
				continue
			timelist.insert(0, str(minutes))
		else:
			timelist.insert(0, "0")
		
		if len(intime) == 3:
			hours = intime[-3]
			try:
				hours = int(hours)
			except ValueError:
				cprint(f"#fR{prefix} time: Hours does not appear to be a number.#r")
				continue
			timelist.insert(0, str(hours))
		else:
			timelist.insert(0, "0")
		
		output = ":".join(timelist)
		break

	return output


def check_streamers(default=None) -> List[str]:
	streamers = ""
	while not streamers:
		streamers = input(colorize(f"#fW#lWho was in the VOD#r #d(default `{', '.join(default)}`, csv)#r: "))

		if streamers == "":
			streamers = default
		else:
			streamers = streamers.replace(" ", "").split(",")
			for streamer in streamers:
				if len(streamer) == 0:
					cprint("#l#fRMissing streamer name!#r")
					streamers = ""
					break
				
				if not all((c.isalnum() or c=="_") for c in streamer):
					if len(streamer) == 0:
						cprint("#l#fRStreamer names must be alphanumeric with underscores!#r")
						streamers = ""
						break
	
	return streamers


RESERVED_NAMES = [
	"\\0", "CON", "PRN", "AUX", "NUL",
	"COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
	"LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
]
def check_title(default=None):
	title = default
	if not title:
		title = ""
		while title == "":
			title = input(colorize("#fW#lTitle of the Video#r #d(--title)#r: "))
			# blank title
			if title == "":
				cprint("#fRTitle cannot be blank.#r")
				continue
			# reserved names
			# upper is necessary because windows still reads lowercase versions as reserved
			if title.upper() in RESERVED_NAMES :
				cprint("#fRTitle cannot be a reserved name such as NUL, COM1, etc.#r")
				title = ""
				continue

			if any((c in DISALLOWED_CHARACTERS) for c in title):
				cprint("#fRTitle cannot use control characters.#r")
				title = ""
				continue
	
	return title


def check_description(formatdict, inputdefault=None):
	desc = ""

	if inputdefault:
		try:
			inputdefault = inputdefault.format(**formatdict).replace("\\n", "\n")
			desc = inputdefault
		except KeyError as err:
			cprint(f"#fRDescription format error from default: {err}.#r")
			desc = ""

	while desc == "":
		desc = input(colorize("#fW#lDescription of Video#r #d(--desc)#r: "))
		if desc == "":
			cprint("#fRDescription cannot be blank.#r")
			continue

		# Format the description
		try:
			desc = desc.format(**formatdict).replace("\\n", "\n")
		except KeyError as err:
			cprint(f"#fRDescription format error: {err}.#r")
			desc = ""
			continue

		if "<" in desc or ">" in desc or any((c in DISALLOWED_CHARACTERS) for c in desc):
			cprint(f"#fRDescription cannot contain angled brackets (\"<\", \">\") or control characters.#r")
			desc = ""
			continue

		if len(desc.encode("utf-8")) > 5000:
			cprint(f"#fRDescription cannot be longer than 5000 unicode characters (codepoints).#r")
			desc = ""
			continue

	return desc

# time in seconds to a timestamp string
def int_to_timestamp(i:int) -> str:
	if i >= 3600: # hours position
		return f"{int(i // 3600)}:{int((i // 60) % 60)}:{int(i % 60)}"
	elif i >= 60: # minutes position
		return f"0:{int(i // 60)}:{int(i % 60)}"
	else:
		return f"0:0:{int(i)}"

# position and duration to a proper timestamp string
def posdur_to_timestamp(pos:int, dur:int) -> Tuple[str, str]:
	return (int_to_timestamp(pos), int_to_timestamp(pos + dur))


def _new(args, conf, stagedir):
	VODS_DIR = conf["vod_dir"]
	CLIPS_DIR = conf["clip_dir"]
	STAGE_DIR = conf["stage_dir"]
	stagedir = Path(STAGE_DIR)

	# find the videos by their ids to confirm they exist
	videos = []
	for video in args.id:
		try:
			(filename, metadata, videotype) = find_video_by_id(video, VODS_DIR, CLIPS_DIR)
			videos += [{"id":video, "file":filename, "meta":metadata, "type":videotype}]
		except CouldntFindVideo:
			util.exit_prog(13, f'Could not find video with ID "{args.id}"')
	
	# Get what streamers were involved (usernames), always asked
	default_streamers = []
	for f in videos:
		if f["meta"]["user_login"] not in default_streamers:
			default_streamers.append(f["meta"]["user_login"])
	args.streamers = check_streamers(default=default_streamers)

	# get title
	if not args.title:
		args.title = check_title(default=None)

	# get description
	formatdict, datestring = create_format_dict(conf, args.streamers, utcdate=metadata["created_at"])
	args.desc = check_description(formatdict, inputdefault=args.desc)

	# get timestamps for each video through input
	for x in range(len(videos)):
		# skip times we dont need because we already have them
		if x < len(args.ss):
			continue
		
		vid = videos[x]["meta"]
		# grab times for this specific stream
		cprint(f"#dTimestamps for `#r#fM{vid['title']}#r` #d({vid['id']})#r")
		if "chapters" in vid and len(vid["chapters"]) > 0:
			cprint(f"#dChapters: ", end="")
			ch = []
			for c in vid["chapters"]:
				(pos, end) = posdur_to_timestamp(c['pos'], c['dur'])
				ch.append(f"`{c['desc']}` ({pos}-{end})")
			cprint(" | ".join(ch) + " | EOF#r")
		else:
			(pos, end) = posdur_to_timestamp(0, vid['length'])
			cprint(f"#dChapter: `{vid['game_name']}` ({pos}-{end}) | EOF#r")
		args.ss += [check_time("Start", args.ss[x] if x < len(args.ss) else None)]
		args.to += [check_time("End", args.to[x] if x < len(args.to) else None)]

	# make slice objects
	slices = []
	for x in range(len(videos)):
		vid = videos[x]
		vidslice = VideoSlice(video_id=vid["id"], ss=args.ss[x], to=args.to[x], filepath=vid["file"])
		slices += [vidslice]

	# make stage object
	stage = StageData(streamers=args.streamers, title=args.title, desc=args.desc, datestring=datestring, slices=slices)
	# Check that new "id" does not collide
	while check_stage_id(stage.id, STAGE_DIR):
		stage.gen_new_id()

	# shorter file name
	#shortfile = stage.filename.replace(VODS_DIR, "$vods").replace(CLIPS_DIR, "$clips")

	print()
	cprint(f"#r`#fC{stage.title}#r` #fM{' '.join(stage.streamers)}#r #d({stage.id})#r")
	cprint(f"#d'''\n#fG{stage.desc}#r\n#d'''#r")
	for vid in stage.slices:
		cprint(f"#fM{vid.video_id}#r > #fY{vid.ss}#r - #fY{vid.to}#r")
	
	# write stage
	stagename = str(stagedir / (stage.id + ".stage"))
	stage.write_stage(stagename)

	# Done!


def _list(args, conf, stagedir):
	VODS_DIR = conf["vod_dir"]
	CLIPS_DIR = conf["clip_dir"]
	STAGE_DIR = conf["stage_dir"]
	stagedir = Path(STAGE_DIR)
	
	if args.id == None:
		stages = StageData.load_all_stages(stagedir)

		for s in stages:
			cprint(f'#r#fY#l{s.id}#r -- `#fC{s.title}#r` ', end="")
			cprint(f'(#fM{" ".join([d.video_id for d in s.slices])}#r) -- ', end="")
			cprint(f'#l#fM{", ".join(s.streamers)}#r')
		
		if len(stages) == 0:
			cprint("#fBNothing staged right now.#r")
	else:
		stage = StageData.load_from_id(stagedir, args.id)

		cprint(f"#r`#fC{stage.title}#r` #fM{' '.join(stage.streamers)}#r #d({stage.id})#r")
		cprint(f"#d'''#fG{stage.desc}#r#d'''#r")
		for vid in stage.slices:
			cprint(f"#fM{vid['id']}#r > #fY{vid['ss']}#r - #fY{vid['to']}#r")


def run(args):
	conf = util.load_conf(args.config)
	
	util.make_dir(vodbotdir)
	stagedir = conf["stage_dir"]
	path_stage = Path(stagedir)
	util.make_dir(stagedir)

	if args.action == "new":
		_new(args, conf, stagedir)
	elif args.action == "rm":
		if not isfile(str(path_stage / (args.id + ".stage"))):
			util.exit_prog(45, f'Could not find stage "{args.id}".')
			
		try:
			os_remove(str(path_stage / (args.id + ".stage")))
			cprint(f'Stage "#fY#l{args.id}#r" has been #fRremoved#r.')
		except OSError as err:
			util.exit_prog(88, f'Stage "{args.id}" could not be removed due to an error. {err}')
	elif args.action == "list":
		_list(args, conf, stagedir)
