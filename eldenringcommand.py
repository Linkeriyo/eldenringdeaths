import asyncio
from datetime import datetime

import discord
from discord.ext import commands

import fileaccess

players: list[str] = ["linkeriyo", "doris", "neko", "emerald"]
player_emojis: list[str] = ["🇱", "🇩", "🇳", "🇪"]
function_emojis: list[str] = ["💀", "↩️", "❌"]
last_deaths: list[str] = []


async def run(message: discord.Message, bot: commands.Bot) -> None:
    deaths, day = fileaccess.read_deaths_and_day_from_file(players)

    if "dia" in message.content:
        day += 1
        fileaccess.write_deaths_and_day_to_file(deaths, day)

    sent_message = await send_message(deaths, day, message)
    await add_reactions(sent_message)

    try:
        while True:
            reaction, user = await bot.wait_for('reaction_add')
            if user == bot.user:
                return

            if reaction.emoji == function_emojis[2]:
                break

            asyncio.create_task(process_reaction(reaction, user, sent_message))
    finally:
        await sent_message.delete()


async def process_reaction(reaction, user, sent_message):
    if reaction.emoji in player_emojis:
        await register_death(sent_message, reaction.emoji, user)
        await reaction.remove(user)
    elif reaction.emoji == function_emojis[0]:
        await register_death_allplayers(sent_message, user)
        await reaction.remove(user)
    elif reaction.emoji == function_emojis[1]:
        await undo_death(sent_message, user)
        await reaction.remove(user)


async def send_message(deaths, day, message):
    if len(deaths) == 0:
        return
    return await message.channel.send(get_deaths_string(deaths) + F"\n\nDÍA {day} DE ELDENCOOP")


async def add_reactions(message):
    emojis = player_emojis + function_emojis
    for emoji in emojis:
        await message.add_reaction(emoji)


def get_deaths_string(deaths: dict[str, int]) -> str:
    deaths = sorted(deaths.items(), key=lambda x: x[1], reverse=True)
    return "\n".join([f"{player}: {death_count}" for player, death_count in deaths])


async def register_death(sent_message, emoji, user):
    player_index = player_emojis.index(emoji)
    player = players[player_index]
    deaths, day = fileaccess.read_deaths_and_day_from_file(players)

    deaths[player] += 1
    add_death_to_history(player, user)

    fileaccess.write_deaths_and_day_to_file(deaths, day)
    await edit_message_with_new_deaths(sent_message, deaths, day)


async def register_death_allplayers(sent_message, user):
    deaths, day = fileaccess.read_deaths_and_day_from_file(players)

    for player in deaths:
        deaths[player] += 1
    add_death_to_history("all", user)

    fileaccess.write_deaths_and_day_to_file(deaths, day)
    await edit_message_with_new_deaths(sent_message, deaths, day)


def add_death_to_history(player, user):
    last_deaths.insert(0, player)
    if len(last_deaths) > 100:
        last_deaths.pop(99)
    log_death(player, user)


async def undo_death(sent_message, user):
    if len(last_deaths) == 0:
        return

    deaths, day = fileaccess.read_deaths_and_day_from_file(players)
    last_death = last_deaths.pop(0)

    log_death(last_death, user, True)

    if last_death == "all":
        for player in deaths:
            deaths[player] -= 1
    else:
        deaths[last_death] -= 1

    fileaccess.write_deaths_and_day_to_file(deaths, day)
    await edit_message_with_new_deaths(sent_message, deaths, day)


async def edit_message_with_new_deaths(message: discord.Message, deaths: dict[str, int], day: str) -> None:
    await message.edit(content=get_deaths_string(deaths) + F"\n\nDÍA {day} DE ELDENCOOP")


def log_death(player, user, undo=False):
    action = "UNDO" if undo else "DEATH"
    string = f"[{datetime.now()}] ({action}) {player} by {user}"
    print(string)
    fileaccess.add_to_log_file(string)
