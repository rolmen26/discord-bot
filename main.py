# main.py
import os
import logging
from dotenv import load_dotenv
from src.my_bot import MyBot
import discord

# Load environment variables
load_dotenv()

if __name__ == "__main__":

    # Initialize intents
    intents = discord.Intents.default()
    intents.message_content = True

    # Create bot instance
    bot = MyBot(command_prefix='$', intents=intents, description='Un bot sencillo')
    
    # Run the bot
    bot.run(os.getenv('DISCORD_TOKEN'))
