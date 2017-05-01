#!/usr/bin/env python3

import urllib.request
import re
from sys import argv
from bs4 import BeautifulSoup
import argparse
import json
import os.path

def fetch_lyrics(u):
	try:
		content = urllib.request.urlopen(u).read()
	except:
		return -1

	zupa = BeautifulSoup(content, "html.parser")
	lyrics = zupa.find("div", attrs={'class': "song-text", 'id': None})

	if not lyrics == None:
		pattern = re.compile("<br\/>((.|\n)*)<p>")
		lyrics = pattern.search(str(lyrics))
		lyrics = re.sub("<.*?>","",str(lyrics.group(1)))

		if lyrics is None:
			return -2

		return lyrics.strip()
	else:
		return "Instrumental"

def download_all_box_przeboje_values(url):
	save_method_name(download_all_box_przeboje_values.__name__)

	u_first = url.replace("[[page]]", "1")

	try:
		result_list = urllib.request.urlopen(u_first).read()
	except:
		print("Invalid URL %s " % u_first)
		return

	zupa = BeautifulSoup(result_list, "html.parser")
	last_page_no = zupa.find("div", attrs={"class": "padding"}).findAll("a")[-2].text # -1 is the last index

	krotki = []
	for i in range(1,int(last_page_no)+1):
		try:
			single_page = urllib.request.urlopen(url.replace("[[page]]", str(i))).read()
			zupa = BeautifulSoup(single_page, "html.parser")
		except:
			print("Couldn't open url %s " % url.replace("[[page]]", str(i)))
			break

		for div in zupa.find("div",attrs={"class": "content"}).findAll("div", attrs={"class": "box-przeboje"}):
			a = div.find("a")
			krotki.append((a["href"], a.text.strip()))

	return krotki

def fetch_all_artist(artist, startFrom=0):
	save_method_name(fetch_all_artist.__name__)

	artist = artist.lower().strip()
	first = (artist[0:1])


	all_artists = download_all_box_przeboje_values("http://www.tekstowo.pl/artysci_na,%s,strona,[[page]].html" % first.upper())

	found_krotka = None
	for krotka in all_artists:
		krotka_name = re.sub("\(.+\)","",krotka[1]).strip()
		if artist == krotka_name.lower():
			found_krotka = krotka
			break

	if found_krotka is None:
		print("No band like '%s' in the database" % artist)
		return

	all_songs = download_all_box_przeboje_values("http://www.tekstowo.pl%s,alfabetycznie,strona,[[page]].html" % found_krotka[0][0:-5])
	u = "http://www.tekstowo.pl"

	path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"lyrics",artist)

	if not os.path.exists(path):
		os.mkdir(path)

	for song in all_songs[1:]:
		lyrics = fetch_lyrics("%s%s" % (u,song[0]))

		try:
			title = ((song[1].split("-"))[1].strip()).translate(str.maketrans({"/" : "-"}))
		except:
			continue

		file = open("%s/%s.txt" % (path,title), "w")
		file.write(lyrics)
		file.close()

	# zupa = BeautifulSoup(first_all_artists, "html.parser")
	# artist_container = zupa.find("div", attrs={"class":"container main-page"}).find("div", attrs={"class": "row"})
	# artists_list = artist_container.findAll("a")

	# for current_artist in artists_list:
	# 	current_artist_name = current_artist.text.lower().strip()

	# 	if current_artist_name == artist:
	# 		artist_name = current_artist.text.strip()
	# 		u = "http://www.azlyrics.com/%s" % current_artist["href"]
	# 		break

	# with open("%s/.restore_artist", "w") as restore_artist_handle:
	# 	restore_artist_handle.write(artist_name)
	# 	restore_artist_handle.close()

	# try:
	# 	artist_page = urllib.request.urlopen(u).read()
	# except:
	# 	print("Invalid URL")
	# 	return

	# zupa = BeautifulSoup(artist_page, "html.parser")
	# songs = zupa.find("div", attrs={"id": "listAlbum"}).findAll("a", attrs={"target": "_blank"})

	# os.makedirs("%s/lyrics/%s/" % (path, artist_name), exist_ok=True)

	# url_pattern = "http://www.azlyrics.com/"

	# for i in range(startFrom, len(songs)-startFrom)
	# 	song = songs[i]
	# 	song_title = re.sub("[^A-Za-z0-9\s\-\(\)\[\]\&\'\"']","_",str(song.text))
	# 	single_path = "%s/lyrics/%s/%s.txt" % (path, artist_name, song_title)
	# 	with open(single_path, "w+") as file:
	# 		current_url = "%s%s" % (url_pattern, song["href"][3:])
	# 		current_lyrics = fetch_lyrics(current_url)
	# 		file.write(current_lyrics)
	# 		file.close()

	# 		with open("%s/.restore_index", "w") as restore_index_handle:
	# 			restore_index_handle.write(str(i))
	# 			restore_index_handle.close()

def restore():
	pass

def clear_file(file):
	file.seek(0)
	file.truncate()

def save_method_name(method_name):
	path = os.path.dirname(os.path.realpath(__file__))
	with open("%s/.restore_method" % path, "w") as restore_method_handle:
		restore_method_handle.write(method_name)
		restore_method_handle.close()
def main():
	parser = argparse.ArgumentParser();
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("--fetch-all-artist", nargs="+", help="downloads lyrics of a particular artist")
	group.add_argument("-r", "--restore", action="store_true", help="restore previous action")

	arguments = parser.parse_args()

	path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"lyrics")

	restore_argument = open("./.restore_args", "w+")
	clear_file(restore_argument)

	if not os.path.exists(path):
		os.mkdir(path)

	if arguments.restore is not False:
		pass
	if arguments.fetch_all_artist is not None:
		restore_argument.write("fetch-all-artist\n%s" % (arguments.fetch_all_artist))
		fetch_all_artist(" ".join(arguments.fetch_all_artist))
		return
	elif arguments.restore == True:
		restore()
	else:
		print("zjebalo sie :(")
		return

	if content == -1:
		print("Invalid URL")
	elif content == -2:
		print("Lyrics not found")
	else:
		print(content)


if __name__ == '__main__':
	main()