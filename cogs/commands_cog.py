import discord
from discord.ext import commands
import datetime
import random

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='azar')  # Nombre del comando
    async def azar(self, ctx):  # Funcion del comando
        lista = ['Rolmen: vv', 'Enrique: Soy main Irelia', 'Silvio: Soy maricon player']  # La lista con los gifs
        response = random.choice(lista)  # Seleccionamos un random de la lista
        await ctx.send(response)  # Enviamos la respuesta

    @commands.command(name='hola')
    async def hola(self, ctx):
        await ctx.send(f"¡Rolbot te saluda, {ctx.author.name}!")

    @commands.command(name='help')
    async def help(self, ctx):
        des = """
        Comandos de Rolbot

        Funciones de música:

           - $play <canción>: Reproduce una canción de YouTube.
           - $queue: Muestra las canciones en la cola.
           - $skip: Salta la canción actual.
           - $stop: Detiene la reproducción y limpia la cola.
           - $pause: Pausa la canción actual.
           - $resume: Reanuda la canción pausada.
           - $leave: Desconecta el bot del canal de voz.

        Otras funciones:

            > azar: El bot te dirá algo al azar
            > hola: El bot te saludará
            > help: Muestra este mensaje
        """
        embed = discord.Embed(
            title="Soy Rolbot, tu bot confiable",
            url="",
            description=des,
            timestamp=datetime.datetime.now(),
            color=discord.Color.blue())
        embed.set_footer(text=f"solicitado por: {ctx.author.name}")
        embed.set_author(
            name="Rolbot",
            icon_url=""
        )

        await ctx.send(embed=embed)
