import discord
from discord.ext import commands

class Voice:

    def __init__(self, bot):
        self.bot = bot
        self.voices = {}

    def __str__(self):
        return "Voice object belonging to: " + self.bot.user.name

    def get_voices(self):
        return self.voices

    @commands.command(pass_context=True)
    async def join(self, ctx):
        channel = ctx.message.author.voice_channel
        server = ctx.message.server.id
        voice = self.voices.get(server)

        if voice == None:
            self.voices[server] = await self.bot.join_voice_channel(channel)

        elif not voice.channel == channel:
            voice = await self.bot.join_voice_channel(channel)

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        server = ctx.message.server.id
        voice = self.voices.get(server)
        if voice != None:
            await voice.disconnect()
        del self.voices[server]

    @commands.command(pass_context=True)
    async def joinTo(self, ctx, *, channel : discord.Channel):
        self.voice = await self.bot.join_voice_channel(channel)
