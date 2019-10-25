import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib
from pymongo import MongoClient

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

		self.post_list = []

		for index, post in enumerate(collection.find()):
			self.post_list.append(post)
	       		
		i = 0
		current_item_index = 0
		while i < collection.count()/3:
			for j in range(3):
				grid = Gtk.Grid()
				name = Gtk.Label(label=self.post_list[current_item_index]['name'])
				frame = Gtk.Frame()
				frame.add(name)

				path = self.get_image(self.post_list[current_item_index]['image'], self.post_list[current_item_index]['_id'])
				try:
					pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 200, 200, True)
					img = Gtk.Image.new_from_pixbuf(pixbuf)
					grid.attach(img, 0, 0, 2, 1)
				except GLib.Error as err:
					print(err)

				grid.attach(frame, 0, 1, 2, 1)

				btn_show = Gtk.Button(label='Show')
				btn_show.connect("clicked", self.show_routine)
				grid.attach(btn_show, 0, 2, 1, 1)

				btn_delete = Gtk.Button(label='Delete')
				btn_delete.connect("clicked", self.delete_routine)
				grid.attach(btn_delete, 1, 2, 1, 1)

				self.grid.attach(grid, j, i , 1, 1)
				current_item_index = current_item_index + 1
			i = i + 1

	def show_routine(self, widget):
        	print("show routine")

	def delete_routine(delf, widget):
		print("delete routine")

	def get_image(self, img_string, object_id):
		path = os.getcwd() + '/img/{}.jpeg'.format(object_id)
		print(img_string)
		print('****************************')		
		with open(path, 'wb') as file:
			file.write(img_string.decode('base64'))
		return path

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
