import gi
import os
import re
import random
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk, GObject
from pymongo import MongoClient

from models import Routine, Exercise

client = MongoClient('localhost', 27017)
db = client.fitness

class MyWindow(Gtk.Window):

	def routine_details(self, widget, *data):
		self.ex_window = Gtk.Window()
		self.ex_window.set_size_request(700, 500)
		title = "Routine {} details".format(data[0].name)
		self.ex_window.set_title(title
)
		self.ex_window.show()

		self.ex_grid = Gtk.Grid()
		self.ex_grid.set_column_homogeneous(True)
		self.ex_grid.set_row_homogeneous(True)
		self.ex_grid.set_row_spacing(20)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(10)
		self.ex_window.add(scrolled_window)
		scrolled_window.add(self.ex_grid)

		self.exercise_list = data[0].get_exercises()
		self.get_exercises()

	def get_exercises(self):
		while(self.ex_grid.get_child_at(0,0)!=None):
			self.ex_grid.remove_column(0)
		i = 0
                current_item_index = 0
                while i < len(self.exercise_list):
                        for j in range(3):
				if current_item_index <= len(self.exercise_list)-1:
                                	exercise = self.exercise_list[current_item_index]
					self.add_ex_to_grid(exercise, current_item_index+1, j, i/3)
	                                current_item_index = current_item_index + 1
                        i = i + 3
		self.ex_window.queue_draw()
		self.ex_window.show_all()
			

	def add_ex_to_grid(self, exercise, no, column, row):
		
		cell_grid = Gtk.Grid()
		number = Gtk.Label(label=no)                
		name = Gtk.Label(label=exercise.name)
                frame_name = Gtk.Frame()
		frame_number = Gtk.Frame()
                frame_name.add(name)
		frame_number.add(number)

		cell_grid.attach(frame_name, 0, 2, 2, 1)
		cell_grid.attach(frame_number, 0, 1, 2, 1)

   		btn_delete = Gtk.Button(label='Delete')
                btn_delete.connect("clicked", self.delete_exercise, exercise, self.collection)
                cell_grid.attach(btn_delete, 0, 3, 1, 1)

		colorh="#FF0000"        
		color=Gdk.RGBA()
		color.parse(colorh)
		color.to_string()
		btn_delete.override_background_color(Gtk.StateFlags.NORMAL, color)

		self.ex_grid.attach(cell_grid, column, row, 1, 1)

	def delete_exercise(self, widget, *data):
		messagedialog = Gtk.MessageDialog(parent=self,
						flags=Gtk.DialogFlags.MODAL,
						type=Gtk.MessageType.WARNING,
						buttons=Gtk.ButtonsType.OK_CANCEL,
						message_format="Are you sure you want to delete this object?")
        	messagedialog.connect("response", self.remove_exercise, data)
        	messagedialog.show()

	def remove_exercise(self, widget, response_id, *data):
        	if response_id == Gtk.ResponseType.OK:
            		exercise = {"_id": data[0][0].id}
			self.exercise_list.remove(data[0][0])
			#self.collection.delete_one(exercise)
			self.get_workouts()
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Operation succedeed")
        		dialog.format_secondary_text("The object has been deleted.")
        		dialog.run()
        		dialog.destroy()
        	elif response_id == Gtk.ResponseType.CANCEL:
        		pass
		widget.destroy()

	def __init__(self):
                Gtk.Window.__init__(self, title="IPM P1")
		self.set_default_size(700, 500)
		self.collection = db.workouts
		
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(True)
		self.grid.set_row_homogeneous(True)
		self.grid.set_row_spacing(20)
		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.set_border_width(10)
		self.add(self.scrolled_window)
		self.scrolled_window.add(self.grid)

		self.routine_list = []

		for index, post in enumerate(self.collection.find()):
			routine = Routine(post['_id'], post['name'], post['description'], post['image'])
			exercises = []
			for ex in post['exercises']:
				id = random.randint(1,100000)
				exercise = Exercise(id, ex[0], ex[1], routine.id)
				exercises.append(exercise)
			routine.set_exercises(exercises)
			self.routine_list.append(routine)
		self.get_workouts()

		

	def add_to_grid(self, routine, img, column, row):
		
		cell_grid = Gtk.Grid()
                name = Gtk.Label(label=routine.name)
                frame = Gtk.Frame()
                frame.add(name)	
		
		if img is not None:
			cell_grid.attach(img, 0, 0, 2, 1)
		cell_grid.attach(frame, 0, 1, 2, 1)

		btn_show = Gtk.Button(label='Show')
                btn_show.connect("clicked", self.routine_details, routine)
                cell_grid.attach(btn_show, 0, 2, 1, 1)

   		btn_delete = Gtk.Button(label='Delete')
                btn_delete.connect("clicked", self.delete_routine, routine, self.collection)
                cell_grid.attach(btn_delete, 1, 2, 1, 1)

		colorh="#FF0000"        
		color=Gdk.RGBA()
		color.parse(colorh)
		color.to_string()
		btn_delete.override_background_color(Gtk.StateFlags.NORMAL, color)

		self.grid.attach(cell_grid, column, row, 1, 1)


	def get_workouts(self):
		while(self.grid.get_child_at(0,0)!=None):
			self.grid.remove_column(0)
		i = 0
                current_item_index = 0
                while i < len(self.routine_list):
                        for j in range(3):
				if current_item_index <= len(self.routine_list)-1:
                                	routine = self.routine_list[current_item_index]
					img = self.get_image(routine)
					self.add_to_grid(routine, img, j, i/3)
	                                current_item_index = current_item_index + 1
                        i = i + 3
		self.queue_draw()
		self.show_all()


	def get_image(self, routine):
		img = None
		path = self.get_image_path(routine.image_string, routine.id)
	        try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 200, 200, True)
                        img = Gtk.Image.new_from_pixbuf(pixbuf)
                                        
                except GLib.Error as err:
                       	pass
		return img

	def delete_routine(self, widget, *data):
		messagedialog = Gtk.MessageDialog(parent=self,
						flags=Gtk.DialogFlags.MODAL,
						type=Gtk.MessageType.WARNING,
						buttons=Gtk.ButtonsType.OK_CANCEL,
						message_format="Are you sure you want to delete this object?")
        	messagedialog.connect("response", self.dialog_response, data)
        	messagedialog.show()

	def dialog_response(self, widget, response_id, *data):
        	if response_id == Gtk.ResponseType.OK:
            		routine = {"_id": data[0][0].id}
			self.routine_list.remove(data[0][0])
			#self.collection.delete_one(routine)
			self.get_workouts()
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Operation succedeed")
        		dialog.format_secondary_text("The object has been deleted.")
        		dialog.run()
        		dialog.destroy()
        	elif response_id == Gtk.ResponseType.CANCEL:
        		pass
		widget.destroy()

	def get_image_path(self, img_string, object_id):
		path = '/home/karolina/ipm1920-p1/img/{}.jpeg'.format(object_id)
		with open(path, 'wb') as file:
			file.write(img_string.decode('base64'))
		return path

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
