class Routine:
	def __init__(self, id, name, description, image_string):
		self.id = id
		self.name = name
		self.description = description
		self.image_string = image_string

	def get_name(self):
		return self.name

	def get_description(self):
		return self.description

	def get_img_path(self):
		return self.image

	def set_img_path(self, img_path):
		self.img_path = img_path

	def set_exercises(self, exercises):
		self.exercises = exercises

	def get_exercises(self):
		return self.exercises



class Exercise:
	def __init__(self, id, name, length, routine):
		self.id = id
		self.name = name
		self.length = length
		self.routine = routine

	def get_name(self):
		return self.name

	def get_description(self):
		return self.description

	def get_length(self):
		return self.length
