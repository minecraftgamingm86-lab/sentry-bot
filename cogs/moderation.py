# cogs/moderation.py
import discord
from discord.ext import commands
from datetime import timedelta
import json
import os

CONFIG_PATH = "/app/data/payment_methods.json"

def load_warnings():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_warnings(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ====================== BAN ======================
    @commands.command(name="ban", help="Ban a member. +ban @user [reason]")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            return await ctx.send("You cannot ban yourself.")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot ban a member with equal or higher role.")

        try:
            await member.send(f"You have been banned from **{ctx.guild.name}**.\nReason: {reason}")
        except:
            pass  # DM failed

        await member.ban(reason=reason)

        embed = discord.Embed(title="Member Banned", color=0x71368A)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed)

    # ====================== KICK ======================
    @commands.command(name="kick", help="Kick a member. +kick @user [reason]")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            return await ctx.send("You cannot kick yourself.")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot kick a member with equal or higher role.")

        try:
            await member.send(f"You have been kicked from **{ctx.guild.name}**.\nReason: {reason}")
        except:
            pass

        await member.kick(reason=reason)

        embed = discord.Embed(title="Member Kicked", color=0x71368A)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed)

    # ====================== TIMEOUT ======================
    @commands.command(name="timeout", help="Timeout a member. +timeout @user <minutes> [reason]")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        if member == ctx.author:
            return await ctx.send("You cannot timeout yourself.")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot timeout a member with equal or higher role.")

        duration = timedelta(minutes=minutes)

        try:
            await member.send(f"You have been timed out in **{ctx.guild.name}** for {minutes} minutes.\nReason: {reason}")
        except:
            pass

        await member.timeout(duration, reason=reason)

        embed = discord.Embed(title="Member Timed Out", color=0x71368A)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Duration", value=f"{minutes} minutes", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        await ctx.send(embed=embed)

    # ====================== UNTIMEOUT ======================
    @commands.command(name="untimeout", help="Remove timeout from a member")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        await member.timeout(None)

        try:
            await member.send(f"Your timeout has been removed in **{ctx.guild.name}**.")
        except:
            pass

        embed = discord.Embed(title="Timeout Removed", color=0x71368A)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

    # ====================== PURGE ======================
    @commands.command(name="purge", help="Delete messages. +purge <amount>")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send("Amount must be between 1 and 100.")

        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ Deleted {len(deleted)-1} messages.", delete_after=5)

    # ====================== WARN ======================
    @commands.command(name="warn", help="Warn a member. +warn @user [reason]")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            return await ctx.send("You cannot warn yourself.")

        warnings = load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in warnings:
            warnings[guild_id] = {}
        if user_id not in warnings[guild_id]:
            warnings[guild_id][user_id] = []

        warnings[guild_id][user_id].append({
            "reason": reason,
            "moderator": str(ctx.author.id),
            "time": discord.utils.utcnow().isoformat()
        })

        save_warnings(warnings)

        warn_count = len(warnings[guild_id][user_id])

        try:
            await member.send(f"You have been warned in **{ctx.guild.name}**.\nReason: {reason}\nTotal warnings: {warn_count}/5")
        except:
            pass

        embed = discord.Embed(title="Member Warned", color=0x71368A)
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Warnings", value=f"{warn_count}/5", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"By {ctx.author}")
        await ctx.send(embed=embed)

        if warn_count >= 5:
            await ctx.send(f"⚠️ {member.mention} has reached 5 warnings!")

    # ====================== REMOVE WARN ======================
    @commands.command(name="removewarn", help="Remove a warning from a member. +removewarn @user")
    @commands.has_permissions(manage_messages=True)
    async def removewarn(self, ctx, member: discord.Member):
        warnings = load_warnings()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in warnings and user_id in warnings[guild_id] and warnings[guild_id][user_id]:
            warnings[guild_id][user_id].pop()
            save_warnings(warnings)
            await ctx.send(f"✅ Removed 1 warning from {member.mention}.")
        else:
            await ctx.send(f"{member.mention} has no warnings.")

    # ====================== UNBAN ======================
    @commands.command(name="unban", help="Unban a user by ID or mention. +unban <user_id>")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} has been unbanned.")
        except:
            await ctx.send("❌ Failed to unban. Make sure the ID is correct.")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
    print("Moderation cog loaded successfully")
