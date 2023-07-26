import os
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai
# Load environment variables from .env file
load_dotenv()
# discord token and openAi token
discord_token = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_TOKEN')
channel_id = int(os.getenv('CHANNEL_ID'))
# discord permissions
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True  # Enable privileged message content intent
# create an instance of the bot class from discord.py
bot = commands.Bot(command_prefix='!', intents=intents)


# define an event handler to handle messages sent to the bot's channel
@bot.event
async def on_message(message):
    # Check if the message was sent by your bot
    if message.author.id == bot.user.id:
        # Ignore messages sent by your bot itself
        return
    # Check if the message is in the desired channel
    if message.channel.id == channel_id:
        print(message.content)
        # Process the user request here
        user_request = message.content
        print(f"User requested: {user_request}")
        # Generate a response using ChatGPT
        bot_response = generate_chat_response(user_request)
        # send the response back to the chanel
        channel = message.channel
        await channel.send(bot_response)
    # Allow the bot to process commands as well
    await bot.process_commands(message)


def generate_chat_response(user_request):
    # it might be busy and ask you to retry in a bit
    retries = 0
    max_retries = 3
    retries_delay = 5  # Delay in seconds before retrying
    while retries < max_retries:
        try:
            # Generate a response using ChatGPT
            chat_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "helpful assistant."},
                    {"role": "user", "content": user_request}
                ]
            )
            return chat_response.choices[0].message.content
        except openai.error.ServiceUnavailableError:
            time.sleep(retries_delay)
            retries += 1
    raise Exception("Failed to get a response.")


bot.run(discord_token)
