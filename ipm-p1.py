import gi
import os
import re
import random
import json
import webbrowser
from pymongo import MongoClient

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk, GObject

from models import Workout, Exercise, ExerciseToWorkout

import locale


client = MongoClient('localhost', 27017)
db = client.fitness


class MyWindow(Gtk.Window):


	def __init__(self):
		if locale.getdefaultlocale()[0] == "en_US":
			language = "en"
			self.get_en_translation()
		else:
			language = "es"
			self.get_es_translation()

                Gtk.Window.__init__(self, title="IPM P1")
		self.set_default_size(700, 500)
		
		# get collections from database
		self.workouts = db.workouts
		self.exercises = db.exercises
		
		self.wk_grid = Gtk.Grid()
		self.wk_grid.set_column_homogeneous(True)
		self.wk_grid.set_row_spacing(20)
		
		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.set_border_width(10)
		self.add(self.scrolled_window)
		self.scrolled_window.add(self.wk_grid)

		self.all_workouts = []
		self.all_exercises = []

		# make objects from all exercises in database
		for exercise_db in self.exercises.find():
			exercise = Exercise(exercise_db['_id'], exercise_db['description'], exercise_db['image'], exercise_db['name'], exercise_db['video'])
			self.all_exercises.append(exercise)

		# make objects from all workouts in database
		for index, workout_db in enumerate(self.workouts.find()):
			workout = Workout(workout_db['_id'], workout_db['name'], workout_db['description'], workout_db['image'])
			# attach proper exercises to the workout
			exercises_of_workout = []
			found_exercise_in_db = False
			for workout_ex in workout_db['exercises']:
				for exercise in self.all_exercises:
					if workout_ex[0] == exercise.name:
						found_exercise_in_db = True
						ex_of_workout = ExerciseToWorkout(workout.id, exercise.id, workout_ex[1])

				# if the exercise given with workout is not in the exercises colllection in database
				if found_exercise_in_db is False:
					id_ = random.randint(1, 10000000)
					exercise = Exercise(id_, None, None, workout_ex[0], None)
					self.all_exercises.append(exercise)
					ex_of_workout = ExerciseToWorkout(workout.id, exercise.id, workout_ex[1])

				exercises_of_workout.append(ex_of_workout)

			# add list of exercises to the routine for faster displaying
			workout.set_exercises(exercises_of_workout)
			self.all_workouts.append(workout)

		self.make_workouts_grid()


	def make_workouts_grid(self):
		while(self.wk_grid.get_child_at(0,0)!=None):
			self.wk_grid.remove_column(0)
		i = 0
                current_item_index = 0
                while i < len(self.all_workouts):
			# 3 workouts in a row
                        for j in range(3):
				if current_item_index <= len(self.all_workouts)-1:
                                	workout = self.all_workouts[current_item_index]

					img = self.get_image(workout)
					self.add_workout_to_grid(workout, img, j, i/3)

	                                current_item_index = current_item_index + 1
                        i = i + 3

		self.queue_draw()
		self.show_all()


	def add_workout_to_grid(self, workout, img, column, row):
		cell_grid = Gtk.Grid()
                name = Gtk.Label()
		name.set_markup("<b>{}</b>".format(workout.name))
                frame = Gtk.Frame()
                frame.add(name)	
		cell_grid.attach(frame, 0, 0, 2, 1)
		last_row = 1
		try:
			for index, text in enumerate(workout.description):
				description = Gtk.Label(label=text+ "                      ")
				description.set_line_wrap(True)
				description.set_size_request(75, 1)
				frame_d = Gtk.Frame()
				frame_d.add(description)
				cell_grid.attach(frame_d, 0, index+2, 2, 1)
				last_row = index+2
		except:
			pass

		if img is not None:
			cell_grid.attach(img, 0, 1, 2, 1)
		
		btn_show = Gtk.Button(label=self.show_btn_name)
                btn_show.connect("clicked", self.show_exercises, workout)
                cell_grid.attach(btn_show, 0, last_row+1, 1, 1)

   		btn_delete = Gtk.Button(label=self.delete_btn_name)
                btn_delete.connect("clicked", self.deletion_message, 1, workout, self.workouts)
                cell_grid.attach(btn_delete, 1, last_row+1, 1, 1)

		colorh="#FF3333"        
		color=Gdk.RGBA()
		color.parse(colorh)
		color.to_string()
		btn_delete.override_background_color(Gtk.StateFlags.NORMAL, color)

		self.wk_grid.attach(cell_grid, column, row, 1, 1)
	

	def confirm_workout_deletion(self, widget, response_id, *data):
        	if response_id == Gtk.ResponseType.OK:
            		routine = {"_id": data[0][1].id}
			self.all_workouts.remove(data[0][1])
			#self.workouts.delete_one(routine)

			self.make_workouts_grid()

			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, self.operation_succedeed_name)
        		dialog.format_secondary_text(self.deletion_confirmation_name)
        		dialog.run()
        		dialog.destroy()

        	elif response_id == Gtk.ResponseType.CANCEL:
        		pass

		widget.destroy()

	def show_exercises(self, widget, *data):
		# make exercise window
		self.ex_window = Gtk.Window()
		self.ex_window.set_size_request(350, 500)
		title = "{}".format(data[0].name)
		self.ex_window.set_title(title)
		self.ex_window.show()

		# prepare grid with exercises
		self.ex_grid = Gtk.Grid()
		self.ex_grid.set_column_homogeneous(True)
		self.ex_grid.set_row_spacing(20)

		# make window scrollable
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(10)
		self.ex_window.add(scrolled_window)
		scrolled_window.add(self.ex_grid)
		self.exercise_list = data[0].get_exercises()
		self.make_exercises_grid()


	def make_exercises_grid(self):
		# remove exercises from the view
		while(self.ex_grid.get_child_at(0,0)!=None):
			self.ex_grid.remove_column(0)

		# add exercises to the view from self.exercise_list
		i = 0
                while i < len(self.exercise_list):
			for ex in self.all_exercises:
				if ex.id == self.exercise_list[i].exercise_id:                                 						self.add_exercise_to_grid(self.exercise_list[i], ex, i)
			i = i + 1
		# refresh view
		self.ex_window.show_all()
			

	def add_exercise_to_grid(self, exercise_to_routine, exercise, row):
		# prepare grid in given cell
		cell_grid = Gtk.Grid()
		
		number = Gtk.Label(label=row+1)                
		frame_number = Gtk.Frame()
		frame_number.add(number)
		cell_grid.attach(frame_number, 0, 0, 1, 1)

		name = Gtk.Label(label="                     "+exercise.name+"                     ")
                frame_name = Gtk.Frame()
                frame_name.add(name)
		cell_grid.attach(frame_name, 0, 1, 1, 1)

		image = self.get_image(exercise)
		if image is not None:
			cell_grid.attach(image, 0, 2, 1, 1)

		if exercise.video is not None:
			btn_video = Gtk.Button(label=self.link_to_video_name)
			btn_video.connect("clicked", self.open_video, exercise.video)
			cell_grid.attach(btn_video, 0, 3, 1, 1)

		# in case there is no description
		last_row = 3
		try:
			for index, text in enumerate(exercise.description):
				description = Gtk.Label(label=text+ "                      ")
				description.set_line_wrap(True)
				description.set_size_request(75, 1)
				frame_d = Gtk.Frame()
				frame_d.add(description)
				cell_grid.attach(frame_d, 0, index+4, 1, 1)
				last_row = index+4
		except:
			pass	

   		btn_delete = Gtk.Button(label=self.delete_btn_name)
                btn_delete.connect("clicked", self.deletion_message, 0, exercise_to_routine, self.workouts)
                cell_grid.attach(btn_delete, 0, last_row+1, 1, 1)

		colorh="#FF3333"        
		color=Gdk.RGBA()
		color.parse(colorh)
		color.to_string()
		btn_delete.override_background_color(Gtk.StateFlags.NORMAL, color)

		# attach cell grid to grid with exercises
		self.ex_grid.attach(cell_grid, 0, row, 1, 1)


	def open_video(self, widget, *data):
		webbrowser.open(data[0], new=0, autoraise=True)


	def confirm_exercise_deletion(self, widget, response_id, *data):
        	if response_id == Gtk.ResponseType.OK:
			self.exercise_list.remove(data[0][1])
		
			# delete from database
			#self.exercises.delete_one(exercise)

			# refresh grid with exercises after deletion
			self.make_exercises_grid()
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, self.operation_succedeed_name)
        		dialog.format_secondary_text(self.deletion_confirmation_name)
        		dialog.run()
        		dialog.destroy()
        	elif response_id == Gtk.ResponseType.CANCEL:
        		pass
		widget.destroy()


	def deletion_message(self, widget, *data):
		messagedialog = Gtk.MessageDialog(parent=self,
						flags=Gtk.DialogFlags.MODAL,
						type=Gtk.MessageType.WARNING,
						buttons=Gtk.ButtonsType.OK_CANCEL,
						message_format=self.deletion_question_name)
		if data[0] == 0:
        		messagedialog.connect("response", self.confirm_exercise_deletion, data)
		else:
			messagedialog.connect("response", self.confirm_workout_deletion, data)
        	messagedialog.show()


	def get_image(self, object_):
		if object_.image_string is None:
			return None

		image = None
		path = self.get_image_path(object_.image_string, object_.id)
	        try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 200, 200, True)
                        image = Gtk.Image.new_from_pixbuf(pixbuf)
                                        
                except GLib.Error as err:
                       	pass
		return image


	def get_image_path(self, img_string, object_id):
		current_directory = os.path.dirname(os.path.realpath(__file__))
		path = current_directory + '/img/{}.jpeg'.format(object_id)
		with open(path, 'wb') as file_:
			file_.write(img_string.decode('base64'))
		return path

	def get_es_translation(self):
		current_directory = os.path.dirname(os.path.realpath(__file__))
		with open(current_directory + '/settings/en-es.txt', 'r') as file_:
			data = json.load(file_)
			self.delete_btn_name = data['Delete']
			self.show_btn_name = data['Show']
			self.operation_succedeed_name = data['Operation succedeed']
			self.deletion_confirmation_name = data['The object has been deleted.']
			self.link_to_video_name = data['Link to video']
			self.deletion_question_name = data['Are you sure you want to delete this object?']


	def get_en_translation(self):
		self.delete_btn_name = 'Delete'
		self.show_btn_name = 'Show'
		self.operation_succedeed_name = 'Operation succedded'
		self.deletion_confirmation_name = 'The object has been deleted.'
		self.link_to_video_name = 'Link to video'
		self.deletion_question_name = 'Are you sure you want to delete this object?'


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
