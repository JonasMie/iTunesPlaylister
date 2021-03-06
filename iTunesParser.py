# -*- coding: utf-8 -*-

#  Created by Jonas Miederer.
#  Date: 27.03.16
#  Time: 17:44
#  Project: iTunesPlaylister
#  We're even wrong about which mistakes we're making. // Carl Winfield
#

import plistlib
import logging
import re

logger = logging.getLogger('iTunesPlaylister')


class Track:
    def __init__(self):
        self.id = None
        self.name = None
        self.artist = None
        self.duration = -1
        self.path = None


class Playlist:
    def __init__(self, playlist, file):
        self.pl = playlist
        self.itlist = file
        self.id = playlist['Playlist ID']
        self.title = playlist['Name']
        self.songs = self.getSongs()
        logger.info('Parsing playlist {}'.format(playlist['Name']))

    def getSongs(self):
        songs = list()
        if 'Playlist Items' in self.pl:
            for song in self.pl['Playlist Items']:
                track = Track()
                track.id = song['Track ID']
                track_obj = self.itlist['Tracks']['{}'.format(track.id)]

                logger.debug('Parsing song {} by {}'.format(track_obj['Name'] if 'Name' in track_obj else '',
                                                            track_obj['Artist'] if 'Artist' in track_obj else ''))

                track.name = track_obj['Name'] if 'Name' in track_obj else ''
                track.artist = track_obj['Artist'] if 'Artist' in track_obj else ''
                track.duration = int(track_obj['Total Time'] / 1000) if 'Total Time' in track_obj else -1
                track.path = re.sub(".+?(?=ultimedia)", "/share/M", track_obj['Location']).replace("%20", " ")
                songs.append(track)
        else:
            logger.warn('Playlist {} does not contain any songs.'.format(self.pl['Name']))
        return songs


class iTunesParser:
    def __init__(self, iTunesFile):
        self.file = iTunesFile
        self.playlists = list()

    def parse(self):
        logger.info('Started parsing playlist.')

        self.itlist = plistlib.readPlist(self.file)
        for playlist in self.itlist['Playlists']:
            if playlist['Name'] not in (
                    '####!####', 'Musik', 'Musikvideos', 'Leihobjekte', 'Filme', 'Eigene Videos', 'TV-Sendungen',
                    'Podcasts',
                    'iTunes U', 'Bücher', 'Hörbücher', 'PDFs', 'Genius',
                    'Klassische Musik', 'Einkäufe', 'Gekauft mit Mein iPod') and 'iTunesU' not in playlist:
                self.playlists.append(Playlist(playlist, self.itlist))
        return self.playlists
