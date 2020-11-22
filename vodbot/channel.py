class Channel:
	def __init__(self, json):
		self.id = json["id"]
		self.login = json["login"]
		self.display_name = json["display_name"]
		self.created_at = json["created_at"]
