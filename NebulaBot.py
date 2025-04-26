import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load Bot token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Create intents object and set intents permissions
intents = discord.Intents.default()
intents.message_content = True

# Create bot object
bot = commands.Bot(command_prefix="!", intents=intents)

# Event runs when bot comes online
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")


@bot.event
async def on_message(msg):
    if msg.author.id != bot.user.id:
        await msg.channel.send(f"Interesting message, {msg.author.mention}")

bot.run(TOKEN)