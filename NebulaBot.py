import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import yt_dlp
import asyncio
from collections import deque

# Load Bot token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

SONG_QUEUE = {}

GUILD_ID = 1365762275163508907

# YDL Functions
async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))

def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Event runs when bot comes online
@bot.event
async def on_ready():
    test_guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=test_guild)
    await bot.tree.sync()  # sync globally too

    print(f"{bot.user} is online!")

@bot.tree.command(name="coinflip", description="Flips a coin")
async def coinflip(interaction: discord.Interaction):
    import random
    import asyncio

    # Send an initial response to acknowledge the interaction
    await interaction.response.defer()  # Defers the response to allow follow-up messages

    # Send the initial flipping message using followup
    flipping_message = await interaction.followup.send("Flipping the coin...", wait=True)

    # Animation frames
    frames = ["_", "/", "|", "\\"]
    for _ in range(4):
        for frame in frames:
            await asyncio.sleep(0.1)  # Wait 0.25 seconds between frames
            await flipping_message.edit(content=frame)

    # Final result
    result = random.choice(["Heads", "Tails"])
    await flipping_message.edit(content=result)


### Music Commands ###


@bot.tree.command(name="skip", description="Skips the current playing song")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        guild_id = str(interaction.guild_id)
        voice_client.stop()
        await interaction.response.send_message("Skipped the current song.")

        # Play the next song automatically
        if SONG_QUEUE.get(guild_id):
            await play_next_song(voice_client, guild_id, interaction.channel)
    else:
        await interaction.response.send_message("Not playing anything to skip.")


@bot.tree.command(name="pause", description="Pause the currently playing song.")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if voice_client is None:
        return await interaction.response.send_message("I'm not in a voice channel.")

    # Check if something is actually playing
    if not voice_client.is_playing():
        return await interaction.response.send_message("Nothing is currently playing.")
    
    # Pause the track
    voice_client.pause()
    await interaction.response.send_message("Playback paused!")


@bot.tree.command(name="resume", description="Resume the currently paused song.")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if voice_client is None:
        return await interaction.response.send_message("I'm not in a voice channel.")

    # Check if it's actually paused
    if not voice_client.is_paused():
        return await interaction.response.send_message("I’m not paused right now.")
    
    # Resume playback
    voice_client.resume()
    await interaction.response.send_message("Playback resumed!")


@bot.tree.command(name="stop", description="Stop playback and clear the queue.")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    voice_client = interaction.guild.voice_client

    # Check if the bot is in a voice channel
    if not voice_client or not voice_client.is_connected():
        await interaction.followup.send("I'm not connected to any voice channel.")
        return

    # Clear the guild's queue
    guild_id_str = str(interaction.guild_id)
    if guild_id_str in SONG_QUEUE:
        SONG_QUEUE[guild_id_str].clear()

    # If something is playing or paused, stop it
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    await interaction.followup.send("Stopped playback and disconnected!")

    # (Optional) Disconnect from the channel
    await voice_client.disconnect()


@bot.tree.command(name="play", description="Play a song or add it to the queue.")
@app_commands.describe(song_query="Search query")
async def play(interaction: discord.Interaction, song_query: str):
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel

    if voice_channel is None:
        await interaction.followup.send("You must be in a voice channel.")
        return

    voice_client = interaction.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect(self_deaf=True)
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    ydl_options = {
        "format": "bestaudio[abr<=96]/bestaudio",
        "noplaylist": True,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
    }

    query = "ytsearch1: " + song_query
    results = await search_ytdlp_async(query, ydl_options)
    tracks = results.get("entries", [])

    if tracks is None:
        await interaction.followup.send("No results found.")
        return

    first_track = tracks[0]
    audio_url = first_track["url"]
    title = first_track.get("title", "Untitled")

    guild_id = str(interaction.guild_id)
    if SONG_QUEUE.get(guild_id) is None:
        SONG_QUEUE[guild_id] = deque()

    SONG_QUEUE[guild_id].append((audio_url, title))

    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"Added to queue: **{title}**")
    else:
        #await interaction.followup.send(f"Now playing: **{title}**")
        await play_next_song(voice_client, guild_id, interaction.channel)


@bot.tree.command(name="playurl", description="Play a song directly from a YouTube URL.")
@app_commands.describe(youtube_url="The full YouTube URL of the video")
async def playurl(interaction: discord.Interaction, youtube_url: str):
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel

    if voice_channel is None:
        await interaction.followup.send("You must be in a voice channel.")
        return

    voice_client = interaction.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect(self_deaf=True)
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    ydl_options = {
        "format": "bestaudio[abr<=96]/bestaudio",
        "noplaylist": True,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
    }

    # Directly extract info from the provided URL
    results = await search_ytdlp_async(youtube_url, ydl_options)

    if results is None:
        await interaction.followup.send("Could not retrieve info for that URL.")
        return

    audio_url = results["url"]
    title = results.get("title", "Untitled")

    guild_id = str(interaction.guild_id)
    if SONG_QUEUE.get(guild_id) is None:
        SONG_QUEUE[guild_id] = deque()

    SONG_QUEUE[guild_id].append((audio_url, title))

    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"Added to queue: **{title}**")
    else:
        await play_next_song(voice_client, guild_id, interaction.channel)


async def play_next_song(voice_client, guild_id, channel):
    if SONG_QUEUE[guild_id]:
        audio_url, title = SONG_QUEUE[guild_id].popleft()
        
        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn -c:a libopus -b:a 96k",
        }
        
        source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable="bin\\ffmpeg\\ffmpeg.exe")

        def after_play(error):
            if error:
                print(f"Error playing audio: {error}")
            # Schedule next song after current one finishes
            fut = asyncio.run_coroutine_threadsafe(play_next_song(voice_client, guild_id, channel), bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error running next song: {e}")

        voice_client.play(source, after=after_play)
        asyncio.create_task(channel.send(f"Now playing: **{title}**"))
    else:
        await voice_client.disconnect()
        SONG_QUEUE[guild_id] = deque()



@bot.event
async def on_message(message):
    print(message.guild.id)

bot.run(TOKEN)