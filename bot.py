
import os
import logging
import discord
from discord import app_commands
from discord.ext import commands

# إعداد التسجيل والأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SuperBot")

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN environment variable")

intents = discord.Intents.default()
intents.message_content = True

class SuperBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Slash commands synced")

bot = SuperBot()

@bot.event
async def on_ready():
    logger.info("Super Bot is online as %s", bot.user)

@bot.tree.command(name="ping", description="Check if Super Bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Pong! {round(bot.latency * 1000)} ms",
        ephemeral=True
    )

@bot.tree.command(name="clear", description="Delete messages")
@app_commands.describe(amount="Number of messages (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.checks.bot_has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(
        f"Deleted {len(deleted)} messages.",
        ephemeral=True
    )

@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.checks.bot_has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member.id == interaction.user.id:
        await interaction.response.send_message("You cannot kick yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("That member's role is too high for me to kick.", ephemeral=True)
        return
    await member.kick(reason=f"{reason} | Moderator: {interaction.user}")
    await interaction.response.send_message(f"Kicked {member.mention}. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.checks.bot_has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member.id == interaction.user.id:
        await interaction.response.send_message("You cannot ban yourself.", ephemeral=True)
        return
    if member.top_role >= interaction.guild.me.top_role:
        await interaction.response.send_message("That member's role is too high for me to ban.", ephemeral=True)
        return
    await member.ban(reason=f"{reason} | Moderator: {interaction.user}")
    await interaction.response.send_message(f"Banned {member.mention}. Reason: {reason}")

@bot.tree.command(name="say", description="Send a message as Super Bot")
@app_commands.checks.has_permissions(manage_guild=True)
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        message = "You don't have permission to use this command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        message = "I don't have the required permissions."
    else:
        logger.error("Command error: %s", error)
        message = "Something went wrong. Try again later."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)

bot.run(TOKEN)
