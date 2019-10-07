#!/usr/bin/python3
# -*-coding:Utf-8 -*

#CALL SAMPLE : ./WallpaperSlideshow.py /path/to/folder recurrencyInSeconds
#CALL EXAMPLE : ./WallpaperSlideshow.py /home/bdeliers/Pictures/WallpaperSlideshow 30

# Environment variables, list directory
from os import environ, listdir
# Is directory, is file
from os.path import isdir, isfile
# Argv
from sys import argv
# Sleep
from time import sleep
# Shuffle list
from random import shuffle
# Call bash command
from subprocess import call
# Visual notification
import notify2
# Threading
import threading

class ChangerThread(threading.Thread):
	def __init__(self, slideshow):
		threading.Thread.__init__(self)
		self.slideshow = slideshow

	def run(self):
		self._running = True

		while self._running:
			# Shuffle wallpapers list
			shuffle(self.slideshow.wallpapers)

			for wallpaper in self.slideshow.wallpapers:
				if self._running:
					# Set wallpaper
					self.slideshow.setWallpaper("{}/{}".format(self.slideshow.wallpapersDir, wallpaper))

					# Sleep
					sleep(self.slideshow.interval)

				else:
					break

	def stop(self):
		self._running = False

class WallpaperSlideshow:
	"""

		Simple wallpaper slideshow
		by BDeliers, August 2018
		Under GPL 3.0 License

		Simple wallpaper changer which changes your wallpaper randomly from a given directory on a defined interval on GNOME/Gconf based Linux desktop environments

	"""

	def __init__(self, wallpapersDir, interval):
		# Get window manager
		self._X_SERVER = environ["XDG_CURRENT_DESKTOP"]
		# Gconf setting
		self._GCONF_WALLPAPER = {
							"Deepin" : "com.deepin.wrap.gnome.desktop.background",
							"GNOME" : "org.gnome.desktop.background",
							"X-Cinnamon" : "org.cinnamon.desktop.background",
							"ubuntu:GNOME" : "org.gnome.desktop.background",
							"Unity" : "org.gnome.desktop.background"
						}
		self.wallpapersDir = wallpapersDir
		self.interval = int(interval)
		self.wallpapers = []

	def isCompatible(self):
		"""
			Returns True if your desktop environment is compatible with the program
		"""

		# If we know how to set wallpaper with this X_SERVER
		if (self._X_SERVER in self._GCONF_WALLPAPER.keys()):
			return True

		else:
			return False

	def listWallpapers(self):
		"""
			List all wallpapers from given directory path
		"""

		# Remove '/' of end of dir
		if self.wallpapersDir.endswith('/'):
			self.wallpapersDir = self.wallpapersDir[:-1]

		if isdir(self.wallpapersDir):
			# Delete all wallpapers
			self.wallpapers = []
			# For all elements in directory
			for element in listdir(self.wallpapersDir):
				# If is png, jpeg or jpg, append to wallpapers list
				if (isfile(element) and element.lower().endswith(".png") or element.lower().endswith(".jpeg") or element.lower().endswith(".jpg")):
					self.wallpapers.append(element)

			self.wallpapers.sort()
		else:
			raise Exception("Invalid directory")

	def setWallpaper(self, wallpaper):
		"""
			Set wallpaper with gsettings
		"""

		call("gsettings set {} picture-uri '{}'".format(self._GCONF_WALLPAPER[self._X_SERVER] ,wallpaper), shell=True)

	def runSlideshow(self):
		"""
			Run the slideshow in a thread
		"""

		# If invalid interval
		if not (int(self.interval) > 0):
			print("Invalid time interval")

		# Get wallpapers
		self.listWallpapers()

		# If empty wallpapers list
		if len(self.wallpapers) == 0:
			print("No wallpapers in directory")

		# If everything is valid
		if (len(self.wallpapers) > 0 and self.interval > 0):
			# Prepare notification
			notify2.init("Wallpaper Slideshow")
			notif = notify2.Notification("Wallpaper Slideshow", "Slideshow has started !", "start")

			# Create thread
			self._thread = ChangerThread(self)
			# Start thread
			self._thread.start()

			# Show notification
			notif.show()

			return True

		else:
			return False

	def stopSlideshow(self):
		"""
			Stop the slideshow in the thread
		"""

		self._thread.stop()

		# Prepare notification
		notify2.init("Wallpaper Slideshow")
		notif = notify2.Notification("Wallpaper Slideshow", "Slideshow is stopped !", "stop")
		# Show notification
		notif.show()

		return True


if __name__ == "__main__":
	slideshow = WallpaperSlideshow(argv[1], argv[2])

	if slideshow.isCompatible():
		try:
			slideshow.runSlideshow()
			print("Started")
		except:
			slideshow.stopSlideshow()
			print("Stopped")

	else:
		print("Not compatible with your X_SERVER")
