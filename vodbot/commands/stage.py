# Staging, where videos get staged and set up with metadata to upload

import vodbot.util as util
from vodbot.printer import cprint, colorize

import json
import pytz
import hashlib
from datetime import datetime
from pathlib import Path
from os import walk as os_walk, remove as os_remove
from os import listdir
from os.path import isfile, isdir


# Default path
vodbotdir = util.vodbotdir


class StageData():
	def __init__(self, title, desc, ss, to, streamers, datestring, filename):
		self.title = title
		self.desc = desc
		self.ss = ss
		self.to = to
		self.streamers = streamers
		self.datestring = datestring
		self.filename = filename

		self.hash = hashlib.sha1()
		self.hash.update(self.title.encode("utf-8"))
		self.hash.update(self.desc.encode("utf-8"))
		self.hash.update(self.ss.encode("utf-8"))
		self.hash.update(self.to.encode("utf-8"))
		self.hash.update(self.datestring.encode("utf-8"))
		self.hash.update(self.filename.encode("utf-8"))
		
		self.hashdigest = self.hash.hexdigest()[:8]
	
	def __hash__(self):
		return hash((self.title, self.desc, self.ss, self.to, self.filename))
	
	def write_stage(self, filename):
		with open(filename, "w") as f:
			jsondump = {
				"title": self.title,
				"desc": self.desc,
				"ss": self.ss,
				"to": self.to,
				"filename": self.filename,
				"streamers": self.streamers,
				"datestring": self.datestring,
				"hash": self.hash.hexdigest()
			}
			json.dump(jsondump, f)


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


def check_time(prefix, inputstring, resp, default=None):
	output = resp
	checkedonce = False

	while True:
		if checkedonce or output == None:
			output = input(colorize(inputstring))
		checkedonce = True

		if output == "":
			if prefix == "Start time":
				return default if default != None else "0:0:0"
			elif prefix == "End time":
				return default if default != None else "EOF"

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


def _add(args, conf, stagedir):
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
	# Get what streamers were involved (usernames), always asked
	args.streamers = None
	if args.streamers == None:
		args.streamers = ""
		while args.streamers == "":
			args.streamers = input(colorize(f"#fW#lWho was in the VOD#r #d(default `{metadata['user_name']}`, csv)#r: "))
			if args.streamers == "":
				args.streamers = [metadata["user_name"]]
			else:
				args.streamers = args.streamers.replace(" ", "").split(",")
				
	# Grab the title
	if args.title == None:
		args.title = ""
		while args.title == "":
			args.title = input(colorize("#fW#lTitle of the Video#r #d(--title)#r: "))
			if args.title == "":
				cprint("#fRTitle cannot be blank.#r")

	# Grab times
	args.ss = check_time("Start time", "#fW#lStart time of the Video#r #d(--ss, default 0:0:0)#r: ", args.ss)
	args.to = check_time("End time", "#fW#lEnd time of the Video#r #d(--to, default EOF)#r: ", args.to)

	# Generate dict to use for formatting
	est = pytz.timezone("US/Eastern") # TODO: allow config to change this
	utc = pytz.utc
	date = datetime.strptime(metadata["created_at"], "%Y-%m-%dT%H:%M:%SZ")
	date.replace(tzinfo=utc)
	date.astimezone(est)
	datestring = date.astimezone(est).strftime("%Y/%m/%d")
	formatdict = {
		"date": datestring,
		"link": f"https://twitch.tv/{metadata['user_name']}",
		"streamer": metadata['user_name'],
	}
	formatdict["twatch"] = f"-- Watch live at " + " ".join([f"https://twitch.tv/{s}" for s in args.streamers])

	# Grab description
	if args.desc == None:
		args.desc = ""
	else:
		# Format the description
		try:
			args.desc = args.desc.format(**formatdict).replace("\\n", "\n")
		except KeyError as err:
			cprint(f"#fRDescription format error: {err}.#r")
			args.desc = ""

	while args.desc == "":
		args.desc = input(colorize("#fW#lDescription of Video#r #d(--desc)#r: "))
		if args.desc == "":
			cprint("#fRDescription cannot be blank.#r")

		# Format the description
		try:
			args.desc = args.desc.format(**formatdict).replace("\\n", "\n")
		except KeyError as err:
			cprint(f"#fRDescription format error: {err}.#r")
			args.desc = ""

	stage = StageData(args.title, args.desc, args.ss, args.to, args.streamers, datestring, str(filename))
	shortfile = stage.filename.replace(VODS_DIR, "...").replace(CLIPS_DIR, "...")

	print()
	cprint(f"#r`#fC{stage.title}#r` #d({stage.ss} - {stage.to})#r")
	cprint(f"#d''' {shortfile}#r\n#fG{stage.desc}#r\n#d''' {stage.hashdigest}#r")
	cprint(f"#d#fM{' '.join(stage.streamers)}#r")
	
	stagename = str(stagedir / (stage.hashdigest + ".stage"))
	stage.write_stage(stagename)

	# Done!


