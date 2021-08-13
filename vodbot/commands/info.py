# Info, command to inspect a piece of media from Twitch

import re
from vodbot.printer import cprint

from vodbot import util
from vodbot.itd import gql

PATTERNS = {
	"vod": [
		r"^(?P<id>\d+)?$",
		r"^(https?://)?(www\.)?twitch.tv/videos/(?P<id>\d+)(\?.*)?$"
	],
	"clip": [
		r"^(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)$",
		r"^(https?://)?(www\.)?twitch.tv/\w+/clip/(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)(\?.*)?$",
		r"^(https?://)?clips\.twitch.tv/(?P<id>[A-Za-z0-9]+(?:-[A-Za-z0-9_-]{16})?)(\?.*)?$"
	],
	"channel": [
		r"^[a-zA-Z0-9][\w]{0,24}$",
		r"^(https?://)?(www\.)?twitch\.tv/(?P<id>[a-zA-Z0-9][\w]{0,24})(\?.*)?$"
	]
}

keytrans = {
	"vod": "VOD",
	"clip": "Clip",
	"channel": "channel"
}


def get_type(cid):
	for ctype, clist in PATTERNS.items():
		for pattern in clist:
			match = re.match(pattern, cid)
			if match:
				return match.group("id"), ctype
	
	return None, None


def run(args):
	# First determine what kind of data it is...
	# We should allow people to paste full links or just the ID too.
	tid = args.id

	# Get the proper id and type of content we need to pull
	cprint("#dDetermining type...#r", end=" ")
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
		
	cprint(f"#dQuerying {keytrans[ctype]} content for `{cid}`...#r")
	
	# run the query
	resp = gql.gql_query(query=query).json()
	resp = resp["data"]
	if resp.get("video") == None and resp.get("clip") == None and resp.get("user") == None:
		util.exit_prog(93, "Could not query info on content from input.")
	
	# Read the data back and out to the terminal
	if ctype == "vod":
		r = resp["video"]
		c = r['creator']
		g = r['game']
		cprint(f"Title: `{r['title']}`")
		cprint(f"Broadcaster: {c['displayName']} - {c['login']} ({c['id']})")
		cprint(f"Playing: {g['name']} ({g['id']})")
		cprint(f"At: {r['publishedAt']} - For: {r['lengthSeconds']} seconds")
	elif ctype == "clip":
		print(resp["clip"])
	elif ctype == "channel":
		print(resp["user"])

	# Done!
