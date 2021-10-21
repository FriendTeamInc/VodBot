# Module that parses chatlogs to and from files

from vodbot.commands.stage import StageData
from vodbot.twitch import ChatMessage
import vodbot.util as util

import json
from typing import List
from pathlib import Path


def chat_to_logfile(msgs: List[ChatMessage], path: str) -> None:
	# create preamble (contains all chatter's names and their colors)
	preamb = []
	for m in msgs:
		s = f"{m.color};{m.user}"
		if s not in preamb:
			preamb.append(s)

	# open chat log file
	with open(path, "wb") as f:
		# write pramble as one line, delimited by null characters
		for s in preamb:
			f.write(s.encode("utf-8"))

			if s != preamb[-1]:
				f.write("\0".encode("utf-8"))
		
		# preamble done
		f.write("\n".encode("utf-8"))

		# write the messages, each line a new message
		for m in msgs:
			idx = preamb.index(f"{m.color};{m.user}")
			# each line is a unique message
			# line string split with \0 for components
			# m[0]=offset from start of stream, m[1]=state (published, deleted, etc),
			# m[2]=user (in preamble), m[3:]=message they sent, encoded as a string
			f.write(f"{m.offset}\0{m.enc_state}\0{idx}\0{m.enc_msg}".encode("utf-8"))

			# newlines on every line except the last
			if m != msgs[-1]:
				f.write("\n".encode("utf-8"))


def logfile_to_chat(path: str) -> List[ChatMessage]:
	chats = []

	with open(path, "rb") as f:
		readfirst = False
		preamb = []
		for line in f.readlines():
			line = line.decode("utf-8").strip("\n") # Remove newline character and decode as utf8
			if not readfirst:
				# first line is preamble, so we unravel it
				for user in line.split("\0"):
					user = user.split(";")
					preamb.append((user[0], user[1]))
				readfirst = True
			else:
				# succeeding lines are all chat messages, so we read each one, match it with a user
				# from the preamble, grab all the other info, make a ChatMessage object, and tack it
				# on to the list.
				line = line.split("\0")
				info = int(line[2])
				chats.append(
					ChatMessage(
						user=preamb[info][1], color=preamb[info][0],
						offset=line[0], enc_state=int(line[1]), enc_msg=line[3]
					)
				)

	return chats


def timestring_as_seconds(time:str, default:int=0):
	if time == "EOF":
		return default
	
	s = time.split(":")

	# Hours, minutes, seconds
	return int(s[0]) * 60 * 60 + int(s[1]) * 60 + int(s[2])


def process_stage(conf: dict, stage: StageData, mode:str) -> Path:
	tempdir = Path(conf["temp_dir"])

	total_offset = 0
	chat_list = []
	for slc in stage.slices:
		# load up each stagedata's meta to see if chat exists
		metapath = slc.filepath[:-5] + ".meta"
		meta = None
		with open(metapath, "r") as f:
			meta = json.load(f)
		
		has_chat = meta.get("has_chat", False)
		duration = meta.get("length")
		chat_path = slc.filepath[:-5] + ".chat"
		# start and end times as seconds
		start_sec = timestring_as_seconds(slc.ss)
		end_sec = timestring_as_seconds(slc.to, duration)
		
		# keep each list of chat separate, compare timestamps to offsets to make
		# sure theyre inbetween the slices
		if has_chat:
			msg_list = [m for m in logfile_to_chat(chat_path) if start_sec <= m.offset < end_sec]
			if total_offset != 0:
				for m in msg_list:
					m.offset = m.offset + total_offset
			
			chat_list += msg_list
		
		# now take each stage's duration and apply it to the next chat list's
		total_offset += end_sec - start_sec

	# determine how to export, then return the resultant path
	if mode != "upload" or mode != "export":
		util.exit_prog(94, f"Cannot export chat with export mode {mode}")
	
	export_type = conf["chat_"+mode]

	if export_type == "raw":
		# copy from archive to temp
		pass
	elif export_type == "RealText":
		# load from archive, parse and write to temp
		pass
	elif export_type == "SAMI":
		# load from archive, parse and write to temp
		pass

	return None

