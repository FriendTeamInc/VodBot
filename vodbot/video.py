class Video:
	def __init__(self, json):
		self.id = json["id"] # url: twitch.tv/videos/{id}
		self.user_id = json["user_id"]
		self.user_name = json["user_name"]
		self.title = json["title"]
		self.created_at = json["created_at"]
		self.duration = json["duration"]
