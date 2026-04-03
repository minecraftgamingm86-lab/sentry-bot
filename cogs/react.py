# cogs/react.py
import discord
from discord.ext import commands

class React(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="react")
    @commands.has_permissions(manage_messages=True)
    async def react(self, ctx, emoji: str = None):
        """
        Usage:
        1. Reply to a message + +react <emoji>
        2. +react <message_id> <emoji>
        """
        target_message = None

        # Case 1: Reply to a message
        if ctx.message.reference and ctx.message.reference.message_id:
            try:
                target_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            except:
                await ctx.send("❌ Could not find the replied message.", delete_after=5)
                return

        # Case 2: Message ID provided
        elif emoji and emoji.isdigit():
            message_id = int(emoji)
            try:
                target_message = await ctx.channel.fetch_message(message_id)
                # Shift emoji to the second argument if provided
                if len(ctx.message.content.split()) > 2:
                    emoji = ctx.message.content.split()[2]
                else:
                    emoji = None
            except:
                await ctx.send("❌ Could not find message with that ID.", delete_after=5)
                return

        # Case 3: No valid input
        if not target_message:
            await ctx.send("❌ Please reply to a message or provide a message ID.\nUsage: `+react <emoji>` (reply) or `+react <message_id> <emoji>`", delete_after=10)
            return

        # If emoji was not provided properly, use the second argument
        if not emoji and len(ctx.message.content.split()) > 1:
            emoji = ctx.message.content.split()[1]

        if not emoji:
            await ctx.send("❌ Please provide an emoji to react with.", delete_after=5)
            return

        try:
            await target_message.add_reaction(emoji)
            await ctx.send(f"✅ Reacted with {emoji}", delete_after=5)

            # Delete the +react command message
            try:
                await ctx.message.delete()
            except:
                pass

        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to react: {e}", delete_after=8)


async def setup(bot):
    await bot.add_cog(React(bot))
