# main.py
import discord
from discord.ext import commands
import asyncio
import os

# No load_dotenv() needed on Railway
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("ERROR: BOT_TOKEN not found in environment variables!")
    print("Make sure you added BOT_TOKEN in Railway Variables tab.")
    exit(1)

print(f"Token loaded successfully (length: {len(TOKEN)})")

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

    # Register persistent views
    try:
        from cogs.tickets import PersistentTicketView, CloseTicketView
        bot.add_view(PersistentTicketView())
        bot.add_view(CloseTicketView())
        print("✅ Ticket views registered")
    except Exception as e:
        print(f"Ticket views registration failed: {e}")

    print("Loading cogs...")
    cog_folder = "cogs"
    loaded = 0

    if os.path.exists(cog_folder):
        for filename in os.listdir(cog_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await bot.load_extension(cog_name)
                    print(f"  Loaded → {cog_name}")
                    loaded += 1
                except Exception as e:
                    print(f"  FAILED → {cog_name}")
    else:
        print("❌ cogs folder not found!")

    print(f"✅ Bot ready! ({loaded} cogs loaded)")
    print("═" * 60)


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
