import discord
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is in {len(bot.guilds)} servers:\n")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id}) | Members: {guild.member_count}")
    await bot.close()

bot.run(os.getenv('DISCORD_TOKEN'))
