# cogs/welcome.py
import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        # === YOUR WELCOME CHANNEL ID ===
        welcome_channel_id = 1461276851304398880   # Change if needed

        channel = member.guild.get_channel(welcome_channel_id)
        if not channel:
            return

        # Text outside the embed
        outside_text = f"Welcome {member.mention}!"

        # Embed with your description
        embed = discord.Embed(
            description=(
                "**You've entered the VOID SPACE!**\n"
                "Please read the rules: https://discord.com/channels/1461274966212214902/1461276954383749152\n"
                "and respect the space!\n\n"
                "For any enquiries kindly https://discord.com/channels/1461274966212214902/1461291659017850985"
            ),
            color=0x71368A   # Dark Purple
        )

        # Your custom image
        embed.set_image(url="https://cdn.discordapp.com/attachments/1461984553953657004/1462199226107826368/PicsArt_01-18-01.35.41.png?ex=69cce765&is=69cb95e5&hm=1ccaf3902331353d3a4ed00402051d5496552a5cab6b9051b1db438681fa0962&")

        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.timestamp = discord.utils.utcnow()

        # Send message
        try:
            await channel.send(content=outside_text, embed=embed)
        except:
            pass  # silent fail


async def setup(bot):
    await bot.add_cog(Welcome(bot))
    print("Welcome message system loaded successfully")