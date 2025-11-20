import os
import random
import discord
from discord.ext import commands

# -------- BASIC SETUP --------
intents = discord.Intents.default()
intents.message_content = True  # Needed so the bot can read commands

bot = commands.Bot(command_prefix="!", intents=intents)

# Store attendees per channel: {channel_id: set(user_ids)}
attendees = {}


def get_attendee_set(channel_id: int) -> set:
    """Get or create the attendee set for this channel."""
    if channel_id not in attendees:
        attendees[channel_id] = set()
    return attendees[channel_id]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Wheel bot is ready! 🎡")


# -------- TEST COMMAND --------
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("🏓 Pong! The bot is working.")


# -------- ATTENDEE COMMANDS --------

@bot.command(name="attadd")
@commands.has_permissions(administrator=True)
async def add_attendees(ctx, *members: discord.Member):
    if not members:
        await ctx.send("⚠️ You need to mention at least one player.\nExample: `!attadd @Player1 @Player2`")
        return

    channel_attendees = get_attendee_set(ctx.channel.id)
    added_names = []

    for member in members:
        if member.id not in channel_attendees:
            channel_attendees.add(member.id)
            added_names.append(member.display_name)

    if not added_names:
        await ctx.send("ℹ️ All those players are already in the list for this channel.")
    else:
        await ctx.send(f"✅ Added to attendee list: **{', '.join(added_names)}**")


@bot.command(name="attlist")
@commands.has_permissions(administrator=True)
async def list_attendees(ctx):
    channel_attendees = get_attendee_set(ctx.channel.id)

    if not channel_attendees:
        await ctx.send("📭 There are no attendees registered for this channel yet.")
        return

    mentions = []
    for user_id in channel_attendees:
        member = ctx.guild.get_member(user_id)
        if member:
            mentions.append(member.mention)
        else:
            mentions.append(f"<@{user_id}>")

    await ctx.send(
        f"🧾 **Current attendees for this channel ({len(mentions)}):**\n" +
        ", ".join(mentions)
    )


@bot.command(name="attclear")
@commands.has_permissions(administrator=True)
async def clear_attendees(ctx):
    channel_attendees = get_attendee_set(ctx.channel.id)
    count = len(channel_attendees)
    channel_attendees.clear()

    await ctx.send(f"🧹 Cleared **{count}** attendees for this channel.")


@bot.command(name="spin")
@commands.has_permissions(administrator=True)
async def spin_wheel(ctx):
    channel_attendees = get_attendee_set(ctx.channel.id)

    if not channel_attendees:
        await ctx.send("❌ There are no attendees yet. Add some with `!attadd @Player1 @Player2`.")
        return

    winner_id = random.choice(list(channel_attendees))
    winner = ctx.guild.get_member(winner_id)

    embed = discord.Embed(
        title="🎡 Wheel of Fate — Result!",
        description="The wheel has spun...",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="🏆 Winner",
        value=winner.mention if winner else f"<@{winner_id}>",
        inline=False
    )

    embed.add_field(
        name="👥 Total Attendees",
        value=str(len(channel_attendees)),
        inline=True
    )

    embed.set_footer(text="Use !spin again to roll for another drop, or !attclear to reset.")

    await ctx.send(embed=embed)


# -------- RUN THE BOT (TOKEN FROM ENV VAR) --------

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    bot.run(TOKEN)
