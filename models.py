class Workout:
	def __init__(self, id, name, description, image):
		self.id = id
		self.description = description
		self.image = image
		self.name = name			

	
	def get_description(self):
		return self.description

	def get_image(self):
		return self.image

	def get_name(self):
		return self.name

	def set_exercises(self, exercises):
		self.exercises = exercises

	def get_exercises(self):
		return self.exercises


class Exercise:
	def __init__(self, id_, description, image, name, video):
		self.id = id_
		self.description = description
		self.image = image
		self.name = name
		self.video = video

	
	def get_description(self):
		return self.description

	def get_image(self):
		return self.image

	def get_name(self):
		return self.name

	def get_video(self):
		return self.video	


class ExerciseToWorkout:
	def __init__(self, routine_id, exercise_id, length, no):
		self.exercise_id = exercise_id
		self.routine_id = routine_id		
		self.length = length
		self.no = no

	def get_length(self):
		return self.lenght

	def __copy__(self):
       		return type(self)(self.routine_id, self.exercise_id, self.length, self.no)
