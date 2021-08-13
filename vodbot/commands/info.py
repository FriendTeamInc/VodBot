# Info, command to inspect a piece of media from Twitch

import re

from vodbot import util
from vodbot.itd import gql

PATTERNS = {
	"vod": [
		r"^(?P<id>\d+)?$",
		r"^(https?://)?(www\.)?twitch.tv/videos/(?P<id>\d+)(\?\.+)?$"
	],
	"clip": [
		r"^(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)$",
		r"^(https?://)?(www\.)?twitch.tv/\w+/clip/(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)(\?\.+)?$",
		r"^(https?://)?clips\.twitch.tv/(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)(\?\.+)?$"
	],
	"channel": [
		r"^[a-zA-Z0-9][\w]{0,24}$",
		r"^(https?://)?(www\.)?twitch\.tv/(?P<id>[a-zA-Z0-9][\w]{0,24})(\?.*)?$"
	]
}


def get_type(cid):
	for ctype, clist in PATTERNS.items():
		for pattern in clist:
			match = re.match(pattern, cid)
			if match:
				return match.group("id"), ctype


def run(args):
	# First determine what kind of data it is...
	# We should allow people to paste full links or just the ID too.
	tid = args.id

	# Get the proper id and type of content we need to pull
	cid, ctype = get_type(tid)

	# The call the appropriate info query for GQL
	query = None
	if ctype == "vod":
		query = gql.GET_VIDEO_QUERY.format(video_id=cid)
	elif ctype == "clip":
		query = gql.GET_CLIP_QUERY.format(clip_slug=cid)
	elif ctype == "channel":
		query = gql.GET_CHANNEL_QUERY.format(channel_id=cid)
	else:
		util.exit_prog(92, "Could not determine content type from input.")
	
	# run the query
	resp = gql.gql_query(query=query).json()
	if resp["data"]["user"] == None:
		util.exit_prog(93, "Could not query info on content from input.")
	resp = resp["data"]["user"]
	
	# Read the data back and out to the terminal
	if ctype == "vod":
		print(resp)
	elif ctype == "clip":
		print(resp)
	elif ctype == "channel":
		print(resp)

	# Done!
