# cogs/modlogs.py
import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from datetime import datetime

CONFIG_PATH = "data/modlogs.json"

def load_logs():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"ban": [], "kick": [], "warn": []}


class PaginatorView(View):
    def __init__(self, embeds):
        super().__init__(timeout=180)
        self.embeds = embeds
        self.current = 0

    async def update(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.current > 0:
            self.current -= 1
            await self.update(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: Button):
        if self.current < len(self.embeds) - 1:
            self.current += 1
            await self.update(interaction)


class ModLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_embeds(self, log_type, title):
        logs = load_logs().get(log_type, [])
        if not logs:
            embed = discord.Embed(title=title, description="No records found.", color=0x71368A)
            return [embed]

        embeds = []
        per_page = 8
        for i in range(0, len(logs), per_page):
            page_logs = logs[i:i+per_page]
            embed = discord.Embed(title=title, color=0x71368A)
            embed.set_footer(text=f"Page {i//per_page + 1} of {(len(logs)-1)//per_page + 1}")

            for log in page_logs:
                time = datetime.fromisoformat(log["timestamp"]).strftime("%d %b %Y %H:%M")
                embed.add_field(
                    name=f"{log['user_name']} • {time}",
                    value=f"**Staff:** {log['staff_name']}\n**Reason:** {log['reason']}",
                    inline=False
                )
            embeds.append(embed)
        return embeds

    @commands.command(name="banlist")
    @commands.has_permissions(manage_messages=True)
    async def banlist(self, ctx):
        embeds = self.create_embeds("ban", "Ban List")
        view = PaginatorView(embeds)
        await ctx.send(embed=embeds[0], view=view)

    @commands.command(name="kicklist")
    @commands.has_permissions(manage_messages=True)
    async def kicklist(self, ctx):
        embeds = self.create_embeds("kick", "Kick List")
        view = PaginatorView(embeds)
        await ctx.send(embed=embeds[0], view=view)

    @commands.command(name="warnlist")
    @commands.has_permissions(manage_messages=True)
    async def warnlist(self, ctx):
        embeds = self.create_embeds("warn", "Warning List")
        view = PaginatorView(embeds)
        await ctx.send(embed=embeds[0], view=view)

    @commands.command(name="everylist")
    @commands.has_permissions(manage_messages=True)
    async def everylist(self, ctx):
        logs = load_logs()
        all_logs = []
        for action_type, entries in logs.items():
            for entry in entries:
                entry["type"] = action_type.upper()
                all_logs.append(entry)

        if not all_logs:
            return await ctx.send("No moderation logs found.")

        embeds = []
        per_page = 8
        for i in range(0, len(all_logs), per_page):
            page = all_logs[i:i+per_page]
            embed = discord.Embed(title="All Moderation Logs", color=0x71368A)
            embed.set_footer(text=f"Page {i//per_page + 1} of {(len(all_logs)-1)//per_page + 1}")

            for entry in page:
                embed.add_field(
                    name=f"{entry['type']} • {entry['user_name']}",
                    value=f"**Staff:** {entry['staff_name']}\n**Reason:** {entry['reason']}",
                    inline=False
                )
            embeds.append(embed)

        view = PaginatorView(embeds)
        await ctx.send(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(ModLogs(bot))
    print("ModLogs cog loaded with pagination")
