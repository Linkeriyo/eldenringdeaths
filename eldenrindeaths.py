import discord
from discord.ext import commands

import fileaccess

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='eldenring', direct_message=True)
async def eldenring(ctx: commands.Context):
    from eldenringcommand import run
    await run(ctx.message, bot)


bot.run(fileaccess.read_token_from_file())
