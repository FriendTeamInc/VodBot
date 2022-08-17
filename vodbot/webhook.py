# Module to ship webhooks out to various places, currently only Discord is supported
from .config import Config

from discord_webhook import DiscordWebhook, DiscordEmbed

_config_attributes = {
	"pull_vod": "VodBot Pulled VOD",
	"pull_clip": "VodBot Pulled Clip",
	"pull_job_done": "VodBot Pull Job Done",
	"export_video": "VodBot Exported Video",
	"export_job_done": "VodBot Export Job Done",
	"upload_video": "VodBot Uploaded Video",
	"upload_job_done": "VodBot Upload Job Done"
}
_webhooks = {atrb: None for atrb in _config_attributes}


def init_webhooks(conf: Config):
	# check main toggle
	if not conf.webhooks.enable:
		return

	for atrb, title in _config_attributes.items:
		confwh = getattr(conf, atrb)

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
		webhook = DiscordWebhook(url=url, content=message)
		embed = DiscordEmbed(title=title)

		embed.set_url("https://vodbot.friendteam.biz")
		embed.set_footer(text="VodBot by NotQuiteApex & F.T.I.")

		_webhooks[atrb] = (webhook, embed)


def send_webhook(wh:str, description:str=""):
	if _webhooks.get(wh, None) == None:
		return
	
	(webhook, embed) = _webhooks[wh]

	embed.set_description(description)

	# TODO: use async?
	resp = webhook.execute()
