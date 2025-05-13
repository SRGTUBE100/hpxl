import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='*', intents=intents)

# Temporary storage for OTPs
user_otps = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

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
                "> **Note:** Only genuine submissions will be processed."
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
    email = discord.ui.TextInput(label="Email Address", placeholder="e.g., example@email.com", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        otp = str(random.randint(100000, 999999))
        user_otps[interaction.user.id] = otp

        try:
            await interaction.user.send(
                f"Hello! 👋\nHere is your OTP to claim the Hypixel Rank: **{otp}**\n"
                "Please use the command below to confirm:\n\n"
                f"`*confirmotp {otp}`"
            )
            await interaction.response.send_message("✅ Your info was submitted! Check your DMs for the OTP.", ephemeral=True)
        except:
            await interaction.response.send_message("⚠️ I couldn't send you a DM! Please enable DMs from server members.", ephemeral=True)

@bot.command()
async def confirmotp(ctx, otp_input):
    actual_otp = user_otps.get(ctx.author.id)

    if actual_otp is None:
        await ctx.reply("❌ You haven't submitted a request yet. Use the panel first.")
    elif otp_input == actual_otp:
        await ctx.reply("🎉 OTP Verified! You'll receive your Hypixel Rank within 24 hours.")
        del user_otps[ctx.author.id]
    else:
        await ctx.reply("❌ Incorrect OTP. Please try again.")

# Run the bot
bot.run("YOUR_BOT_TOKEN")
