# cogs/say.py
import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
        """
        Usage: +say #channel Your message with emojis here
        Supports server emojis and bot's custom emojis
        Example: +say #general Hello <a:Coc:1488531237516611586> 
        """
        try:
            # The magic: just send the message as-is
            # Discord will automatically render <a:name:id> and <:name:id> correctly
            sent_msg = await channel.send(message)

            await ctx.send(f"✅ Message sent to {channel.mention}", delete_after=6)
            # Optional: delete the command message for clean look
            try:
                await ctx.message.delete()
            except:
                pass

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to send messages in that channel.")
        except Exception as e:
            await ctx.send(f"❌ Failed to send: {e}")

    # Bonus: +sayembed version (if you want)
    @commands.command(name="sayembed")
    @commands.has_permissions(manage_messages=True)
    async def sayembed(self, ctx, channel: discord.TextChannel, *, text: str):
        embed = discord.Embed(description=text, color=0x71368A)
        try:
            await channel.send(embed=embed)
            await ctx.send(f"✅ Embed sent to {channel.mention}", delete_after=6)
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send("❌ Missing permissions in that channel.")


async def setup(bot):
    await bot.add_cog(Say(bot))