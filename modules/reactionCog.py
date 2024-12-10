# -*- coding: utf-8 -*-
import logging
import os

from discord.ext import commands

from services.open_ai_service import OpenAIService


async def get_response_from_openai(enable_ai, message, open_ai_model):
    if enable_ai:
        open_ai_service = OpenAIService(open_ai_model)
        response_from_ai = open_ai_service.chat_with_gpt(message)
        if response_from_ai is not None:
            await message.reply(response_from_ai)
            logging.info(f"Response from OpenAi with msg: {message.content.strip()}:{response_from_ai}")
        else:
            await message.reply('Nie wiem,')
            logging.info(f"Message was too long. Skipping API call.")
    else:
        await message.reply('Nie wiem.')
        logging.info(f"OpenAi API is turned off. Sending default message.")


class ReactionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_message(self, message):
        """Event handler called when a message is received."""
        enable_ai = os.getenv("enabled_ai", 'False').lower() in ('true', '1', 't')
        open_ai_model = os.getenv('open_ai_model')
        # Ignore messages from bot
        if message.author.bot:
            return

        # If the message has content and the bot is mentioned - send it to Open API gateway
        if self.bot.user.mentioned_in(message):
            await get_response_from_openai(enable_ai, message, open_ai_model)


async def setup(bot):
    await bot.add_cog(ReactionCog(bot))
