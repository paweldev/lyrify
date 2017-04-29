#!/usr/bin/env python3

import urllib.request
import re
from sys import argv
from bs4 import BeautifulSoup
import argparse
import json
import os.path

def search(search_string):
	params = {
		"q": search_string
	}

	urlencoded_params = urllib.parse.urlencode(params)

	search_url = "http://search.azlyrics.com/search.php?%s" % urlencoded_params

	try:
		search_results = urllib.request.urlopen(search_url).read()
	except:
		print("zjebało sie")
		sys.exit()

	zupa2 = BeautifulSoup(search_results, "html.parser")
	songlist = zupa2.find("table", attrs={"class": "table table-condensed"})

	if not songlist:
		print("Lyrics not found")
		return

	first_result = songlist.find("a")
	u = first_result["href"]
	return u

def lastfm(search_string):
	params = {
		"method": "user.getrecenttracks",
		"user": search_string,
		"api_key": "c6a2e66016cf51fa983210d6ed74fc83",
		"format": "json"
	}

	urlencoded_params = urllib.parse.urlencode(params)
	request_url = "http://ws.audioscrobbler.com/2.0/?%s" % urlencoded_params

	try:
		response = urllib.request.urlopen(request_url).read()
	except:
		print("zjebales, nie dostaje odpowiedzi od api")

	parse_response = json.loads(response)
	title = parse_response["recenttracks"]["track"][0]["name"]
	artist = parse_response["recenttracks"]["track"][0]["artist"]["#text"]
	search_string = title + " " + artist
	return search_string

def fetch_lyrics(u):
	try:
		content = urllib.request.urlopen(u).read()
	except:
		return -1

	zupa = BeautifulSoup(content, "html.parser")
	lyrics = zupa.find("div", attrs={'class': None, 'id': None})
	lyrics = re.sub("<.*?>","",str(lyrics))

	if lyrics is None:
		return -2

	return lyrics

def fetch_all_artist(artist, startFrom=0):
	path = os.path.dirname(os.path.realpath(__file__))
	with open("%s/.restore_method", "w") as restore_method_handle:
		restore_method_handle.write("fetch_all_lyrics")
		restore_method_handle.close()

	artist = artist.lower().strip()
	first = (artist[0:1]).lower()
	u = "http://www.azlyrics.com/%s.html" % first

	try:
		first_all_artists = urllib.request.urlopen(u).read()
	except:
		print("Invalid URL")
		return

	zupa = BeautifulSoup(first_all_artists, "html.parser")
	artist_container = zupa.find("div", attrs={"class":"container main-page"}).find("div", attrs={"class": "row"})
	artists_list = artist_container.findAll("a")

	for current_artist in artists_list:
		current_artist_name = current_artist.text.lower().strip()

		if current_artist_name == artist:
			artist_name = current_artist.text.strip()
			u = "http://www.azlyrics.com/%s" % current_artist["href"]
			break

	with open("%s/.restore_artist", "w") as restore_artist_handle:
		restore_artist_handle.write(artist_name)
		restore_artist_handle.close()

	try:
		artist_page = urllib.request.urlopen(u).read()
	except:
		print("Invalid URL")
		return

	zupa = BeautifulSoup(artist_page, "html.parser")
	songs = zupa.find("div", attrs={"id": "listAlbum"}).findAll("a", attrs={"target": "_blank"})

	os.makedirs("%s/lyrics/%s/" % (path, artist_name), exist_ok=True)

	url_pattern = "http://www.azlyrics.com/"

	for i in range(startFrom, len(songs)-startFrom)
		song = songs[i]
		song_title = re.sub("[^A-Za-z0-9\s\-\(\)\[\]\&\'\"']","_",str(song.text))
		single_path = "%s/lyrics/%s/%s.txt" % (path, artist_name, song_title)
		with open(single_path, "w+") as file:
			current_url = "%s%s" % (url_pattern, song["href"][3:])
			current_lyrics = fetch_lyrics(current_url)
			file.write(current_lyrics)
			file.close()

			with open("%s/.restore_index", "w") as restore_index_handle:
				restore_index_handle.write(str(i))
				restore_index_handle.close()

def restore():


def main():
	parser = argparse.ArgumentParser();
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-s","--search", nargs="+", help="search for particular song")
	group.add_argument("-l","--lastfm", nargs="+", help="search for lyrics of the recent song listened by a last.fm user")
	group.add_argument("--fetch-all-artist", nargs="+", help="downloads lyrics of a particular artist")
	group.add_argument("-r", "--restore", action="store_true", help="restore previous action")

	arguments = parser.parse_args()


	if arguments.search is not None:
		u = search(" ".join(arguments.search))
	elif arguments.lastfm is not None:
		recent_track = lastfm(" ".join(arguments.lastfm))
		u = search(recent_track)
	elif arguments.fetch_all_artist is not None:
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