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

	def get_img_string(self):
		return self.image_string

	def set_exercises(self, exercises):
		self.exercises = exercises

	def get_exercises(self):
		return self.exercises


class Exercise:
	def __init__(self, id, description, image, name, video):
		self.id = id
		self.description = description
		self.image = image
		self.name = name
		self.video = video

	def get_name(self):
		return self.name

	def get_description(self):
		return self.description

	def get_image(self):
		return self.image

	def get_video(self):
		return self.video	


class ExerciseToRoutine:
	def __init__(self, routine_id, exercise_id, length):
		self.routine_id = routine_id
		self.exercise_id = exercise_id
		self.length = length

	def get_length(self):
		return self.lenght
