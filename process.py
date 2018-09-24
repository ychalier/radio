import unicodedata
import subprocess
import random
import shutil
import glob
import json
import sys
import os

from string import punctuation

with open("config.json", "r") as config_file:
	config = json.loads(config_file.read())

def normalize(filename):
	base = os.path.splitext(os.path.basename(filename))[0]
	nfd = unicodedata.normalize("NFD", base)
	pct = "".join([c for c in nfd if c not in list(punctuation) + ["̀", "́"]])
	return pct.replace(" ", "_").lower() + ".ogg"

print("Converting files...", end="")
jobs = glob.glob(os.path.join(sys.argv[1], "*.mp3"))
fnull = open(os.devnull, 'w') # used to hide ffmpeg output
for i, file in enumerate(jobs):
	print("\rConverting files {0}/{1}".format(i+1, len(jobs)), end="")
	sys.stdout.flush()
	cmd = [
		"ffmpeg",
		"-i", file,
		"-y",                 # overwrite files
		"-c:a", "libvorbis",  # a vorbis ogg is needed
		"-map", "0:0",        # other streams causes issues, only 1st mp3 kept
		"-ar", "44100",       # need to unify frequencies to avoid issues
		os.path.join(sys.argv[1], normalize(file))
	]
	p = subprocess.Popen(cmd, stdout=fnull, stderr=subprocess.STDOUT)
	p.wait()
	os.remove(file)

print("\nBuilding index...")
with open(os.path.join(sys.argv[1], config["index_file"]), "w") as index:
	files = [f for f in glob.glob(os.path.join(sys.argv[1], "*.ogg"))\
			 if config["jingle_file"] not in f]
	random.shuffle(files)
	for i, file in enumerate(files):
		if i % config["jingle_frequency"] == 0:
			index.write(config["jingle_file"] + ".ogg\n")
		index.write(os.path.basename(file) + "\n")

print("Making archive...")
shutil.make_archive(config["zip_file"], 'zip', sys.argv[1])

print("Sending to server...")
subprocess.call([config["scp_cmd"], config["zip_file"]+".zip", config["host"]])

print("Erasing local archive...")
os.remove(config["zip_file"]+".zip")
