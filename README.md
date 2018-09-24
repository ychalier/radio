# radio

A set of documentation and tools to setup an audio stream on a local RaspberryPi.

## server setup

First, let's install the server, [Icecast 2](http://icecast.org). A more complete documentation is available on the website.

		sudo apt-get install icecast2

Follow the prompts to enter a host (`localhost` here will be fine) and a password. If you want to change the port, you can edit the file /etc/icecast2/icecast.xml:

		sudo nano /etc/icecast2/icecast.xml

And edit the following line:

		<listen-socket>
				<port>8042</port>
		</listen-socket>

Restart the server and check the result:

		sudo service icecast2 restart
		sudo netstat -lptu

Then let's install the client that send the audio to the server, [Ices 2](http://icecast.org/ices/).

		sudo apt-get install libshout3-dev
		sudo aptitude install libxml2-dev
		sudo aptitude install libogg-dev
		sudo aptitude install libvorbis-dev
		wget http://downloads.us.xiph.org/releases/ices/ices-2.0.2.tar.bz2
		tar xf ices-2.0.2.tar.bz2
		cd ices-2.0.2/
		./configure
		make
		sudo make install
		sudo mkdir /var/log/ices/
		sudo touch /var/log/ices/ices.log

Then create a configuration file for Ices, following the [documentation](http://icecast.org/ices/docs/ices-2.0.2/config.html).

		sudo nano /etc/ices.xml

Check the file [ices.xml](ices.xml) for an example, or this [gist](https://gist.github.com/thcipriani/1793378). Some parameters that are prone to be changed:

 - `"random"`: `0` (songs plays in order) or `1` (songs shuffled at start)
 - `"once"`: `0` (repeats playlist when finished) or `1` (read playlist until the end)
 - `"file"`: path to an index file, with one song per line (one may comments with `#`)
 - `<mount>`: the access point that will be served by the Icecast server; writing a meaninfull extension (.ogg for example) helps clients player to know how to handle the data and avoids crashes

Then, start the server with:

		sudo ices /etc/ices.xml

If it automatically closes, check the log in /var/log/ices/ices.log.

		cat /var/log/ices/ices.log

## media files processing

Most issues will come from the encoding of the files you serve. Most basic way to do this is to encode if OGG/Vorbis, with one stream and smooth the sampling frequencies (here set at 41000Hz to level with the jingle).

This small Python [script](process.py) will handle that for you, given that `ffmpeg` is installed and has been compiled with `libvorbis`. You can check that by typing

		ffmpeg -h | grep libvorbis

If you get a result, then everything is fine. Else, you need to make a new install that includes the library for vorbis.

Then create a configuration file called *config.json* for the script, in JSON, with the following format:

		{
			"jingle_frequency": 1,
			"jingle_file": "",
			"index_file": "",
			"zip_file": "",
			"scp_cmd": "scp",
			"host": "user@ip:/path/to/folder/"
		}

Fill it with the number of songs between two jingles (`jingle_frequency`, integer), the basename of the files for the jingle, the index and the archive (i.e. without the extension and without any parent folder), and the folder to place the archive on the RaspberryPi.

Then, create a folder and put your mp3s in it. It must contain a file named as written in the configuration file, that will be used as a jingle. Then call the script from the parent folder, and give the folder with mp3s as an argument.

		python3 process.py folder

Wait for the conversion to finish. A prompt will ask you the password for the target RaspberryPi. When it closes, the archives is on the RaspberryPi, and it contains readable files for Ices.

Then on the raspberry, use the scripts [install.sh](install.sh) with as argument a path to the archive to extract the content and clean the folder, and the [run.sh](run.sh) to start Ices. It will automatically connect to the Icecast server and you should see a mountpoint on the administration panel of the server.

## custom player

Although the Icecast server allows to directly access the stream, the static file [player.html](player.html) offers a nicer GUI for the player. It will be hosted at http://yohan.chalier.fr/radio/.
