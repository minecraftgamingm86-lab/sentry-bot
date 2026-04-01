# cogs/vouch.py
import discord
from discord.ext import commands
import re

# ================== SETTINGS ==================
VOUCH_CHANNEL_ID = 1461281231231782962   # Your vouch channel
REACTION_EMOJI = "❤️‍🔥"                    # Fire heart emoji
VOUCH_IMAGE_URL = "https://cdn.discordapp.com/attachments/1461276954383749155/1486509825000210625/IMG_0542.jpg?ex=69cd03e8&is=69cbb268&hm=2a87c7c81a6288ce6bea1b34e8066ad1f2a0cda7d4372cfb11107bf70ad67830&"
# =============================================

class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Only work in the selected vouch channel
        if message.channel.id != VOUCH_CHANNEL_ID:
            return

        # Check if "+vouch" appears anywhere in the message
        if re.search(r'\+vouch', message.content, re.IGNORECASE):

            # Your custom message
            thank_you = f"Thank you {message.author.mention}! We value your Trust & Support in **VOID SPACE**."

            # Create embed with only image
            embed = discord.Embed(color=0x71368A)
            embed.set_image(url=VOUCH_IMAGE_URL)

            # Send the reply
            await message.channel.send(content=thank_you, embed=embed)

            # React with fire heart emoji on the ORIGINAL message
            try:
                await message.add_reaction("❤️‍🔥")
            except Exception as e:
                print(f"Failed to add reaction: {e}")

            # Optional: React on the bot's reply too
            try:
                reply_msg = await message.channel.history(limit=1).flatten()
                if reply_msg:
                    await reply_msg[0].add_reaction("❤️‍🔥")
            except:
                pass


async def setup(bot):
    await bot.add_cog(Vouch(bot))