# Info, command to inspect a piece of media from Twitch

import re

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

KEYTRANS = {
	"vod": "VOD",
	"clip": "Clip",
	"channel": "Channel"
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
	print("Determining type...", end=" ")
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
	cword = KEYTRANS[ctype]
		
	print(f"Querying {cword} content for `{cid}`...")
	
	# run the query
	resp = gql.gql_query(query=query).json()
	resp = resp["data"]
	if not any([resp.get("video"), resp.get("clip"), resp.get("user")]):
		util.exit_prog(93, f"Could not query info on {cword} content from input.")
	
	# Read the data back and out to the terminal
	if ctype == "vod":
		r = resp['video']
		c = r['creator']
		g = r['game']
		print(f"Title: `{r['title']}` - ID: `{r['id']}`")
		print(f"Broadcaster: {c['displayName']} - {c['login']} ({c['id']})")
		print(f"Playing: {g['name']} ({g['id']})")
		print(f"At: {r['publishedAt']} - For: {r['lengthSeconds']} seconds")
	elif ctype == "clip":
		r = resp['clip']
		c = r['curator']
		b = r['broadcaster']
		g = r['game']
		print(f"Title: `{r['title']}` - ID: `{r['id']}`")
		print(f"Slug: `{r['slug']}`")
		print(f"Clipper: {c['displayName']} - {c['login']} ({c['id']})")
		print(f"Broadcaster: {b['displayName']} - {b['login']} ({b['id']})")
		print(f"Playing: {g['name']} ({g['id']})")
		print(f"At: {r['createdAt']} - For: {r['durationSeconds']} seconds - With: {r['viewCount']} views")
	elif ctype == "channel":
		r = resp['user']
		print(f"Broadcaster: {r['displayName']} - {r['login']} (ID: `{r['id']}`)")
		print(f"Description: {r['description']}")
		print(f"Channel Created At: {r['createdAt']}")
		r = r['roles']
		print(f"Roles: Affiliate={r['isAffiliate']} - Partner={r['isPartner']}")
		#cprint(f"Site Roles: Staff={r['isStaff']} - GlobalMod={r['isGlobalMod']} - SiteAdmin={r['isSiteAdmin']}")

	# Done!
