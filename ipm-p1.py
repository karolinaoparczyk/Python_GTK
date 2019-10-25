import gi
import os
import re
import random
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
from pymongo import MongoClient

from models import Routine, Exercise

client = MongoClient('localhost', 27017)
db = client.fitness

class MyWindow(Gtk.Window):

	def __init__(self):
                Gtk.Window.__init__(self, title="IPM P1")
		self.set_default_size(700, 500)
		collection = db.workouts
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(True)
		self.grid.set_row_homogeneous(True)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(10)
		self.add(scrolled_window)
		scrolled_window.add(self.grid)

		self.routine_list = []

		for index, post in enumerate(collection.find()):
			routine = Routine(post['_id'], post['name'], post['description'], post['image'])
			exercises = []
			for ex in post['exercises']:
				id = random.randint(1,100000)
				exercise = Exercise(id, ex[0], ex[1], routine.id)
				exercises.append(exercise)
			routine.set_exercises(exercises)
			self.routine_list.append(routine)
    		i = 0
		current_item_index = 0
		while i < collection.count()/3:
			for j in range(3):
				routine = self.routine_list[current_item_index]
				grid = Gtk.Grid()
				name = Gtk.Label(label=routine.name)
				frame = Gtk.Frame()
				frame.add(name)

				path = self.get_image(routine.image_string, routine.id)
				try:
					pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 200, 200, True)
					img = Gtk.Image.new_from_pixbuf(pixbuf)
					grid.attach(img, 0, 0, 2, 1)
					routine.set_img_path(path)
				except GLib.Error as err:
					pass

				grid.attach(frame, 0, 1, 2, 1)

				btn_show = Gtk.Button(label='Show')
				btn_show.connect("clicked", self.show_routine, routine)
				grid.attach(btn_show, 0, 2, 1, 1)

				btn_delete = Gtk.Button(label='Delete')
				btn_delete.connect("clicked", self.delete_routine)
				grid.attach(btn_delete, 1, 2, 1, 1)

				self.grid.attach(grid, j, i , 1, 1)
				current_item_index = current_item_index + 1
			i = i + 1

	def show_routine(self, widget, *data):
		for item in data[0].get_exercises():
			print(item.name + " " + item.length)

	def delete_routine(delf, widget):
		print("delete routine")

	def get_image(self, img_string, object_id):
		path = os.getcwd() + '/img/{}.jpeg'.format(object_id)
		with open(path, 'wb') as file:
			file.write(img_string.decode('base64'))
		return path

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
