import gi
import os
import re
import random
import json
import webbrowser
import sys
import tkinter

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk, GObject

from models import Workout, Exercise, ExerciseToWorkout
from client import define_connection, close

import locale

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
		self.workouts = define_connection('search_workouts', 'workouts')
		self.render_workouts()	
		
		self.wk_grid = Gtk.Grid()
		self.wk_grid.set_column_homogeneous(True)
		self.wk_grid.set_row_spacing(20)
		self.wk_grid.set_column_spacing(20)
		
		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.set_border_width(10)
		self.add(self.scrolled_window)
		self.scrolled_window.add(self.wk_grid)

		self.exercises = define_connection('search_exercises', 'exercises')
		self.render_exercises()

		self.all_exercises = []
		# make objects from all exercises in database
		for exercise_db in self.exercises:
			try:
				exercise = Exercise(exercise_db['_id'], exercise_db['description'], exercise_db['image'], exercise_db['name'], exercise_db['video'])
				self.all_exercises.append(exercise)
			except:
				pass
		self.all_workouts = []
		# make objects from all workouts in database
		exercises_not_in_db = []
		
		for index, workout_db in enumerate(self.workouts):
			workout = Workout(workout_db['_id'], workout_db['name'], workout_db['description'], workout_db['image'])
			# attach proper exercises to the workout
			exercises_of_workout = []
			
			no = 1
			for workout_ex in workout_db['exercises']:
				found_exercise_in_db = False
				for exercise in self.all_exercises:
					if found_exercise_in_db is False and workout_ex[0] == exercise.name:
						found_exercise_in_db = True
						ex_of_workout = ExerciseToWorkout(workout.id, exercise.id, workout_ex[1], no)
						no = no + 1
						exercises_of_workout.append(ex_of_workout)

				# if the exercise given with workout is not in the exercises colllection in database
				if found_exercise_in_db is False and len(sys.argv) > 1 and sys.argv[1] == "1":
					id_ = random.randint(1, 10000000)
					exercise = Exercise(id_, "None", "None", workout_ex[0], "None")
					exercises_not_in_db.append("{}".format(str(json.dumps(exercise.__dict__))))
					self.all_exercises.append(exercise)
					ex_of_workout = ExerciseToWorkout(workout.id, exercise.id, workout_ex[1], no)
					no = no + 1
					exercises_of_workout.append(ex_of_workout)
				
			# add list of exercises to the routine for faster displaying
			workout.set_exercises(exercises_of_workout)
			self.all_workouts.append(workout)

		if len(sys.argv) > 1 and sys.argv[1] == "1":
			result = define_connection("insert_ex", "{}".format(exercises_not_in_db))
			exercises_json = []
			for ex in exercises_of_workout:
				ex_json = json.dumps(ex.__dict__)
				exercises_json.append(ex_json)
			define_connection("insert_ex_to_wk", "{}".format(exercises_json))
		self.make_workouts_grid()


	def render_workouts(self):
		self.workouts = self.workouts.replace("'",'"')
		self.workouts = self.workouts.replace('""','min"')
		self.workouts = self.workouts.replace('l"',"l'")
		self.workouts = json.loads(self.workouts)
		self.workouts = self.workouts['result']['workouts']

	
	def render_exercises(self):
		self.exercises = self.exercises.replace("'",'"')
		self.exercises = self.exercises.replace('they"re',"they're")
		self.exercises = self.exercises.replace('That"s',"That's")
		self.exercises = self.exercises.replace('arm"s',"arm's")
		self.exercises = json.loads(self.exercises)
		self.exercises = self.exercises['result']['exercises']		


	def make_workouts_grid(self):
		while(self.wk_grid.get_child_at(0,0)!=None):
			self.wk_grid.remove_column(0)
		i = 0
		current_item_index = 0
		while i < len(self.all_workouts):
			# 3 workouts in a row
			for j in range(4):
				if current_item_index <= len(self.all_workouts)-1:
					workout = self.all_workouts[current_item_index]
					img = None
					try:
						img = self.get_image(workout)
					except GLib.Error:
						pass
					self.add_workout_to_grid(workout, img, j, i/4)

					current_item_index = current_item_index + 1
			i = i + 4

		self.queue_draw()
		self.show_all()


	def add_workout_to_grid(self, workout, img, column, row):
		cell_grid = Gtk.Grid()
		name = Gtk.Label()
		name.set_markup("<big><b>{}</b></big>".format(workout.name))
		frame = Gtk.Frame()
		frame.add(name)	
		cell_grid.attach(frame, 0, 0, 2, 1)

		description = ""
		try:
			for text in workout.description:
				description = description + '\n' + text
		except:
			pass
	
		if not description:
			descr_lb = Gtk.Label()
			descr_lb.set_markup("<i>no description</i>")
		else:
			descr_lb = Gtk.Label(label=description)
		descr_lb.set_line_wrap(True)
		descr_lb.set_size_request(75, 1)
		frame_d = Gtk.Frame()
		frame_d.add(descr_lb)
		scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
		scrolled_window.set_border_width(10)
		scrolled_window.set_min_content_height(200)
		scrolled_window.add(frame_d)
		cell_grid.attach(scrolled_window, 0, 3, 2, 1)

		
		if img is not None:
			cell_grid.attach(img, 0, 1, 2, 1)
		else:
			error = Gtk.Label()
			error.set_markup("<span color='red'><i>No image available</i></span>")
			frame_err = Gtk.Frame()
			frame_err.add(error)
			cell_grid.attach(frame_err, 0, 1, 2, 1)
		
		btn_show = Gtk.Button(label=self.show_btn_name)
		btn_show.connect("clicked", self.show_exercises, workout)
		cell_grid.attach(btn_show, 0, 4, 1, 1)

		btn_delete = Gtk.Button(label=self.delete_btn_name)
		btn_delete.connect("clicked", self.deletion_message, 1, workout, self.workouts)
		cell_grid.attach(btn_delete, 1, 4, 1, 1)

		colorh="#FF3333"        
		color=Gdk.RGBA()
		color.parse(colorh)
		color.to_string()
		btn_delete.override_background_color(Gtk.StateFlags.NORMAL, color)

		self.wk_grid.attach(cell_grid, column, row, 1, 1)
	

	def confirm_workout_deletion(self, widget, response_id, *data):
		if response_id == Gtk.ResponseType.OK:
			result = define_connection("delete", ("workout", data[0][1].id))
			try:
				self.all_workouts.remove(data[0][1])
				self.make_workouts_grid()
				self.create_info_message_dialog(self.operation_succeded_name, self.deletion_confirmation_name)
			except:
				self.create_info_message_dialog(self.error_occured_name, self.deletion_error_name)
		elif response_id == Gtk.ResponseType.CANCEL:
        		pass

		widget.destroy()
	

	def create_info_message_dialog(self, text, secondary_text):
		dialog = Gtk.MessageDialog(parent=self,
					modal=True,
					message_type=Gtk.MessageType.INFO,
					buttons=Gtk.ButtonsType.OK,
					text=text)
		dialog.format_secondary_text(secondary_text)
		dialog.run()
		dialog.destroy()


	def show_exercises(self, widget, *data):
		# make exercise window
		self.ex_window = Gtk.Window()
		self.ex_window.maximize()
		title = "{}".format(data[0].name)
		self.ex_window.set_title(title)
		self.ex_window.show()

		# prepare grid with exercises
		self.ex_grid = Gtk.Grid()
		self.ex_grid.set_column_homogeneous(True)
		self.ex_grid.set_column_spacing(20)

		# make window scrollable
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(10)
		self.ex_window.add(scrolled_window)
		scrolled_window.add(self.ex_grid)
		self.make_exercises_grid(data[0])


	def make_exercises_grid(self, workout):
		
		# remove exercises from the view
		while(self.ex_grid.get_child_at(0,0)!=None):
			self.ex_grid.remove_column(0)

		# add exercises to the view from self.exercise_list
		i = 0
		
		exercises_of_workout = []
		while i < len(workout.exercises):
			for ex in self.all_exercises:
				if ex.id == workout.exercises[i].exercise_id:
					exercises_of_workout.append([ex, i])
			i = i + 1

		for ex, ex_to_wk in zip(exercises_of_workout, workout.exercises):
			self.add_exercise_to_grid(ex_to_wk, ex[0], ex[1], workout)
			
		# refresh view
		self.ex_window.show_all()
			

	def add_exercise_to_grid(self, exercise_to_routine, exercise, column, workout):
		# prepare grid in given cell
		cell_grid = Gtk.Grid()
		cell_grid.set_column_homogeneous(True)

		number = Gtk.Label()  
		number.set_markup("<b>{}</b>".format(exercise_to_routine.no))              
		frame_number = Gtk.Frame()
		frame_number.add(number)
		cell_grid.attach(frame_number, 0, 0, 2, 1)

		btn_left = Gtk.Button(label="<- {}".format(self.left_name))
		btn_left.connect("clicked", self.change_exercise_position, 0, exercise_to_routine, workout)
		cell_grid.attach(btn_left, 0, 1, 1, 1)
	
		if column == 0:
			btn_left.set_sensitive(False)

		btn_right = Gtk.Button(label="{} ->".format(self.right_name))
		btn_right.connect("clicked", self.change_exercise_position, 1, exercise_to_routine, workout)
		cell_grid.attach(btn_right, 1, 1, 1, 1)	
	
		if column == len(workout.exercises)-1:
			btn_right.set_sensitive(False)
		
		name = Gtk.Label()
		name.set_markup("<big><b>{}</b></big>".format(exercise.name))
		frame_name = Gtk.Frame()
		frame_name.add(name)
		cell_grid.attach(frame_name, 0, 2, 2, 1)

		image = self.get_image(exercise)
		if image is not None:
			cell_grid.attach(image, 0, 3, 2, 1)
		else:
			error = Gtk.Label()
			error.set_markup("<span color='red'><i>No image available</i></span>")
			frame_err = Gtk.Frame()
			frame_err.add(error)
			cell_grid.attach(frame_err, 0, 3, 2, 1)

		if exercise.video is not None:
			btn_video = Gtk.Button(label=self.link_to_video_name)
			btn_video.connect("clicked", self.open_video, exercise.video)
			cell_grid.attach(btn_video, 0, 4, 2, 1)

		description = ""
		if exercise.description != "None":
			try:
				for text in exercise.description:
					description = description + "\n" + text
			except:
				pass

		if not description or description == "None":
			descr_lb = Gtk.Label()
			descr_lb.set_markup("<i>no description</i>")
		else:
			descr_lb = Gtk.Label(label=description)
		descr_lb.set_line_wrap(True)
		descr_lb.set_size_request(75, 1)
		frame_d = Gtk.Frame()
		frame_d.add(descr_lb)
		scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
		scrolled_window.set_border_width(10)
		scrolled_window.set_min_content_height(200)
		scrolled_window.set_min_content_width(200)
		scrolled_window.add(frame_d)
		cell_grid.attach(scrolled_window, 0, 5, 2, 1)
		
		btn_delete = Gtk.Button(label=self.delete_btn_name)
		btn_delete.connect("clicked", self.deletion_message, 0, exercise_to_routine, self.workouts)
		cell_grid.attach(btn_delete, 0, 6, 2, 1)

		colorh="#FF3333"        
		color=Gdk.RGBA()
		color.parse(colorh)
		color.to_string()
		btn_delete.override_background_color(Gtk.StateFlags.NORMAL, color)

		# attach cell grid to grid with exercises
		self.ex_grid.attach(cell_grid, column, 0, 1, 1)


	def open_video(self, widget, *data):
		webbrowser.open(data[0], new=0, autoraise=True)

	
	def change_exercise_position(self, widget, *data):
		exercises = data[2].exercises
		for ex in exercises:
			print(ex.no)
			print(ex.exercise_id)
			print(ex.routine_id)
		exercises_in_new_order = []
		if data[0] == 0:
			for ex in exercises:
				if ex.no == data[1].no - 1:
					ex.no = ex.no + 1
					data[1].no = data[1].no - 1
					exercises_in_new_order.append(data[1])
					exercises_in_new_order.append(ex)
				else:
					exercises_in_new_order.append(ex)
			
		elif data[0] == 1:
			exercise_to_right = None
			for ex in exercises:
				if ex.no == data[1].no + 1:
					element_to_left = ex.__copy__()
					element_to_left.no = ex.no - 1
					element_to_right = data[1].__copy__()
					element_to_right.no = data[1].no + 1
					exercises_in_new_order.append(element_to_left)
					exercises_in_new_order.append(element_to_right)
				elif ex.no != data[1].no:
					exercises_in_new_order.append(ex)

		data[2].set_exercises(exercises_in_new_order)
		for ex in data[2].exercises:
			print(ex.no)
			print(ex.exercise_id)
			print(ex.routine_id)
		self.make_exercises_grid(data[2])


	def confirm_exercise_deletion(self, widget, response_id, *data):
		if response_id == Gtk.ResponseType.OK:
			result = define_connection("delete", ("exercise", data[0][1].exercise_id))
			result = result.replace("'",'"')
			result = json.loads(result)
			if result['result'] == "OK":
				self.exercise_list.remove(data[0][1])
				self.make_exercises_grid()
				self.create_info_message_dialog(self.operation_succeded_name, self.deletion_confirmation_name)
			else:
				self.create_info_message_dialog(self.error_occured_name, self.deletion_error_name)

		elif response_id == Gtk.ResponseType.CANCEL:
        		pass
		widget.destroy()


	def deletion_message(self, widget, *data):
		messagedialog = Gtk.MessageDialog(parent=self,
						modal=True,
						message_type=Gtk.MessageType.WARNING,
						buttons=Gtk.ButtonsType.OK_CANCEL,
						text=self.deletion_question_name)
		if data[0] == 0:
        		messagedialog.connect("response", self.confirm_exercise_deletion, data)
		else:
			messagedialog.connect("response", self.confirm_workout_deletion, data)
		messagedialog.show()


	def get_image(self, object_):
		if object_.image is None:
			return None

		image = None
		path = ("img/" + object_.image)
		try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 200, 200, True)
		
			image = Gtk.Image.new_from_pixbuf(pixbuf)
		
                                       
		except GLib.Error as err:
			pass
		return image

	def get_es_translation(self):
		current_directory = os.path.dirname(os.path.realpath(__file__))
		with open(current_directory + '/settings/en-es.txt', 'r') as file_:
			data = json.load(file_)
			self.delete_btn_name = data['Delete']
			self.show_btn_name = data['Show']
			self.operation_succeded_name = data['Operation succedeed']
			self.deletion_confirmation_name = data['The object has been deleted.']
			self.link_to_video_name = data['Link to video']
			self.deletion_question_name = data['Are you sure you want to delete this object?']
			self.error_occured_name = data['Error occured']
			self.deletion_error_name = data['The object has not been deleted. Contact your administrator.']
			self.left_name = data['Left']
			self.right_name = data['Right']


	def get_en_translation(self):
		self.delete_btn_name = 'Delete'
		self.show_btn_name = 'Show'
		self.operation_succeded_name = 'Operation succedded'
		self.deletion_confirmation_name = 'The object has been deleted.'
		self.link_to_video_name = 'Link to video'
		self.deletion_question_name = 'Are you sure you want to delete this object?'
		self.error_occured_name = 'Error occured'
		self.deletion_error_name = 'The object has not been deleted. Contact your administrator.'
		self.left_name = 'Left'
		self.right_name = 'Right'


win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.maximize()
win.show_all()
Gtk.main()
