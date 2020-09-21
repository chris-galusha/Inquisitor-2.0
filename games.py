from discord.ext import commands
import random


class Games:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, dice : str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await self.bot.say(result)

    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, *choices : str):
        """Chooses between multiple choices."""
        await self.bot.say(random.choice(choices))

    @commands.command(pass_context=True)
    async def speak(self, ctx):
        phrase = ctx.message.content.split(' ', 1)[1]
        print(phrase)
        await self.bot.say(phrase)
