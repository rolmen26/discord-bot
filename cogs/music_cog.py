import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # All the music related stuff
        self.is_playing = False

        # 2D array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch5:{item}", download=False)['entries']
            except Exception as e:
                print(f"Error searching YouTube: {e}")
                return False

        results = [{'source': entry['url'], 'title': entry['title'], 'duration': entry['duration'], 'uploader': entry['uploader']} for entry in info]
        return results

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # Get the first URL
            m_url = self.music_queue[0][0]['source']
            print(f"Next URL to play: {m_url}")

            # Display next song information
            next_song = self.music_queue[0]
            embed = discord.Embed(
                title="Now Playing",
                description=f"**{next_song[0]['title']}** by {next_song[0]['uploader']}\nDuration: {next_song[0]['duration']} seconds",
                color=discord.Color.green()
            )
            self.bot.loop.create_task(self.music_queue[0][1].send(embed=embed))

            # Remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            print(f"URL to play: {m_url}")

            # Display current song information
            current_song = self.music_queue[0]
            embed = discord.Embed(
                title="Now Playing",
                description=f"**{current_song[0]['title']}** by {current_song[0]['uploader']}\nDuration: {current_song[0]['duration']} seconds",
                color=discord.Color.green()
            )
            await self.music_queue[0][1].send(embed=embed)

            # Try to connect to voice channel if not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # Remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", help="Plays a selected song from YouTube")
    async def p(self, ctx, *args):
        query = " ".join(args)
        results = self.search_yt(query)

        if not results:
            await ctx.send("No se pudieron encontrar canciones. Intenta con otra búsqueda.")
            return

        description = "\n".join([f"{i + 1}. **{result['title']}** by {result['uploader']} (Duration: {result['duration']} seconds)" for i, result in enumerate(results)])
        embed = discord.Embed(
            title="Resultados de la búsqueda",
            description=description,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Escribe el número de la canción que deseas reproducir.")

        await ctx.send(embed=embed)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit() and 1 <= int(msg.content) <= len(results)

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30)
            choice = int(msg.content) - 1
            song = results[choice]

            url = song['source']
            print(f"Playing URL: {url}")
            embed = discord.Embed(
                title=song['title'],
                url=url,
                description=f"Duration: {song['duration']} seconds\nUploader: {song['uploader']}",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Canción solicitada por: {}".format(ctx.author.name))
            await ctx.send(embed=embed)

            self.music_queue.append([song, ctx.author.voice.channel])

            if not self.is_playing:
                await self.play_music()

        except TimeoutError:
            await ctx.send("No se seleccionó ninguna canción a tiempo. Intenta de nuevo.")

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        if len(self.music_queue) == 0:
            await ctx.send("No music in queue")
        else:
            retval = ""
            for i in range(0, len(self.music_queue)):
                retval += f"{i + 1}. **{self.music_queue[i][0]['title']}** by {self.music_queue[i][0]['uploader']}\n"

            embed = discord.Embed(
                title='Music Queue',
                description=retval,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc is None or not self.vc.is_connected():
            await ctx.send("El bot no está conectado a un canal de voz.")
            return

        if self.vc.is_playing():
            self.vc.stop()
            await self.play_music()
        else:
            await ctx.send("El bot no está reproduciendo nada.")

    @commands.command(name='stop', help='Stops the music')
    async def stop(self, ctx):
        if self.is_playing:
            self.vc.stop()
            self.music_queue = []
            self.is_playing = False
        else:
            await ctx.send('El bot no está reproduciendo nada.')

    @commands.command(name='pause', help='Pauses the current song')
    async def pause(self, ctx):
        if self.is_playing:
            self.vc.pause()
        else:
            await ctx.send("El bot no está reproduciendo nada.")

    @commands.command(name='resume', help='Resumes the paused song')
    async def resume(self, ctx):
        if self.vc.is_paused():
            self.vc.resume()
        else:
            await ctx.send("No se estaba reproduciendo nada. Para reproducir algo usa $play")

    @commands.command(name='leave', help='Disconnects the bot from the voice channel')
    async def leave(self, ctx):
        if self.vc:
            await self.vc.disconnect()
            self.vc = None
        else:
            await ctx.send("El bot no está conectado a ningún canal.")
