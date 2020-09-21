import discord
import asyncio
import string
import os
import pafy
import math
import time
import random
import sys
import urllib
import urllib.parse
import urllib.request
import re
import requests
import html
import unidecode
from os import listdir
from discord.ext import commands
from discord import opus
from media import Media


RESULT_LIMIT = 6 # Default number of results listed in selection
MEDIA_DIR = '../Music'
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass

    raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))


if not discord.opus.is_loaded():
    load_opus_lib()

class Music:

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def on_ready(self):
        for server in self.bot.servers:
            self.players[server] = Audio_Player(self.bot, server)

    @commands.command(pass_context=True)
    async def play(self, ctx, *, song : str):
        player = self.players.get(ctx.message.server)
        await player.play(ctx, song)

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        player = self.players.get(ctx.message.server)
        player.pause()

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        player = self.players.get(ctx.message.server)
        player.pause()

    @commands.command(pass_context=True)
    async def queue(self, ctx):
        player = self.players.get(ctx.message.server)
        player.queue()

    @commands.command(pass_context=True)
    async def playing(self, ctx):
        player = self.players.get(ctx.message.server)
        player.playing()
        current_media = player.current_media
        if current_media:
            message = current_media.get_name()
        else:
            message = "nothing"
        await self.bot.send_message(ctx.message.channel, "Playing " + message)

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        player = self.players.get(ctx.message.server)
        player.skip()

    @commands.command(pass_context=True)
    async def stop(self, ctx):
        player = self.players.get(ctx.message.server)
        player.stop()

class Audio_Player:
    """ To handle the controls and commands pertaining to governing the opus player,
    play, pause, etc. """

    def __init__(self, bot, server):
        self.bot = bot
        self.queue = []
        self.player = None
        self.current_media = None
        self.server = server
        self.MR = Media_Retriever()
        self.votes = 0

    def get_voice(self):
        return self.bot.get_cog("Voice").get_voices().get(self.server.id)

    def clear_player(self):
        self.current_media = None
        self.player = None

    async def play(self, ctx, song):
        media_search_results = self.MR.get_media_results(song)
        media_list = self.MR.mediaListGenerator(media_search_results, RESULT_LIMIT)
        choice = await self.select(ctx, media_list)
        media = media_search_results[choice - 1]
        self.queue.append(media)
        if self.queue and not self.playing():
            await self.play_next()

    async def play_next(self):
        self.votes = 0
        if self.queue:
            media = self.queue.pop()
            title = media.get_name()
            location = media.get_location()
            location = self.MR.getStreamURL(location)
            voice = self.get_voice()
            player = await voice.create_ytdl_player(location, after=self.play_next)
            self.player = player
            self.current_media = media
        else:
            print("Queue is empty")
            self.clear_player()

    def get_quorum(self):
        pass

    async def select(self, ctx, media_list):
        description = ""
        title = str(len(media_list)) + " Results found:"
        count = 1
        for media in media_list:
            description += str(count) + '. ' + media + '\n'
            count += 1
        embed = discord.Embed(title = title, description = description, color = 0xFF0000)
        await self.bot.send_message(ctx.message.channel, embed = embed)
        reply = await self.bot.wait_for_message(timeout=30, author=ctx.message.author, channel=ctx.message.channel)
        choice = 1
        if reply.content.isdigit():
            choice = int(reply.content)

        return choice

    def pause(self):
        player = self.player
        player.pause()

    def resume(self):
        player = self.player
        player.resume()

    def skip(self):
        player = self.player
        # TODO

    def stop(self):
        player = self.player
        player.stop()
        self.clear_player()

    def playing(self):
        player = self.player
        if player:
            playing = True
        else:
            playing = False

        print(playing)

        return playing

    def queue(self):
        print(self.queue)



class Media_Retriever():

    def __init__(self):
        pass

    def get_media_results(self, query, local = False): # returns a list of search results, ["media", "media location"] based on query

        media_dir = MEDIA_DIR

        if local:

            strict = True # Is the file search strict, match query exactly vs by keywords

            media_results = self.searchLocalFiles(query, media_dir, strict)

        else:

            media_results = self.searchYoutube(query)

        return media_results

    def searchYoutube(self, query):

        media_results = []

        query_string = urllib.parse.urlencode({"search_query": query})
        html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)

        htmlDecoded = html_content.read().decode()
        htmlDecoded = html.unescape(htmlDecoded)
        htmlDecoded = unidecode.unidecode(htmlDecoded)

        titles = re.findall(r'class="yt-lockup-title ">.*?href=\"\/watch\?v=.*?><span.*?>(.*?)</span></a>.*?Duration', htmlDecoded)  # Returns video titles
        search_results = re.findall(r'class="yt-lockup-title ">.*?href=\"\/watch\?v=(.{11}).*?Duration', htmlDecoded)  # Returns the ?v="<this>" part of the video links

        for i in range(len(titles)):
            media_results.append(Media(titles[i], 'https://www.youtube.com/watch?v=' + search_results[i]))

        return media_results

    def getStreamURL(self, url):

        video = pafy.new(url)
        audio = video.getbestaudio()
        streamURL = audio.url

        return streamURL

    def mediaListGenerator(self, media_list, limit = RESULT_LIMIT):

        temp_list = []

        if len(media_list) < limit:
            limit = len(media_list)

        for i in range(limit):
            temp_list.append(media_list[i].get_name())

        return temp_list


    def searchLocalFiles(self, query, search_dir = MEDIA_DIR, strict = False):

        media_results = []

        if strict:
            query = [query.lower()]

        else:
            query = query.lower().split()

        for path, subdirs, files in os.walk(search_dir):

            for name in files:
                duplicate = False

                for term in query:

                    if term in name.lower() and '.mp3' in name.lower():

                        for i in range(len(media_results)):

                            if name == media_results[i][0]:

                                duplicate = True
                                break

                        if not duplicate:
                            media_results.append([name, os.path.join(path, name)])

        return media_results



class Media:

    def __init__(self, song_name, song_link):
        self.name = song_name
        self.location = song_link

    def get_location(self):
        return self.location

    def get_name(self):
        return self.name
