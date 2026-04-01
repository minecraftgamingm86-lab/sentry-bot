# cogs/embed_builder.py
import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput, ChannelSelect
from discord import TextChannel, Interaction
import asyncio

class EmbedBuilderView(View):
    def __init__(self, message: discord.Message, embed: discord.Embed):
        super().__init__(timeout=None)
        self.message = message
        self.embed = embed
        self.last_edit = 0.0

    async def update(self, interaction: Interaction):
        now = asyncio.get_event_loop().time()
        if now - self.last_edit < 1.3:  # simple rate limit protection
            await interaction.followup.send("Please wait a moment before next edit.", ephemeral=True)
            return

        self.last_edit = now

        try:
            await interaction.response.defer(ephemeral=True)
            await self.message.edit(embed=self.embed, view=self)
            await interaction.followup.send("Embed updated ✓", ephemeral=True, delete_after=4)
        except discord.Forbidden:
            await interaction.followup.send("Bot lacks permission to edit message.", ephemeral=True)
        except discord.HTTPException as e:
            if e.code == 50027 or "rate limit" in str(e).lower():
                await interaction.followup.send("Rate limited – wait 3 seconds and try again.", ephemeral=True)
            else:
                await interaction.followup.send(f"Failed to update embed: {e}", ephemeral=True)


    # ─── Buttons ───────────────────────────────────────────────────────────────

    @discord.ui.button(label="Title", style=discord.ButtonStyle.grey, emoji="✏️")
    async def edit_title(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(TitleModal(self))

    @discord.ui.button(label="Description", style=discord.ButtonStyle.grey, emoji="📝")
    async def edit_desc(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(DescriptionModal(self))

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.grey, emoji="🔽")
    async def edit_footer(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(FooterModal(self))

    @discord.ui.button(label="Color", style=discord.ButtonStyle.grey, emoji="🎨")
    async def edit_color(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(ColorModal(self))

    @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.grey, emoji="🖼️")
    async def set_thumbnail(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(ThumbnailModal(self))

    @discord.ui.button(label="Image", style=discord.ButtonStyle.grey, emoji="🖼️")
    async def set_image(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(ImageModal(self))

    @discord.ui.button(label="Send", style=discord.ButtonStyle.green, emoji="📤")
    async def send_final(self, interaction: Interaction, button: Button):
        select = ChannelSelect(
            placeholder="Select where to send...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text, discord.ChannelType.news]
        )

        async def callback(inter: Interaction):
            await inter.response.defer(ephemeral=True)
            channel = inter.guild.get_channel(int(inter.data["values"][0]))
            if not channel:
                await inter.followup.send("Channel not found.", ephemeral=True)
                return
            try:
                await channel.send(embed=self.embed)
                await inter.followup.send(f"Embed sent to {channel.mention}", ephemeral=True)
            except discord.Forbidden:
                await inter.followup.send("Missing send permissions in that channel.", ephemeral=True)
            except Exception as e:
                await inter.followup.send(f"Send failed: {e}", ephemeral=True)

        select.callback = callback
        view = View()
        view.add_item(select)


        await interaction.response.send_message("Choose destination channel:", view=view, ephemeral=True)

# ─── Modals ──────────────────────────────────────────────────────────────────

class TitleModal(Modal, title="Edit Title"):
    value = TextInput(label="Title", max_length=256, required=False)

    def __init__(self, view: EmbedBuilderView):
        super().__init__()
        self.view = view
        self.value.default = view.embed.title

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.title = self.value.value.strip() or None

        await interaction.response.defer(ephemeral=True)

        try:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
            await interaction.followup.send("Title updated!", ephemeral=True, delete_after=3)
        except discord.Forbidden:
            await interaction.followup.send("Bot missing 'Manage Messages' or role position issue.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"Edit failed (rate limit?): {e}", ephemeral=True)


class DescriptionModal(Modal, title="Edit Description"):
    value = TextInput(label="Description", style=discord.TextStyle.paragraph, max_length=4000, required=False)

    def __init__(self, view: EmbedBuilderView):
        super().__init__()
        self.view = view
        self.value.default = view.embed.description

    async def on_submit(self, interaction: Interaction):
        self.view.embed.description = self.value.value.strip() or None
        await self.view.update(interaction)


class FooterModal(Modal, title="Edit Footer"):
    text = TextInput(label="Footer text", max_length=2048, required=False)
    icon = TextInput(label="Icon URL (optional)", required=False)

    def __init__(self, view: EmbedBuilderView):
        super().__init__()
        self.view = view
        if view.embed.footer:
            self.text.default = view.embed.footer.text
            self.icon.default = view.embed.footer.icon_url

    async def on_submit(self, interaction: Interaction):
        self.view.embed.set_footer(
            text=self.text.value.strip() or None,
            icon_url=self.icon.value.strip() or None
        )
        await self.view.update(interaction)


class ColorModal(Modal, title="Edit Color"):
    value = TextInput(label="Hex color", placeholder="#71368A", max_length=7, required=False)

    def __init__(self, view: EmbedBuilderView):
        super().__init__()
        self.view = view
        if view.embed.color:
            self.value.default = f"#{view.embed.color.value:06x}".upper()

    async def on_submit(self, interaction: Interaction):
        hex_str = self.value.value.strip().lstrip('#')
        if not hex_str:
            self.view.embed.color = None
        else:
            try:
                if len(hex_str) == 3:
                    hex_str = ''.join(c*2 for c in hex_str)
                self.view.embed.color = discord.Color(int(hex_str, 16))
            except ValueError:
                await interaction.followup.send("Invalid hex format (example: #71368A)", ephemeral=True)
                return
        await self.view.update(interaction)


class ThumbnailModal(Modal, title="Set Thumbnail"):
    url = TextInput(label="URL", placeholder="https://...", required=False)

    def __init__(self, view: EmbedBuilderView):
        super().__init__()
        self.view = view
        if view.embed.thumbnail:
            self.url.default = view.embed.thumbnail.url

    async def on_submit(self, interaction: Interaction):
        url = self.url.value.strip()
        self.view.embed.set_thumbnail(url=url or None)
        await self.view.update(interaction)


class ImageModal(Modal, title="Set Main Image"):
    url = TextInput(label="URL", placeholder="https://...", required=False)

    def __init__(self, view: EmbedBuilderView):
        super().__init__()
        self.view = view
        if view.embed.image:
            self.url.default = view.embed.image.url

    async def on_submit(self, interaction: Interaction):
        url = self.url.value.strip()
        self.view.embed.set_image(url=url or None)
        await self.view.update(interaction)

# ─── Command ─────────────────────────────────────────────────────────────────

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="embed")
    @commands.has_permissions(manage_messages=True)
    async def embed_builder(self, ctx):
        embed = discord.Embed(
            title="Example Title",
            description="Example description text.\nUse the buttons below to customize.",
            color=0x71368A  # dark purple
        )
        embed.set_footer(text="Footer text • Edit me")

        view = EmbedBuilderView(ctx.message, embed)

        await ctx.send(
            content="**Embed Builder**\nCustomize → then press **Send**",
            embed=embed,
            view=view
        )


async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))
