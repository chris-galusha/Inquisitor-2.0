from discord.ext import commands

class Events:

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')
