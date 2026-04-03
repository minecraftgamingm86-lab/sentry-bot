# cogs/moderation.py
import discord
from discord.ext import commands
from datetime import timedelta
import json
import os
from datetime import datetime

CONFIG_PATH = "/app/data/config.json"   # for welcome or tickets

def load_logs():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"ban": [], "kick": [], "warn": []}

def save_logs(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def log_action(self, action_type, member, staff, reason="No reason provided"):
        logs = load_logs()
        entry = {
            "user_id": str(member.id),
            "user_name": str(member),
            "staff_id": str(staff.id),
            "staff_name": str(staff),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        logs[action_type].append(entry)
        save_logs(logs)

    # ====================== BAN ======================
    @commands.command(name="ban", help="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot ban someone with equal or higher role.")

        self.log_action("ban", member, ctx.author, reason)

        try:
            await member.send(f"You have been **banned** from **{ctx.guild.name}**.\nReason: {reason}")
        except:
            pass

        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} has been banned.")

    # ====================== KICK ======================
    @commands.command(name="kick", help="Kick a member")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot kick someone with equal or higher role.")

        self.log_action("kick", member, ctx.author, reason)

        try:
            await member.send(f"You have been **kicked** from **{ctx.guild.name}**.\nReason: {reason}")
        except:
            pass

        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} has been kicked.")

    # ====================== TIMEOUT ======================
    @commands.command(name="timeout", help="Timeout a member")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot timeout someone with equal or higher role.")

        await member.timeout(timedelta(minutes=minutes), reason=reason)
        await ctx.send(f"✅ {member.mention} has been timed out for {minutes} minutes.")

    # ====================== UNTIMEOUT ======================
    @commands.command(name="untimeout", help="Remove timeout from a member")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"✅ {member.mention} is no longer timed out.")

    # ====================== PURGE ======================
    @commands.command(name="purge", help="Delete messages. +purge <amount>")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send("Amount must be between 1 and 100.")
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ Deleted {amount} messages.", delete_after=5)

    # ====================== WARN ======================
    @commands.command(name="warn", help="Warn a member")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        self.log_action("warn", member, ctx.author, reason)

        try:
            await member.send(f"You have been **warned** in **{ctx.guild.name}**.\nReason: {reason}")
        except:
            pass

        await ctx.send(f"✅ {member.mention} has been warned.")

    # ====================== UNWARN ======================
    @commands.command(name="unwarn", help="Remove the latest warning from a member")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, member: discord.Member):
        logs = load_logs()
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in logs and "warn" in logs[guild_id] and logs[guild_id]["warn"]:
            # Remove the latest warning
            removed = logs[guild_id]["warn"].pop()
            save_logs(logs)

            await ctx.send(f"✅ Removed 1 warning from {member.mention}.")
        else:
            await ctx.send(f"{member.mention} has no warnings to remove.")

    # ====================== UNBAN ======================
    @commands.command(name="unban", help="Unban a user by ID")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} has been unbanned.")
        except:
            await ctx.send("❌ Failed to unban. Make sure the ID is correct and the user is banned.")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
    print("Moderation cog loaded with unwarn system")
