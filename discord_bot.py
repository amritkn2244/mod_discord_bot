import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import openai

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if TOKEN is None:
    raise ValueError("Bot token not found! Check your .env file.")
if OPENAI_API_KEY is None:
    raise ValueError("OpenAI API key not found! Check your .env file.")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  

    if bot.user.mentioned_in(message) or (message.reference and message.reference.resolved and message.reference.resolved.author == bot.user):
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        if not prompt:  
            await message.channel.send("Hello! How can I assist you?")
            return

        response = chat_with_gpt(prompt)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def hi(ctx):
    await ctx.send("hello!")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role is None:
        await ctx.send("Muted role not found. Please create a 'Muted' role first.")
        return
    await member.add_roles(mute_role, reason=reason)
    await ctx.send(f'Muted {member.mention}')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role is None:
        await ctx.send("Muted role not found. Please create a 'Muted' role first.")
        return
    await member.remove_roles(mute_role)
    await ctx.send(f'Unmuted {member.mention}')

@bot.command()
async def userinfo(ctx, member: discord.Member):
    join_date = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
    roles = [role.name for role in member.roles if role.name != "@everyone"]
    await ctx.send(f'User: {member.name}\nJoined: {join_date}\nRoles: {", ".join(roles)}')

@bot.command()
async def help(ctx):
    help = (
        "$kick @user [reason] - Kick a user from the server.\n"
        "$ban @user [reason] - Ban a user from the server.\n"
        "$ping - Check if the bot is responsive.\n"
        "$hi - Says Hello back.\n"
        "$userinfo @user - Get information about a user.\n"
        "$mute @user - Mute a user.\n"
        "$unmute @user - Unmute a user.\n"
        "$help - Show this help message."
    )
    await ctx.send(help)

#chatgpt integration
def chat_with_gpt(prompt):
    try:
        if not openai.api_key:
            return "Error: OpenAI API key is missing!"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                      {"role": "user", "content": prompt}]
        )

        if not response.get("choices"):
            return "Error: No response from OpenAI."

        return response["choices"][0].get("message", {}).get("content", "Error: No valid response from OpenAI.")
    
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "I'm having trouble responding right now. Please try again later!"

bot.run(TOKEN)
