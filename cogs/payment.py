# cogs/payment.py
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json
import os

CONFIG_PATH = "data/payment_embed.json"

def load_payment_embed():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "title": "Payment & Purchase",
        "description": "Please send proof of payment or ask any questions related to payment.",
        "image": "",
        "footer": "VOID SPACE • Secure Payments"
    }

def save_payment_embed(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


class PaymentEditorView(View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.embed_data = load_payment_embed()

    def get_embed(self):
        embed = discord.Embed(
            title=self.embed_data.get("title", "Payment & Purchase"),
            description=self.embed_data.get("description", "Default description"),
            color=0x71368A
        )
        if self.embed_data.get("image"):
            embed.set_image(url=self.embed_data["image"])
        if self.embed_data.get("footer"):
            embed.set_footer(text=self.embed_data["footer"])
        return embed

    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.message.edit(embed=self.get_embed(), view=self)
            await interaction.followup.send("✅ Preview updated!", ephemeral=True, delete_after=4)
        except:
            await interaction.followup.send("Failed to update.", ephemeral=True)

    @discord.ui.button(label="Title", style=discord.ButtonStyle.secondary, emoji="✏️")
    async def edit_title(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(TitleModal(self))

    @discord.ui.button(label="Description", style=discord.ButtonStyle.secondary, emoji="📝")
    async def edit_desc(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(DescriptionModal(self))

    @discord.ui.button(label="Image", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def edit_image(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(ImageModal(self))

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.secondary, emoji="🔻")
    async def edit_footer(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(FooterModal(self))

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green, emoji="💾")
    async def save_embed(self, interaction: discord.Interaction, button):
        save_payment_embed(self.embed_data)
        await interaction.response.send_message("✅ Payment embed saved successfully!", ephemeral=True)


# Modals
class TitleModal(Modal, title="Edit Title"):
    text = TextInput(label="Title", max_length=256, required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.text.default = view.embed_data.get("title")
    async def on_submit(self, i: discord.Interaction):
        self.view.embed_data["title"] = self.text.value.strip() or "Payment & Purchase"
        await self.view.update(i)

class DescriptionModal(Modal, title="Edit Description"):
    text = TextInput(label="Description", style=discord.TextStyle.paragraph, max_length=2000, required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.text.default = view.embed_data.get("description")
    async def on_submit(self, i: discord.Interaction):
        self.view.embed_data["description"] = self.text.value.strip() or "Default description"
        await self.view.update(i)

class ImageModal(Modal, title="Set Image URL"):
    url = TextInput(label="Image URL", required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.url.default = view.embed_data.get("image")
    async def on_submit(self, i: discord.Interaction):
        u = self.url.value.strip()
        self.view.embed_data["image"] = u if u else ""
        await self.view.update(i)

class FooterModal(Modal, title="Edit Footer"):
    text = TextInput(label="Footer text", max_length=2048, required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.text.default = view.embed_data.get("footer")
    async def on_submit(self, i: discord.Interaction):
        self.view.embed_data["footer"] = self.text.value.strip() or ""
        await self.view.update(i)


class Payment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="paymentedit")
    @commands.has_permissions(manage_messages=True)
    async def paymentedit(self, ctx):
        view = PaymentEditorView(self.bot, ctx)
        embed = view.get_embed()
        await ctx.send("**Payment Embed Editor**\nEdit using buttons below and click Save when done.", embed=embed, view=view)

    @commands.command(name="payment")
    @commands.has_permissions(manage_messages=True)
    async def payment(self, ctx):
        data = load_payment_embed()
        embed = discord.Embed(
            title=data.get("title", "Payment & Purchase"),
            description=data.get("description", ""),
            color=0x71368A
        )
        if data.get("image"):
            embed.set_image(url=data.get("image"))
        if data.get("footer"):
            embed.set_footer(text=data.get("footer"))

        await ctx.send(embed=embed)
        # Delete the +payment command message
        try:
            await ctx.message.delete()
        except:
            pass


async def setup(bot):
    await bot.add_cog(Payment(bot))