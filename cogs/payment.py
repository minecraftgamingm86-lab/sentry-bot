# cogs/payment.py
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import json
import os

CONFIG_PATH = "/app/data/payment_methods.json"

def load_payment_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_payment_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


class PaymentEditorView(View):
    def __init__(self, bot, ctx, method_name: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.ctx = ctx
        self.method_name = method_name.lower()
        self.config = load_payment_config().get(self.method_name, {
            "title": f"{method_name} Payment Method",
            "description": "Please send payment to the details below.",
            "image": "",
            "footer": "VOID SPACE • Secure Payments"
        })

    def get_embed(self):
        embed = discord.Embed(
            title=self.config.get("title", f"{self.method_name.upper()} Payment"),
            description=self.config.get("description", "Default description"),
            color=0x71368A
        )
        if self.config.get("image"):
            embed.set_image(url=self.config.get("image"))
        if self.config.get("footer"):
            embed.set_footer(text=self.config.get("footer"))
        return embed

    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.message.edit(embed=self.get_embed(), view=self)
            await interaction.followup.send("✅ Preview updated!", ephemeral=True, delete_after=4)
        except:
            await interaction.followup.send("Failed to update preview.", ephemeral=True)

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
    async def save(self, interaction: discord.Interaction, button):
        config = load_payment_config()
        config[self.method_name] = self.config
        save_payment_config(config)
        await interaction.response.send_message(f"✅ {self.method_name.upper()} payment embed saved!", ephemeral=True)


# Modals (same as before)
class TitleModal(Modal, title="Edit Title"):
    text = TextInput(label="Title", max_length=256, required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.text.default = view.config.get("title")
    async def on_submit(self, i: discord.Interaction):
        self.view.config["title"] = self.text.value.strip() or "Payment Method"
        await self.view.update(i)

class DescriptionModal(Modal, title="Edit Description"):
    text = TextInput(label="Description", style=discord.TextStyle.paragraph, max_length=2000, required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.text.default = view.config.get("description")
    async def on_submit(self, i: discord.Interaction):
        self.view.config["description"] = self.text.value.strip() or "Please send payment."
        await self.view.update(i)

class ImageModal(Modal, title="Set Image URL"):
    url = TextInput(label="Image URL", required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.url.default = view.config.get("image")
    async def on_submit(self, i: discord.Interaction):
        u = self.url.value.strip()
        self.view.config["image"] = u if u else ""
        await self.view.update(i)

class FooterModal(Modal, title="Edit Footer"):
    text = TextInput(label="Footer text", max_length=2048, required=False)
    def __init__(self, view): 
        super().__init__()
        self.view = view
        self.text.default = view.config.get("footer")
    async def on_submit(self, i: discord.Interaction):
        self.view.config["footer"] = self.text.value.strip() or ""
        await self.view.update(i)


class Payment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_payment_embed(self, ctx, method: str):
        data = load_payment_config().get(method.lower(), {})
        if not data:
            await ctx.send(f"❌ No saved embed for **{method}** yet. Use `+{method.lower()}edit` to create one.")
            return

        embed = discord.Embed(
            title=data.get("title", f"{method.upper()} Payment"),
            description=data.get("description", ""),
            color=0x71368A
        )
        if data.get("image"):
            embed.set_image(url=data.get("image"))
        if data.get("footer"):
            embed.set_footer(text=data.get("footer"))

        await ctx.send(embed=embed)
        try:
            await ctx.message.delete()
        except:
            pass

    # Dynamic commands for each payment method
    @commands.command(name="wise")
    @commands.has_permissions(manage_messages=True)
    async def wise(self, ctx):
        await self.send_payment_embed(ctx, "wise")

    @commands.command(name="wiseedit")
    @commands.has_permissions(manage_messages=True)
    async def wiseedit(self, ctx):
        view = PaymentEditorView(self.bot, ctx, "wise")
        embed = view.get_embed()
        await ctx.send(f"**Wise Payment Editor**", embed=embed, view=view)

    @commands.command(name="paypal")
    @commands.has_permissions(manage_messages=True)
    async def paypal(self, ctx):
        await self.send_payment_embed(ctx, "paypal")

    @commands.command(name="paypaledit")
    @commands.has_permissions(manage_messages=True)
    async def paypaledit(self, ctx):
        view = PaymentEditorView(self.bot, ctx, "paypal")
        embed = view.get_embed()
        await ctx.send(f"**PayPal Payment Editor**", embed=embed, view=view)

    @commands.command(name="venmo")
    @commands.has_permissions(manage_messages=True)
    async def venmo(self, ctx):
        await self.send_payment_embed(ctx, "venmo")

    @commands.command(name="venmoedit")
    @commands.has_permissions(manage_messages=True)
    async def venmoedit(self, ctx):
        view = PaymentEditorView(self.bot, ctx, "venmo")
        embed = view.get_embed()
        await ctx.send(f"**Venmo Payment Editor**", embed=embed, view=view)

    @commands.command(name="cashapp")
    @commands.has_permissions(manage_messages=True)
    async def cashapp(self, ctx):
        await self.send_payment_embed(ctx, "cashapp")

    @commands.command(name="cashappedit")
    @commands.has_permissions(manage_messages=True)
    async def cashappedit(self, ctx):
        view = PaymentEditorView(self.bot, ctx, "cashapp")
        embed = view.get_embed()
        await ctx.send(f"**Cash App Payment Editor**", embed=embed, view=view)

    @commands.command(name="zelle")
    @commands.has_permissions(manage_messages=True)
    async def zelle(self, ctx):
        await self.send_payment_embed(ctx, "zelle")

    @commands.command(name="zelleedit")
    @commands.has_permissions(manage_messages=True)
    async def zelleedit(self, ctx):
        view = PaymentEditorView(self.bot, ctx, "zelle")
        embed = view.get_embed()
        await ctx.send(f"**Zelle Payment Editor**", embed=embed, view=view)

    @commands.command(name="crypto")
    @commands.has_permissions(manage_messages=True)
    async def crypto(self, ctx):
        await self.send_payment_embed(ctx, "crypto")

    @commands.command(name="cryptoedit")
    @commands.has_permissions(manage_messages=True)
    async def cryptoedit(self, ctx):
        view = PaymentEditorView(self.bot, ctx, "crypto")
        embed = view.get_embed()
        await ctx.send(f"**Crypto Payment Editor**", embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Payment(bot))
