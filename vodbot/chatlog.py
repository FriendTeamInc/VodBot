# Module that parses chatlogs to and from files

from random import randint
from .commands.stage import StageData
from .printer import cprint
from .twitch import ChatMessage
from .config import Config
from . import util

import json
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List, Tuple
from pathlib import Path

HTML_FXIED_SYMBOLS = {
	"&": "&#38;",
	"<": "&#60;",
	">": "&#62;",
}


@dataclass_json
@dataclass
class _ChatMember:
	username: str
	color: str

@dataclass_json
@dataclass
class _ChatMessage:
	user: int
	offset: int
	#state: str
	message: str

@dataclass_json
@dataclass
class _ChatLog:
	users: List[_ChatMember]
	msgs: List[_ChatMessage]


def chat_to_logfile(chatmsgs: List[ChatMessage], path: str) -> None:
	msgs = []
	preamb = []
	users = {}
	for m in chatmsgs:
		s = m.user
		if s not in users:
			preamb.append({"username": s, "color": m.color})
			users[s] = len(preamb)-1
		
		msgs.append({"user": users[s], "offset": m.offset, "message": m.msg})
	
	with open(path, "w") as f:
		chatlog = _ChatLog.from_dict({"users": preamb, "msgs": msgs})
		f.write(chatlog.to_json())


def logfile_to_chat(path: str) -> List[ChatMessage]:
	chats = []

	chatlog: _ChatLog = None
	with open(path) as f:
		chatlog = _ChatLog.from_json(f.read())
	
	for chat in chatlog.msgs:
		chats.append(ChatMessage(
			user=chatlog.users[chat.user].username, color=chatlog.users[chat.user].color,
			offset=chat.offset, msg=chat.message
		))

	return chats


def chat_to_userlist(msgs: List[ChatMessage]) -> Tuple[List[dict], List[str]]:
	userlist = {}
	userorder = []
	uid = 0
	for m in msgs:
		if m.user not in userlist:
			userlist[m.user] = {"id":uid, "clr":m.color}
			userorder.append(m.user)
			uid += 1
	
	return userlist, userorder


def chat_to_listwithbounds(msgs: List[ChatMessage], vid_duration:int, msg_duration:int) -> List[dict]:
	# First we run through all the messages and see what needs showing and what doesn't
	chat_lists = []
	# this is so cursed
	last_msgs: List[ChatMessage] = []
	for t in range(vid_duration):
		current_msgs: List[ChatMessage] = []
		for m in msgs:
			if t <= m.offset < t+msg_duration:
				current_msgs.append(m)
			elif m.offset >= t+msg_duration:
				break
		
		if current_msgs != last_msgs:
			# write line and overwrite last_msgs
			last_msgs = current_msgs
			write = {"begin": t, "end": vid_duration, "msgs":[], "break":False}
			if len(current_msgs) != 0:
				# write full messages line
				for m in current_msgs:
					# write color, name, and message
					write["msgs"] += [{"clr":m.color, "usr":m.user, "msg":m.msg}]
			else:
				# write clear line
				write["break"] = True

			# write string
			chat_lists.append(write)
	
	# set end boundaries
	for x in range(len(chat_lists)):
		if x != len(chat_lists)-1:
			chat_lists[x]["end"] = chat_lists[x+1]["begin"]
	
	return chat_lists


