# Module to ship webhooks out to various places, currently only Discord is supported
from ctypes import Union
from typing import Any, Dict, List
from .twitch import Clip, Vod
from .config import Config
from .util import format_duration as formdur

from discord_webhook import DiscordWebhook, DiscordEmbed

_config_attributes = {
	"pull_vod": "Pulled VOD",
	"pull_clip": "Pulled Clip",
	"pull_error": "Pull Error",
	"pull_job_done": "Pull Job Done",
	"export_video": "Exported Video",
	"export_error": "Export Error",
	"export_job_done": "Export Job Done",
	"upload_video": "Uploaded Video",
	"upload_error": "Upload Error",
	"upload_job_done": "Upload Job Done"
}
_webhooks = {atrb: None for atrb in _config_attributes}


def init_webhooks(conf: Config):
	# check main toggle
	if not conf.webhooks.enable or not conf.webhooks.url:
		return

	for atrb, title in _config_attributes.items():
		confwh = getattr(conf.webhooks, atrb)

		# check individual toggle
		if not confwh.enable:
			continue

		# check overwriting attributes
		o = {}
		for what in ["url", "username", "avatar_url", "message"]:
			o[what] = getattr(conf.webhooks, what)
			if getattr(confwh, what, None):
				o[what] = getattr(confwh, what)

		# setup webhook and embed
		webhook = DiscordWebhook(
			url=o["url"], content=o["message"], username=o["username"],
			avatar_url=o["avatar_url"], rate_limit_retry=True)
		embed = DiscordEmbed()

		embed.set_footer(text="VodBot \U0001F49C by NotQuiteApex & Friend Team Inc.")
		embed.set_color("7353b2")

		webhook.add_embed(embed)

		_webhooks[atrb] = (webhook, embed)


def _send_webhook(wh:str, **kwargs: Union[str, List[Dict[str, Union[str, bool]]]]):
	# check if there is a webhook and it has a url, otherwise safely ignore
	if _webhooks.get(wh, None) is None or not _webhooks[wh][0].url:
		return
	
	webhook: DiscordWebhook
	embed: DiscordEmbed
	(webhook, embed) = _webhooks[wh]

	embed.url = kwargs.get("url")
	embed.title = kwargs.get("title", "UNKNOWN TITLE PLZ FIX")
	embed.fields = kwargs.get("fields", [])
	embed.color = kwargs.get("color", embed.color)
	
	webhook.remove_embeds()
	webhook.add_embed(embed)
	# TODO: use async?
	try:
		resp = webhook.execute(remove_embeds=True)
	except:
		# ignore failures to connect
		pass


def send_pull_vod(vod: Vod):
	s = "\n".join(f'- "{c.description}" at {formdur(c.position)} for {formdur(c.duration)}' for c in vod.chapters)
	_send_webhook("pull_vod",
		url=vod.url, title=f'Pulled VOD "{vod.title}" ({vod.id})',
		fields=[
			{"name": "Created At", "value": vod.created_at},
			{"name": "Streamer", "value": vod.user_name},
			{"name": "Length", "value": formdur(vod.length)},
			{"name": "Game", "value": vod.game_name},
			{"name": "Has Chat", "value": str(vod.has_chat)},
			{"name": "Chapters", "value": s, "inline": False}
		]
	)


def send_pull_clip(clip: Clip):
	_send_webhook("pull_clip",
		url=clip.url, title=f'Pulled Clip "{clip.title}" ({clip.id})',
		fields=[
			{"name": "Created At", "value": clip.created_at},
			{"name": "Clipper", "value": clip.clipper_name},
			{"name": "Streamer", "value": clip.user_name},
			{"name": "Stream", "value": f"[{clip.video_id}](https://twitch.tv/videos/{clip.video_id})"},
			{"name": "Offset", "value": formdur(clip.length)},
			{"name": "Length", "value": formdur(clip.length)},
		]
	)


def send_pull_error(description: str, link: str):
	_send_webhook("pull_error",
		url=link, title=description, color="bf4d30"
	)


def send_pull_job_done(fin_vods, fin_clips, all_vods, all_clips):
	_send_webhook("pull_job_done",
		title=f"Pull job completed successfully!", color="227326",
		fields=[
			{"name": "VODs Pulled", "value": f"{fin_vods} of {all_vods}"},
			{"name": "Clips Pulled", "value": f"{fin_clips} of {all_clips}"},
		]
	)


def send_export_video():
	pass


def send_export_error():
	pass
def send_export_job_done():
	pass


def send_upload_video():
	pass
def send_upload_error():
	pass
def send_upload_job_done():
	pass
