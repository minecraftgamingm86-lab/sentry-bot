# cogs/tickets.py
import discord
from discord.ext import commands
from discord.ui import View, Select, Button
from discord import SelectOption, Interaction, CategoryChannel
import json
import os

CONFIG_PATH = "/app/data/payment_methods.json"

def load_ticket_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_ticket_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ================================================
#  Persistent Ticket Creation Panel
# ================================================
class PersistentTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

        options = [
            SelectOption(label="Buy Accounts / Enquiries",        value="buy_accounts", emoji="<:coc:1462053918740844709>"),
            SelectOption(label="Walls Maxing / Farming",          value="walls_farming", emoji="<:walls:1462055575717150974>"),
            SelectOption(label="Capital Raids / Capital Golds",   value="capital_raids", emoji="<:clancapital:1461849162248224788>"),
            SelectOption(label="Showcase / CWL Base",             value="custom_base", emoji="<:builder:1462058517904101510>"),
            SelectOption(label="Gold / Event Pass Purchase",      value="gold_purchase", emoji="<:goldpass:1461847049250275570>"),
            SelectOption(label="Raffle Tickets",                  value="raffle", emoji="<:vticket:1472623749089071315>"),
        ]

        select = Select(
            placeholder="Select One",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="void_ticket_select"
        )
        select.callback = self.create_ticket
        self.add_item(select)

    async def create_ticket(self, interaction: Interaction):
        value = interaction.data["values"][0]

        guild = interaction.guild
        user = interaction.user

        config = load_ticket_config().get(str(guild.id), {})
        category_id = config.get("ticket_category_id")

        # Create ticket number
        existing = [ch for ch in guild.text_channels if ch.name.startswith("ticket-")]
        ticket_number = len(existing) + 1
        ticket_name = f"ticket-{ticket_number:05d}"

        # Get category if set
        category = None
        if category_id:
            category = guild.get_channel(category_id)
            if isinstance(category, CategoryChannel):
                # Category exists
                pass
            else:
                category = None  # invalid category

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, manage_channels=True),
        }

        if category:
            channel = await category.create_text_channel(
                name=ticket_name,
                topic=f"Ticket: {value.replace('_', ' ').title()} | Opened by {user}",
                overwrites=overwrites,
                reason=f"Ticket opened by {user}"
            )
        else:
            channel = await guild.create_text_channel(
                name=ticket_name,
                topic=f"Ticket: {value.replace('_', ' ').title()} | Opened by {user}",
                overwrites=overwrites,
                reason=f"Ticket opened by {user}"
            )

        # Welcome embed
        embed = discord.Embed(
            title=f"✦ VOID SUPPORT TERMINAL ✦ – {value.replace('_', ' ').title()}",
            description=f"{user.mention}, thank you for opening a ticket!\n\n**Please describe your issue in detail.**\nA staff member will assist you shortly.",
            color=0x71368A
        )
        embed.set_footer(text="VOID SPACE • Official Ticket System")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1461984553953657004/1472633716307263628/Add_a_heading.jpg?ex=69cbf906&is=69caa786&hm=6210b0c8bd0897abdce0bbb3fa4609c33d80d6effc6c2437622daf6401755ea5&")

        await channel.send(embed=embed, content=user.mention)

        # Close button
        close_view = CloseTicketView()
        await channel.send("**Click below to close this ticket**", view=close_view)

        await interaction.response.send_message(f"✅ Ticket created → {channel.mention}", ephemeral=True)


# ================================================
#  Close Ticket with Confirmation
# ================================================
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def ask_close(self, interaction: Interaction, button: Button):
        confirm_view = ConfirmCloseView(interaction.channel)
        await interaction.response.send_message("Are you sure you want to close this ticket?", view=confirm_view, ephemeral=True)


class ConfirmCloseView(View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=60)
        self.channel = channel

    @discord.ui.button(label="Yes, Close", style=discord.ButtonStyle.red)
    async def yes(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.channel.delete(reason=f"Ticket closed by {interaction.user}")
        except Exception as e:
            await interaction.followup.send(f"Failed to close: {e}", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: Interaction, button: Button):
        await interaction.response.send_message("Cancelled.", ephemeral=True, delete_after=5)
        self.stop()


# ================================================
#  Commands
# ================================================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketpanel")
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx):
        embed = discord.Embed(
            title="✦ VOID SUPPORT TERMINAL ✦",
            description="Use this ticket to purchase COC accounts\nor access VOID-approved services.",
            color=0x71368A
        )
        embed.set_footer(text="VOID SPACE OFFICIAL TICKET TOOL")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1461984553953657004/1472633716307263628/Add_a_heading.jpg?ex=69cbf906&is=69caa786&hm=6210b0c8bd0897abdce0bbb3fa4609c33d80d6effc6c2437622daf6401755ea5&")

        view = PersistentTicketView()
        await ctx.send(embed=embed, view=view)

    @commands.command(name="setticketcategory")
    @commands.has_permissions(administrator=True)
    async def setticketcategory(self, ctx, category: discord.CategoryChannel):
        """Set the category where new tickets will be created"""
        config = load_ticket_config()
        guild_id = str(ctx.guild.id)
        if guild_id not in config:
            config[guild_id] = {}
        config[guild_id]["ticket_category_id"] = category.id
        save_ticket_config(config)

        await ctx.send(f"✅ Ticket category set to **{category.name}**.\nNew tickets will now be created inside this category.")


async def setup(bot):
    await bot.add_cog(Tickets(bot))
