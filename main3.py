
import asyncio, os
from games import Games
from events import Events
from music import Music
from administration import Administration
from discord.ext import commands

tasks = []

def startBots():
    loop = asyncio.get_event_loop()
    gathered = asyncio.gather(*tasks, loop=loop)
    loop.run_until_complete(gathered)

def createBotTask(bot, token):
    loop = asyncio.get_event_loop()
    tasks.append(loop.create_task(bot.start(token)))


def setupBot(prefix, token_file_location, description="A Discord Bot that does Discordy things."):
    file = open(token_file_location)
    token = file.readline().strip("\n")
    bot = commands.Bot(command_prefix=prefix, description=description)
    bot.add_cog(Games(bot))
    bot.add_cog(Events(bot))
    bot.add_cog(Music(bot))
    bot.add_cog(Administration(bot))

    createBotTask(bot, token)

    return bot

if __name__ == "__main__":
    emperor = setupBot("~", os.path.join("../discord_bot_tokens/", r"emperor_token.txt"), "A Discord bot for doing Discordy things and purging heresy.")

    startBots()