# https://github.com/arcusmaximus/YTSubConverter/blob/master/ytt.ytt
def chat_to_ytt(conf: Config, msgs: List[ChatMessage], path: str, vid_duration:int):
	msg_duration = conf.chat.message_display_time
	msg_alignment = conf.chat.ytt_align
	msg_anchor = conf.chat.ytt_anchor
	pos_x = conf.chat.ytt_position_x
	pos_y = conf.chat.ytt_position_y

	if msg_alignment == "left":
		msg_alignment = 0
	elif msg_alignment == "right":
		msg_alignment = 1
	elif msg_alignment == "center":
		msg_alignment = 2
	else:
		msg_alignment = 0
	
	# get individual users and their info
	chat_users, user_order = chat_to_userlist(msgs)
	# get chat with message in bounds
	chat_lists = chat_to_listwithbounds(msgs, vid_duration, msg_duration)

	with open(path, "w", encoding="utf8") as f:
		# write preamble stuffs
		f.write('<?xml version="1.0" encoding="utf-8"?>\n')
		f.write('<timedtext format="3"><head>\n')
		# write pens and side anchoring HERE
		# default text
		f.write('<pen id="1" fc="#FEFEFE"/>\n')
		# user name text
		for user in user_order:
			u = chat_users[user]
			clr = u["clr"]
			if conf.chat.randomize_uncolored_names and clr == "FFFFFF":
				clr = f"{randint(127,255):02x} {randint(127,255):02x} {randint(127, 255):02x}"
				chat_users[user]["clr"] = clr
			f.write(f'<pen id="{u["id"]+2}" fc="#{u["clr"]}" fo="254" b="1" />\n')
		f.write(f'<ws id="1" ju="{msg_alignment}" />\n')
		f.write(f'<wp id="1" ap="{msg_anchor}" ah="{pos_x}" av="{pos_y}" />\n')
		f.write('</head><body>\n')

		count = 0
		for c in chat_lists:
			if not c["msgs"]:
				continue
			f.write(f'<p t="{c["begin"]*1000}" d="{(c["end"]-c["begin"])*1000}" wp="1" ws="1">')
			count += 1
			for m in c["msgs"]:
				msg = m["msg"]
				for k,v in HTML_FXIED_SYMBOLS.items():
					msg = msg.replace(k, v)
				u = chat_users[m["usr"]]
				f.write(f'<s p="{u["id"]+2}">{m["usr"]}</s><s p="1">: {msg}</s>')
				if m != c["msgs"][-1]:
					f.write("\n")
				
			f.write("</p>\n")
		
		# finish up
		f.write("</body></timedtext>")


def process_stage(conf: Config, stage: StageData, mode:str) -> Path:
	tempdir = Path(conf.directories.temp)

	cprint(f"#rLoading all chat messages for `#fM{stage.id}#r`.", end="")
	total_offset = 0
	chat_list = []
	for slc in stage.slices:
		# load up each stagedata's meta to see if chat exists
		metapath = slc.filepath[:-4] + ".meta"
		meta = None
		with open(metapath, "r") as f:
			meta = json.load(f)
		
		has_chat = meta.get("has_chat", False)
		duration = meta.get("length", 0)
		chat_path = slc.filepath[:-4] + ".chat"
		# start and end times as seconds
		start_sec = util.timestring_as_seconds(slc.ss)
		end_sec = util.timestring_as_seconds(slc.to, duration)
		
		# keep each list of chat separate, compare timestamps to offsets to make
		# sure theyre inbetween the slices
		if has_chat:
			msg_list = [m for m in logfile_to_chat(chat_path) if start_sec <= m.offset < end_sec]
			for m in msg_list:
				m.offset = m.offset - start_sec + total_offset
			
			chat_list += msg_list
		
		# now take each stage's duration and apply it to the next chat list's
		total_offset += end_sec - start_sec

	# determine how to export, then return the resultant path
	if mode != "upload" and mode != "export":
		util.exit_prog(94, f"Cannot export chat with export mode {mode}")
	
	export_type = conf.chat.export_format if mode != "upload" else "YTT"

	if len(chat_list) == 0:
		cprint(f" No chat found in `#fM{stage.id}#r` stage. Skipping...")
		return None

	cprint(f" Exporting as format `#fY{export_type}#r`.")

	returnpath = None
	if export_type == "raw":
		# chat to logfile time
		returnpath = tempdir / f"{stage.id}.chat"
		chat_to_logfile(chat_list, str(returnpath))
	elif export_type == "YTT":
		# load from archive, parse and write to temp
		returnpath = tempdir / f"{stage.id}.ytt"
		chat_to_ytt(conf, chat_list, str(returnpath), total_offset)

	return returnpath

