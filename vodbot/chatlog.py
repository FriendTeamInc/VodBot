# Module that parses chatlogs to and from files

from os import write
from vodbot.commands.stage import StageData
from vodbot.twitch import ChatMessage
import vodbot.util as util

import json
from typing import List
from pathlib import Path
import shutil


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
						offset=int(line[0]), enc_state=int(line[1]), enc_msg=line[3]
					)
				)

	return chats


def chat_to_realtext(msgs: List[ChatMessage], path: str, vid_duration:int, msg_duration:int):
	with open(path, "w") as f:
		# add preamble (stuff like opening tags)
		f.write('<window type="generic" wordwrap="true"><font color="#ffffff">\n')

		# this is so cursed
		last_msgs: List[ChatMessage] = []
		for t in range(vid_duration):
			current_msgs: List[ChatMessage] = []
			for m in msgs:
				if t <= m.offset <= t+msg_duration:
					current_msgs.append(m)
				elif m.offset > t+msg_duration:
					break
			
			if current_msgs != last_msgs:
				# write line and overwrite last_msgs
				last_msgs = current_msgs
				string_to_write = f'<time begin="{t}"/>'
				if len(current_msgs) != 0:
					# write full messages line
					for m in current_msgs:
						# write name and message
						string_to_write += f'<font color="#{m.color}"><b>{m.user}</b></font>: {m.msg}'
						if m != current_msgs[-1]:
							string_to_write += "<br/>"
				else:
					string_to_write += "<clear/>"
					pass # write clear line

				# write string
				string_to_write += "\n"
				f.write(string_to_write)

		# finish up
		f.write("</font></window")


def timestring_as_seconds(time:str, default:int=0):
	if time == "EOF":
		return default
	
	s = time.split(":")
	
	seconds = int(s[-1]) if len(s) >= 1 else 0
	minutes = int(s[-2]) if len(s) >= 2 else 0
	hours = int(s[-3]) if len(s) >= 3 else 0

	# Hours, minutes, seconds
	return hours * 60 * 60 + minutes * 60 + seconds


def process_stage(conf: dict, stage: StageData, mode:str) -> Path:
	tempdir = Path(conf["temp_dir"])
	msg_duration = int(conf["chat_msg_time"])

	total_offset = 0
	chat_list = []
	for slc in stage.slices:
		# load up each stagedata's meta to see if chat exists
		metapath = slc.filepath[:-4] + ".meta"
		meta = None
		with open(metapath, "r") as f:
			meta = json.load(f)
		
		has_chat = meta.get("has_chat", False)
		duration = meta.get("length")
		chat_path = slc.filepath[:-4] + ".chat"
		# start and end times as seconds
		start_sec = timestring_as_seconds(slc.ss)
		end_sec = timestring_as_seconds(slc.to, duration)
		
		# keep each list of chat separate, compare timestamps to offsets to make
		# sure theyre inbetween the slices
		if has_chat:
			msg_list = [m for m in logfile_to_chat(chat_path) if start_sec <= m.offset < end_sec]
			if total_offset != 0:
				for m in msg_list:
					m.offset = m.offset - start_sec + total_offset
			
			chat_list += msg_list
		
		# now take each stage's duration and apply it to the next chat list's
		total_offset += end_sec - start_sec

	# determine how to export, then return the resultant path
	if mode != "upload" and mode != "export":
		util.exit_prog(94, f"Cannot export chat with export mode {mode}")
	
	export_type = conf["chat_"+mode]

	returnpath = None
	if export_type == "raw":
		# chat to logfile time
		returnpath = tempdir / (stage.id + ".chat")
		chat_to_logfile(chat_list, str(returnpath))
	elif export_type == "RealText":
		# load from archive, parse and write to temp
		returnpath = tempdir / (stage.id + ".rt")
		chat_to_realtext(chat_list, str(returnpath), total_offset, msg_duration)
	elif export_type == "SAMI":
		# load from archive, parse and write to temp
		returnpath = tempdir / (stage.id + ".sami")
	
	print(returnpath)

	return returnpath

