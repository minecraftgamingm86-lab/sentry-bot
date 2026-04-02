# cogs/welcome.py
import discord
from discord.ext import commands
from discord.ui import Button, View

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        # Your welcome channel
        welcome_channel_id = 1461276851304398880
        channel = member.guild.get_channel(welcome_channel_id)
        if not channel:
            return

        # Text outside the embed
        outside_text = f"Welcome {member.mention}!"

        # Embed
        embed = discord.Embed(
            title="You've entered the **VOID SPACE!**",
            description="Use the buttons below to check out our server rules and all the essentials you need to get started.",
            color=0x71368A  # Dark Purple
        )

        # Your custom image
        embed.set_image(url="https://cdn.discordapp.com/attachments/1461276954383749155/1489193132972183592/PicsArt_04-02-01.13.26.png?ex=69cf86ae&is=69ce352e&hm=8e85544db8373cabe3c09326b1dd6dcdefb69480275baae81543d86ca6365f23&")

        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.timestamp = discord.utils.utcnow()

        # Buttons with direct channel links
        view = WelcomeButtons()

        try:
            await channel.send(content=outside_text, embed=embed, view=view)
        except:
            pass


class WelcomeButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Rules", style=discord.ButtonStyle.secondary, emoji="📜")
    async def rules_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "📜 **Rules Channel:** https://discord.com/channels/1461274966212214902/1461276954383749152",
            ephemeral=True
        )

    @discord.ui.button(label="About VOID", style=discord.ButtonStyle.secondary, emoji="ℹ️")
    async def about_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "ℹ️ **About VOID Channel:** https://discord.com/channels/1461274966212214902/1461278282933731328",
            ephemeral=True
        )

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.secondary, emoji="🎟️")
    async def ticket_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "🎟️ **Open a Ticket Channel:** https://discord.com/channels/1461274966212214902/1461291659017850985",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Welcome(bot))
    print("Welcome message with buttons loaded")
