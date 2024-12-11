# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import os
import random

from discord.ext import commands

from services.common import get_santa_busy_response
from services.open_ai_service import OpenAIService


async def send_santa_response_in_parts(channel, response):
    try:
        sentences = response.split(". ")
        for sentence in sentences:
            if sentence.strip():
                if not sentence.endswith("."):
                    sentence += "."
                async with channel.typing():
                    await asyncio.sleep(3)
                await channel.send(sentence)
    except Exception as e:
        logging.error(f"Error sending Santa response in parts: {e}")


async def get_response_from_openai(enable_ai, message, open_ai_model):
    if enable_ai:
        open_ai_service = OpenAIService(open_ai_model)
        response_from_ai = await open_ai_service.chat_with_gpt(message)
        if response_from_ai is not None:
            await send_santa_response_in_parts(message.channel, response_from_ai)
            # await message.reply(response_from_ai)
            logging.info(f"Response from OpenAi with msg: {message.content.strip()}:{response_from_ai}")
        else:
            await message.reply(get_santa_busy_response())
            logging.info(f"Message was too long. Skipping API call.")
    else:
        await message.reply(get_santa_busy_response())
        logging.info(f"OpenAi API is turned off. Sending default message.")


async def return_response_for_attachment():
    try:
        with open('resources/responses_to_image.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        random_reaction = random.choice(data['reactions'])
        return random_reaction
    except FileNotFoundError:
        logging.error("Error: File 'responses_to_image.json' not found.")
        return None


class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Event handler called when a message is received."""
        enable_ai = os.getenv("enabled_ai", 'False').lower() in ('true', '1', 't')
        open_ai_model = os.getenv('open_ai_model')
        channel_id_for_santa_claus = int(os.getenv('channel_id_for_santa_claus'))
        enabled_image_ai_analyze = os.getenv("enabled_image_ai_analyze", 'False').lower() in ('true', '1', 't')

        # Ignore messages from bot
        if message.author.bot:
            return

        # If the message has attachments
        if message.attachments:
            christmas_emojis = [
                "🎄", "🎅", "❄️", "⛄", "🎁", "🦌", "⭐", "🍪", "🥛", "🎶",
                "🕯️", "🌟", "🧑‍🎄", "🦌🎄", "🌲", "🎉", "🔔", "🍬", "🍫"
            ]
            random_emoji = random.choice(christmas_emojis)
            await message.add_reaction(random_emoji)
            if enabled_image_ai_analyze is True:
                # TODO add implementation to analyze photos
                return
            else:
                response = await return_response_for_attachment()
                async with message.channel.typing():
                    await asyncio.sleep(3)
                await message.reply(response)
                return

        # If the message has content and its on Santa Claus channel - send it to Open API gateway
        if message.channel.id == channel_id_for_santa_claus and not message.author.bot:
            await get_response_from_openai(enable_ai, message, open_ai_model)
            return

        # If the message has content and the bot is mentioned - send it to Open API gateway
        if self.bot.user.mentioned_in(message):
            await get_response_from_openai(enable_ai, message, open_ai_model)
            return


async def setup(bot):
    await bot.add_cog(ReactionCog(bot))
