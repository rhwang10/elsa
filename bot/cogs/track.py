import asyncio
from discord.ext import commands

from bot.models.track import AsyncAudioSource, Track
from bot.models.voice_context import VoiceContext

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_contexts = {}

    def get_voice_context(self, ctx: commands.Context):
        voice_context = self.voice_contexts.get(ctx.guild.id)
        if not voice_context:
            voice_context = VoiceContext(self.bot, ctx)
            self.voice_contexts[ctx.guild.id] = voice_context

        return voice_context

    def cog_unload(self):
        for state in self.voice_contexts.values():
            self.bot.loop.create_task(state.stop())

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_context = self.get_voice_context(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('An error occurred: {}'.format(str(error)))


    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        dest = ctx.author.voice.channel

        if ctx.voice_context.voice:
            await ctx.voice_context.voice.move_to(dest)
            return

        ctx.voice_context.voice = await dest.connect()

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, url: str):
        if not ctx.voice_context.voice:
            await ctx.invoke(self._join)

        try:
            source = await AsyncAudioSource.create(url)
        except Exception as e:
            print("Error creating audio source", e)
        else:
            track = Track(source)

            await ctx.voice_context.tracks.put(track)
            await ctx.send(
                f"Enqueued {source}"
            )

    @commands.command(name='leave')
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_context.voice:
            return await ctx.send("Not connected to any channel")

        await ctx.voice_context.stop()
        del self.voice_contexts[ctx.guild.id]

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_context.is_playing and ctx.voice_context.voice.is_playing():
            ctx.voice_context.voice.pause()
            return await ctx.send("Paused!")

    @commands.command(name='resume')
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_context.is_playing and ctx.voice_context.voice.is_paused():
            ctx.voice_context.voice.resume()
            return await ctx.send("Resumed!!")

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):

        if not ctx.voice_context.is_playing:
            return await ctx.send("But there's no song playing!")

        ctx.voice_context.skip()

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        ctx.voice_context.tracks.clear()

        if not ctx.voice_context.is_playing:
            ctx.voice_context.voice.stop()

    @_join.before_invoke
    @_play.before_invoke
    async def validate_voice_context(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You aren't connected to a voice channel")

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("I'm already in a voice channel")
