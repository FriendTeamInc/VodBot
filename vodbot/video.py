import json

class Video:
	def __init__(self, json):
		self.id = json["id"] # url: twitch.tv/videos/{id}
		self.user_id = json["user_id"]
		self.user_name = json["user_name"]
		self.title = json["title"]
		self.created_at = json["created_at"]
		self.duration = json["duration"]
		
		self.url = f"twitch.tv/videos/{self.id}"
	
	def __repr__(self):
		return f"VOD({self.id}, {self.created_at}, {self.user_name}, {self.created_at}, {self.duration})"
	
	def write_meta(self, filename):
		jsondict = {
			"id": self.id,
			"user_id": self.user_id,
			"user_name": self.user_name,
			"title": self.title,
			"created_at": self.created_at,
			"duration": self.duration
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)
