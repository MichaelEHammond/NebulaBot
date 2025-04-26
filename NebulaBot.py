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
    # Ensure bot can be activated via slash commands
    await bot.tree.sync()
    print(f"{bot.user} is online!")

# @bot.event
# async def on_message(msg):
#     # Check if messasge was sent by user
#     if msg.author.id != bot.user.id:
#         await msg.channel.send(f"Interesting message, {msg.author.mention}")

# @bot.tree.command(name="greet", description="Sends a greeting to the user")
# async def greet(interaction: discord.Interaction):
#     username = interaction.user.mention
#     await interaction.response.send_message(f"Hello there, {username}")

bot.run(TOKEN)