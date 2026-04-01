# cogs/help.py
import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="✦ VOID SPACE BOT HELP ✦",
            description="Here are all available commands:",
            color=0x71368A
        )

        # Group commands by cog
        for cog_name, cog in self.bot.cogs.items():
            commands_list = []
            
            for command in cog.get_commands():
                # Skip hidden commands if any
                if command.hidden:
                    continue
                    
                desc = command.help or "No description available."
                commands_list.append(f"`+{command.name}` — {desc}")

            if commands_list:
                cog_title = cog_name.replace("Cog", "").replace("Commands", "").strip()
                embed.add_field(
                    name=f"**{cog_title}**",
                    value="\n".join(commands_list),
                    inline=False
                )

        embed.set_footer(text=f"Total commands: {len(self.bot.commands)} | Prefix: +")
        
        await ctx.send(embed=embed)

    # Optional: Add descriptions to your other commands for better help
    # Example in tickets.py:
    # @commands.command(name="ticketpanel", help="Send the ticket creation panel")
    # @commands.command(name="setticketcategory", help="Set the category for new tickets")

    # Same for welcome:
    # @commands.command(name="setupwelcome", help="Setup custom welcome message")


async def setup(bot):
    await bot.add_cog(Help(bot))