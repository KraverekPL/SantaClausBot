import logging
import asyncio
import os
import random
import json
import discord

from dotenv import load_dotenv
from discord.ext import commands, tasks

# Logging configuration
load_dotenv(".env")
logging.basicConfig(level=os.getenv('log_level'), format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logging.info('---------------------------------------------------------------')
    logging.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logging.info(f'Log level: ' + os.getenv('log_level'))
    logging.info(f'Enable AI (OpenAI): ' + os.getenv('enabled_ai'))
    logging.info(f'Message history enabled: ' + os.getenv('message_history_enabled'))
    logging.info(f'Message history limit: ' + os.getenv('message_history_limit'))
    logging.info(f'OpenAI model: ' + os.getenv('open_ai_model'))
    logging.info(f'OpenAI max tokens: ' + os.getenv('open_ai_max_tokens'))
    logging.info(f'OpenAI temperature: ' + os.getenv('open_ai_temperature'))
    logging.info(f'OpenAI top p: ' + os.getenv('open_ai_top_p'))
    logging.info(f'OpenAI enabled  images creation: ' + os.getenv('enabled_image_ai_analyze'))
    logging.info(f'Max messages per day: ' + os.getenv('open_ai_max_number_of_messages_per_guild_per_day'))
    logging.info(f'Bot is in {len(bot.guilds)} guilds.')
    do_not_load_those_cogs = ['__init__']
    for filename in os.listdir('modules'):
        if filename.endswith('.py') and filename[:-3] not in do_not_load_those_cogs:
            try:
                await bot.load_extension(f'modules.{filename[:-3]}')
                logging.info(f'Loaded cog: {filename[:-3]}')
            except commands.ExtensionError as e:
                logging.error(f'Error loading cog {filename[:-3]}: {e.with_traceback(e.__traceback__)}')
    logging.info('---------------------------------------------------------------')


@bot.command(name='say', help='Pozwala rozmawiac jako Mikolaj')
async def say_as_bot(ctx, *, message: str):
    try:
        if not message:
            logging.info("Message for command say is empty.")
            return
        channel_id = int(os.getenv('channel_id_for_talking'))
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message)
            logging.info(f"Message sent to channel with id {channel_id}: {message}")
        else:
            logging.error(f"Channel with id {channel_id} not found.")
    except Exception as e:
        logging.error(f"Error sending message: {e}")


@bot.command(name='exit', help='Wyłącza Mikołaja')
async def exit_bot(ctx):
    allowed_user_id = os.getenv('target_user_id')
    if ctx.author.id == int(allowed_user_id):
        logging.info("Bot was closed by creator.")
        await ctx.send('Bot zostanie teraz wyłączony.')
        await bot.close()
    else:
        await ctx.send('Nie masz uprawnień do tej komendy.')
        logging.info(f"There was an attempt to disable the bot by the user: {ctx.author.id}")


async def main():
    try:
        await bot.start(os.getenv("BOT_TOKEN"))
    except Exception as e:
        logging.error(f'An error occurred: {e}')
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
