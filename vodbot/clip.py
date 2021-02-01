import json

class Clip:
	def __init__(self, json):
		self.id = json["id"] # url: twitch.tv/videos/{id}
		self.user_id = json["broadcaster_id"]
		self.user_name = json["broadcaster_name"]
		self.clipper_id = json["creator_id"]
		self.clipper_name = json["creator_name"]
		self.title = json["title"]
		self.created_at = json["created_at"]
		self.view_count = json["view_count"]
		
		self.url = f"twitch.tv/{self.user_name}/clip/{self.id}"
	
	def __repr__(self):
		return f"Clip({self.id}, {self.user_name}, {self.created_at}, {self.duration})"
	
	def write_meta(self, filename):
		jsondict = {
			"id": self.id,
			"user_id": self.user_id,
			"user_name": self.user_name,
			"user_id": self.clipper_id,
			"user_name": self.clipper_name,
			"title": self.title,
			"created_at": self.created_at,
			"view_count": self.view_count
		}
		
		with open(filename, "w") as f:
			json.dump(jsondict, f, sort_keys=True, indent=4)
