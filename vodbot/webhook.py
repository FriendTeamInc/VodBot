# Module to ship webhooks out to various places, currently only Discord is supported
from .twitch import Clip, Vod
from .config import Config
from .util import format_duration

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

		# check url
		url = conf.webhooks.url
		if confwh.url:
			url = confwh.url

		# check message
		message = conf.webhooks.message
		if confwh.message:
			message = confwh.message

		# setup webhook and embed
		webhook = DiscordWebhook(url=url, content=message, rate_limit_retry=True)
		embed = DiscordEmbed()

		embed.set_footer(text="VodBot Made with \U0001F49C by NotQuiteApex & Friend Team Inc.")
		embed.set_color("7353b2")

		webhook.add_embed(embed)

		_webhooks[atrb] = (webhook, embed)


def send_pull_vod(vod: Vod):
	wh = "pull_vod"
	# check if there is a webhook and it has a url, otherwise safely ignore
	if _webhooks.get(wh, None) is None or not _webhooks[wh][0].url:
		return
	
	webhook: DiscordWebhook
	embed: DiscordEmbed
	(webhook, embed) = _webhooks[wh]

	embed.set_url(vod.url)
	embed.set_title(f'Pulled VOD "{vod.title}" ({vod.id})')

	s = f'By {vod.user_name}\nAt {vod.created_at} for {format_duration(vod.length)}\nChapters:'
	for chapter in vod.chapters:
		s += f'\n- "{chapter.description}" at {chapter.position}s for {format_duration(chapter.duration)}'
	embed.set_description(s)

	_send_webhook(webhook, embed)


def send_pull_clip(clip: Clip):
	wh = "pull_clip"
	# check if there is a webhook and it has a url, otherwise safely ignore
	if _webhooks.get(wh, None) is None or not _webhooks[wh][0].url:
		return
	
	webhook: DiscordWebhook
	embed: DiscordEmbed
	(webhook, embed) = _webhooks[wh]

	embed.set_url(clip.url)
	embed.set_title(f'Pulled Clip "{clip.title}" ({clip.id})')

	embed.add_embed_field(name="Created at", value=clip.created_at)
	embed.add_embed_field(name="Clipper", value=clip.clipper_name)
	embed.add_embed_field(name="Streamer", value=clip.user_name)
	embed.add_embed_field(name="Stream", value=f"[{clip.video_id}](https://twitch.tv/videos/{clip.video_id})")
	embed.add_embed_field(name="Offset", value=format_duration(clip.offset))
	embed.add_embed_field(name="Length", value=format_duration(clip.length))

	_send_webhook(webhook, embed)


def send_pull_error(description: str, link: str):
	wh = "pull_error"
	# check if there is a webhook and it has a url, otherwise safely ignore
	if _webhooks.get(wh, None) is None or not _webhooks[wh][0].url:
		return
	
	webhook: DiscordWebhook
	embed: DiscordEmbed
	(webhook, embed) = _webhooks[wh]
	pass


def _send_webhook(webhook: DiscordWebhook, embed: DiscordEmbed):
	webhook.remove_embeds()
	webhook.add_embed(embed)
	# TODO: use async?
	try:
		resp = webhook.execute(remove_embeds=True)
	except:
		# ignore failures to connect
		pass



def send_webhook(wh:str, description:str=""):
	# check if there is a webhook and it has a url, otherwise safely ignore
	if _webhooks.get(wh, None) is None or not _webhooks[wh][0].url:
		return
	
	(webhook, embed) = _webhooks[wh]

	embed.set_description(description)
