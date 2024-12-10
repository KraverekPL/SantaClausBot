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
    do_not_load_those_cogs = ['__init__']
    for filename in os.listdir('modules'):
        if filename.endswith('.py') and filename[:-3] not in do_not_load_those_cogs:
            try:
                await bot.load_extension(f'modules.{filename[:-3]}')
                logging.info(f'Loaded cog: {filename[:-3]}')
            except commands.ExtensionError as e:
                logging.error(f'Error loading cog {filename[:-3]}: {e.with_traceback(e.__traceback__)}')
    logging.info('---------------------------------------------------------------')

@bot.command(name='exit', help='Wyłącza bota')
async def exit_bot(ctx):
    allowed_user_id = os.getenv('target_user_id')  # Zastąp to właściwym ID użytkownika
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