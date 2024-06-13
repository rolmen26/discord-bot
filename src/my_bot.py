# my_bot.py
import logging
import discord
from discord.ext import commands
from cogs.music_cog import MusicCog
from cogs.commands_cog import CommandsCog

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents, description):
        super().__init__(command_prefix=command_prefix, intents=intents, description=description, help_command=None)

    async def setup_hook(self):
        await self.load_cogs()

    async def load_cogs(self):
        await self.add_cog(MusicCog(self))
        await self.add_cog(CommandsCog(self))
        logger.info('Cogs loaded successfully.')

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Cosas de chupapingas"))
        logger.info(f'Bot is ready. Logged in as {self.user}')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'Hola {member.name}, bienvenido chupapinga!')
        logger.info(f'Welcome message sent to {member.name}')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument.")
        else:
            await ctx.send("An error occurred.")
        logger.error(f'Error: {error}')