class Workout:
	def __init__(self, id, name, description, image_string):
		self.id = id
		self.description = description
		self.image_string = image_string
		self.name = name			

	
	def get_description(self):
		return self.description

	def get_image_string(self):
		return self.image_string

	def get_name(self):
		return self.name

	def set_exercises(self, exercises):
		self.exercises = exercises

	def get_exercises(self):
		return self.exercises


class Exercise:
	def __init__(self, id_, description, image_string, name, video):
		self.id = id_
		self.description = description
		self.image_string = image_string
		self.name = name
		self.video = video

	
	def get_description(self):
		return self.description

	def get_image_string(self):
		return self.image_string

	def get_name(self):
		return self.name

	def get_video(self):
		return self.video	


class ExerciseToWorkout:
	def __init__(self, routine_id, exercise_id, length):
		self.exercise_id = exercise_id
		self.routine_id = routine_id		
		self.length = length

	def get_length(self):
		return self.lenght