def _list(args, conf, stagedir):
	VODS_DIR = conf["vod_dir"]
	CLIPS_DIR = conf["clip_dir"]
	if args.id == None:
		stages = [d[:-6] for d in listdir(str(stagedir))
			if isfile(str(stagedir / d)) and d[-5:] == "stage"]

		for stage in stages:
			jsonread = None
			try:
				with open(str(stagedir / (stage+".stage"))) as f:
					jsonread = json.load(f)
			except FileNotFoundError:
				# Throw error?
				continue
			except KeyError:
				continue
			
			cprint(f'#r#fY#l{stage}#r -- `#fC{jsonread["title"]}#r` #d(', end="")
			cprint(f'{jsonread["ss"]} - {jsonread["to"]})#r -- ', end="")
			cprint(f'#fM{", ".join(jsonread["streamers"])}#r')
		
		if len(stages) == 0:
			cprint("#fBNothing staged right now.#r")
	else:
		if not isfile(str(stagedir / (args.id + ".stage"))):
			util.exit_prog(45, f'Could not find stage "{args.id}".')
		
		jsonread = None
		try:
			with open(str(stagedir / (args.id+".stage"))) as f:
				jsonread = json.load(f)
		except FileNotFoundError:
			util.exit_prog(46, f'Could not find stage "{args.id}". (FileNotFound)')
		except KeyError:
			util.exit_prog(46, f'Could not parse stage "{args.id}" as JSON. Is this file corrupted?')
		
		title = jsonread['title']
		desc = jsonread['desc']
		ss = jsonread['ss']
		to = jsonread['to']
		streamers = jsonread['streamers']
		datestring = jsonread['datestring']
		filename = jsonread['filename']

		stage = StageData(title, desc, ss, to, streamers, datestring, filename)
		shortfile = stage.filename.replace(VODS_DIR, "...").replace(CLIPS_DIR, "...")

		print()
		cprint(f"#r`#fC{stage.title}#r` #d({stage.ss} - {stage.to})#r")
		cprint(f"#d''' {shortfile}#r\n#fG{stage.desc}#r\n#d''' #fYHash: {stage.hashdigest}#r")
		cprint(f"#d#fM{' '.join(stage.streamers)}#r")


