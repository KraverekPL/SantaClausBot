# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import random
import re
import time

import discord
import openai
from discord.ext import commands
from openai import OpenAI

import openai
import requests
from io import BytesIO
from PIL import Image

GPT___TURBO_ = 'gpt-3.5-turbo-0125'

GPT___TURBO_INSTRUCT = 'gpt-3.5-turbo-instruct'

last_user_message_times = {}


def get_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_activity",
                "description": "Get user's activity",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID, always found in format <@1234567890>"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
    ]
    return tools


def get_messages(ai_behaviour: str, message_to_ai):
    user_id_pattern = re.compile(r'<@!?1315827200770969693>')  # remove bot id from msg
    cleaned_content = user_id_pattern.sub('', message_to_ai.content.strip())
    # user_name = message_to_ai.author.display_name
    prompt = cleaned_content
    messages = [
        {
            "role": "system",
            "content": ai_behaviour
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return messages


def can_user_send_message(user_id):
    if user_id not in last_user_message_times:
        last_user_message_times[user_id] = []

    delay_new_message_per_user = int(os.getenv('open_ai_number_of_msg_per_sec_user'))
    if last_user_message_times[user_id]:
        last_user_message_time = last_user_message_times[user_id][-1]
    else:
        last_user_message_time = 0

    elapsed_time = time.time() - last_user_message_time
    if elapsed_time >= delay_new_message_per_user:
        last_user_message_times[user_id].append(time.time())
        return True
    else:
        return False


def can_guild_send_message(guild_id):
    today = datetime.date.today().strftime("%Y-%m-%d")
    file_path = f"guild_data_{guild_id}.json"
    max_number_msg = int(os.getenv('open_ai_max_number_of_messages_per_guild_per_day'))
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                guild_data = json.load(file)
            except json.JSONDecodeError:
                guild_data = {}
    else:
        guild_data = {}

    if today not in guild_data:
        guild_data[today] = 0
    remain_requests = int(max_number_msg) - int(guild_data[today])
    logging.info(f'Remaining requests for guild {guild_id}: {max_number_msg}-{guild_data[today]}={remain_requests} ')
    if guild_data[today] < max_number_msg:
        guild_data[today] += 1
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(guild_data, file)
        return True
    else:
        return False


async def add_history_to_message(message, limit):
    boundary_conditions = "Używaj prostego języka. Nie dodawaj na początku Mikołaj:"
    if not isinstance(message.channel, (discord.TextChannel, discord.DMChannel, discord.Thread)):
        logging.warning(f"Channel type does not support history: {type(message.channel)}")
    else:
        try:
            original_message = message.content.strip()
            history = []
            async for msg in message.channel.history(limit=int(limit)):
                history.append(msg)
            history.reverse()
            history_response = "Historia czatu:\n"
            for msg in history:
                if msg.author.bot:
                    history_response += f"Mikołaj: {msg.content}\n"
                else:
                    history_response += f"Dziecko: {msg.content}\n"
                logging.info(f"History: {msg.author.name}: {msg.content.strip()}")
            message.content = history_response + "\n" + original_message + ".\n" + boundary_conditions
            return message
        except Exception as e:
            logging.error(f"Error while adding history to message: {e}")
            return None


class OpenAIService(commands.Cog):
    def __init__(self, model_ai):
        self.model_ai = model_ai

    open_ai_token = os.getenv('open_ai_api_token')
    ai_behaviour = os.getenv('ai_behavior')
    top_p = float(os.getenv('open_ai_top_p'))
    max_tokens = int(os.getenv('open_ai_max_tokens'))
    temperature = float(os.getenv('open_ai_temperature'))

    def gpt_35_turbo_instruct(self, message_to_ai):
        client = OpenAI(self.open_ai_token)
        response = client.completions.create(
            prompt=message_to_ai,
            model=self.model_ai,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        logging.info(f"Response from API OpenAI: {response}")
        logging.info(
            f"Costs: {response.usage.prompt_tokens}+{response.usage.completion_tokens}={response.usage.total_tokens}")
        return response.choices[0].text

    def gpt_35_turbo_0125(self, message, is_tools_enabled):
        openai.api_key = self.open_ai_token
        if is_tools_enabled is True:
            response = openai.chat.completions.create(
                messages=get_messages(self.ai_behaviour, message),
                model=self.model_ai,
                max_tokens=self.max_tokens,
                tools=get_tools(),
                tool_choice="auto",
            )
            logging.info(f"First response from API OpenAI: {response}")
            logging.info(
                f"Costs (first call): {response.usage.prompt_tokens}+{response.usage.completion_tokens}={response.usage.total_tokens}")
            available_tools = {
                'get_user_activity': ""
            }
            message_response = response.choices[0].message
            if message_response.tool_calls:
                messages = get_messages(self.ai_behaviour, message)
                messages.append(message_response)
                for tool_call in message_response.tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_tools[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    function_args["guild_context"] = message.guild
                    function_response = function_to_call(**function_args)
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                response = openai.chat.completions.create(
                    model=self.model_ai,
                    messages=messages,
                )
                logging.info(f"Second response from API OpenAI: {response}")
                logging.info(
                    f"Costs (second call): {response.usage.prompt_tokens}+{response.usage.completion_tokens}={response.usage.total_tokens}")
                return response.choices[0].message.content
        else:
            response = openai.chat.completions.create(
                messages=get_messages(self.ai_behaviour, message),
                model=self.model_ai,
                max_tokens=self.max_tokens,
            )
            logging.info(f"Response from API OpenAI: {response}")
            logging.info(
                f"Costs (second call): {response.usage.prompt_tokens}+{response.usage.completion_tokens}={response.usage.total_tokens}")
            return response.choices[0].message.content

    async def chat_with_gpt(self, message):
        # Send a message to the ChatGPT API and get a response
        user_id_to_check = message.author.id
        guild_id = message.guild.id
        message_history_limit = os.getenv('message_history_limit')
        message_history_enabled = os.getenv('message_history_enabled')
        try:
            max_openai_length = 250
            if len(message.content.strip()) > max_openai_length:
                return None
            elif not can_user_send_message(user_id_to_check):
                logging.warning("Too many messages per second. Slow mode on.")
                return "Pisz wolniej dziecko, jestem już stary i wolno czytam. "
            elif not can_guild_send_message(guild_id):
                logging.warning("Maximum number of messages per guild was reached.")
                return "Musze już iść spać i dzisiaj nie bede w stanie przeczytać więcej Twoich wiaodmości. Prosze badz grzecznym dzieckiem!"

            response_from_ai = None
            # Add history to message
            if message_history_enabled:
                message_to_ai = await add_history_to_message(message, message_history_limit)
            else:
                message_to_ai = message

            # Call OpenAI API engine
            if GPT___TURBO_INSTRUCT in self.model_ai:
                response_from_ai = self.gpt_35_turbo_instruct(message_to_ai)
            elif GPT___TURBO_ in self.model_ai:
                response_from_ai = self.gpt_35_turbo_0125(message_to_ai, False)

            return response_from_ai
        except Exception as e:
            logging.error(f"Error during calling OpenAI API. e: {e.with_traceback(e.__traceback__)}")
