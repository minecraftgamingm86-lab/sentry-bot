# main.py
import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("ERROR: BOT_TOKEN not found in .env file!")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="+",
    intents=intents,
    help_command=None,
    case_insensitive=True
)

@bot.event
async def on_ready():
    print("═" * 60)
    print(f"Bot is online!     •   {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Logged in as       •   {bot.user}")
    print(f"Prefix             •   +")
    print(f"Servers            •   {len(bot.guilds)}")
    print("═" * 60)

    # Register persistent views (Ticket + Close button)
    try:
        from cogs.tickets import PersistentTicketView, CloseTicketView
        bot.add_view(PersistentTicketView())
        bot.add_view(CloseTicketView())
        print("✅ Ticket system ready")
    except:
        print("Ticket views skipped")

    # Load all cogs silently (no spam)
    print("Loading cogs...")
    cog_folder = "cogs"
    loaded = 0

    if os.path.exists(cog_folder):
        for filename in os.listdir(cog_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await bot.load_extension(cog_name)
                    loaded += 1
                except:
                    pass  # silent fail

    print(f"✅ Bot fully ready! ({loaded} cogs loaded)")
    print("═" * 60)


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())