def _edit(args, conf, stagedir):
	if not isfile(str(stagedir / (args.id + ".stage"))):
		util.exit_prog(45, f'Could not find stage "{args.id}".')
	
	jsonread = None
	try:
		with open(str(stagedir / (args.id+".stage"))) as f:
			jsonread = json.load(f)
	except FileNotFoundError:
		util.exit_prog(46, f'Could not find stage "{args.id}". (FileNotFound)')
	except KeyError:
		util.exit_prog(46, f'Could not parse stage "{args.id}" as JSON. Is this file corrupted?')
	
	old_title = jsonread['title']
	old_desc = jsonread['desc']
	old_ss = jsonread['ss']
	old_to = jsonread['to']
	old_streamers = jsonread['streamers']
	old_datestring = jsonread['datestring']
	old_filename = jsonread['filename']

	old_stage = StageData(old_title, old_desc, old_ss, old_to, old_streamers, old_datestring, old_filename)
	shortfile = old_stage.filename.replace(VODS_DIR, "...").replace(CLIPS_DIR, "...")

	cprint("#l#fRCurrent stage:")
	cprint(f"#r`#fC{old_stage.title}#r` #d({old_stage.ss} - {old_stage.to})#r")
	cprint(f"#d''' {shortfile}#r\n#fG{old_stage.desc}#r\n#d''' #fYHash: {old_stage.hashdigest}#r")
	cprint(f"#d#fM{' '.join(old_stage.streamers)}#r")
	
	# Now to take the edits, where blank responses are defaulted to the original value.
	# Get what streamers were involved (usernames)
	args.streamers = None
	if args.streamers == None:
		args.streamers = ""
		while args.streamers == "":
			args.streamers = input(colorize(f"#fW#lWho was in the VOD#r #d(default to original, csv)#r: "))
			if args.streamers == "":
				args.streamers = old_streamers
			else:
				args.streamers = args.streamers.replace(" ", "").split(",")

	# Grab the title
	if args.title == None:
		args.title = ""
		while args.title == "":
			args.title = input(colorize("#fW#lTitle of the Video#r #d(--title, default to original)#r: "))
			if args.title == "":
				args.title = old_title

	# Grab times
	args.ss = check_time("Start time", "#fW#lStart time of the Video#r #d(--ss, default to original)#r: ", args.ss, old_ss)
	args.to = check_time("End time", "#fW#lEnd time of the Video#r #d(--to, default to original)#r: ", args.to, old_to)

	# Generate dict to use for formatting
	est = pytz.timezone("US/Eastern") # TODO: allow config to change this
	utc = pytz.utc
	date = datetime.strptime(metadata["created_at"], "%Y-%m-%dT%H:%M:%SZ")
	date.replace(tzinfo=utc)
	date.astimezone(est)
	datestring = date.astimezone(est).strftime("%Y/%m/%d")
	formatdict = {
		"date": datestring,
		"links": " ".join([f"https://twitch.tv/{s}" for s in args.streamers]),
		"streamer": metadata['user_name'],
	}
	formatdict["twatch"] = f"-- Watch live at " + formatdict["links"]

	while args.desc == "":
		args.desc = input(colorize("#fW#lDescription of Video#r #d(--desc, default to original)#r: "))
		if args.desc == "":
			args.desc = old_desc
			break

		# Format the description
		try:
			args.desc = args.desc.format(**formatdict).replace("\\n", "\n")
		except KeyError as err:
			cprint(f"#fRDescription format error: {err}.#r")
			args.desc = ""

	new_stage = StageData(args.title, args.desc, args.ss, args.to, args.streamers, old_datestring, old_filename)
	shortfile = new_stage.filename.replace(VODS_DIR, "...").replace(CLIPS_DIR, "...")

	cprint("#l#fRNew stage:")
	cprint(f"#r`#fC{new_stage.title}#r` #d({new_stage.ss} - {new_stage.to})#r")
	cprint(f"#d''' {shortfile}#r\n#fG{new_stage.desc}#r\n#d''' #fYHash: {new_stage.hashdigest}#r")
	cprint(f"#d#fM{' '.join(new_stage.streamers)}#r")

	cprint("#l#fRSave changes and remove old stage?#r")


def run(args):
	util.make_dir(vodbotdir)
	stagedir = vodbotdir / "stage"
	util.make_dir(stagedir)
	conf = util.load_twitch_conf(args.config)

	if args.action == "add":
		_add(args, conf, stagedir)
	elif args.action == "edit":
		_edit(args, conf, stagedir)
	elif args.action == "rm":
		if not isfile(str(stagedir / (args.id + ".stage"))):
			util.exit_prog(45, f'Could not find stage "{args.id}".')
		
		try:
			os_remove(str(stagedir / (args.id + ".stage")))
			cprint(f'Stage "#fY#l{args.id}#r" has been #fRremoved#r.')
		except OSError as err:
			util.exit_prog(88, f'Stage "{args.id}" could not be removed due to an error. {err}')
	elif args.action == "list":
		_list(args, conf, stagedir)
