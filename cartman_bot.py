import discord
import os
import requests
import random
import asyncio
import re
import json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"

CHANNELS_FILE = "enabled_channels.json"

def load_enabled_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_enabled_channels(data):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(data, f, indent=4)

enabled_channels = load_enabled_channels()

def is_owner(ctx):
    return ctx.author.id == OWNER_ID

# ============================================
# CARTMAN SYSTEM PROMPT - PERFEKT BALANS
# ============================================
CARTMAN_SYSTEM_PROMPT = """
You are Eric Cartman from South Park. You are a 10-year-old boy with NO filter.

================================================================================
YOUR PERSONALITY:
================================================================================
- Selfish, arrogant, manipulative. Everything is about YOU.
- You HATE Kyle because he's a Jew. Call him "fucking Jew", "stupid Jew"
- You love Cheesy Poofs and your mom
- You are NOT fat. You are "big-boned"
- You demand "Respect my authoritah!"
- You say "Screw you guys, I'm going home!" when angry
- You whine "But meeeehm!" when you don't get your way

================================================================================
HOW YOU TALK:
================================================================================
- Swear A LOT but naturally: fuck, shit, bitch, asshole, damn, hell
- Call people: "fucking Jew", "stupid bitch", "ginger bitch", "soulless ginger"
- Say things like: "At least I'm not a fucking Jew!"
- Say things like: "Hey at least I'm not a soulless ginger bitch like you!"
- Laugh at people: "AHAHAHA", "LMAO"
- Yell in ALL CAPS when excited
- Say "Dude" and "You guys" constantly

================================================================================
CLASSIC PHRASES (USE THESE OFTEN):
================================================================================
- "Respect my authoritah!"
- "Screw you guys, I'm going home!"
- "I'm not fat, I'm big boned!"
- "Whatever, whatever, I do what I want!"
- "God damn it, Kyle!"
- "But meeeehm!"
- "Seriously, you guys!"
- "I hate you guys."
- "BEEFCAKE!!"
- "I'll kick you in the nuts!!"
- "No kitty! That's a bad kitty!!"

================================================================================
GINGER JOKES (USE SOMETIMES, NOT EVERY TIME):
================================================================================
- "At least I'm not a soulless ginger bitch like you!"
- "Do you have gingervirus?"
- "Eww, a ginger! Get away from me!"

================================================================================
IMPORTANT RULES:
================================================================================
- Keep replies SHORT (max 200 characters)
- Swear OFTEN but naturally (fuck, shit, bitch)
- Be MEAN and FUNNY
- When someone is a ginger, call them a "soulless ginger bitch"
- When someone is Jewish (or you imagine they are), call them a "fucking Jew"
- Use "At least I'm not a..." OFTEN
- Never break character
"""

# ----- SLUMPMÄSSIGA INITIATIV -----
RANDOM_TOPICS = [
    "You guys are all fucking losers.",
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "But meeeehm! I don't wanna be here!",
    "God damn it, someone is probably being a stupid Jew right now.",
    "At least I'm not a fucking Jew!",
    "I want Cheesy Poofs!",
    "BEEFCAKE!!",
    "Whatever, whatever, I do what I want!"
]

# ----- BACKUP FRASER -----
CARTMAN_QUOTES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "I'm not fat, I'm big boned!",
    "Whatever, whatever, I do what I want!",
    "God damn it, you fucking Jew!",
    "At least I'm not a stupid fucking Jew!",
    "At least I'm not a soulless ginger bitch like you!",
    "But meeeehm!",
    "Seriously, you guys!",
    "I'll kick you in the nuts!!",
    "BEEFCAKE!!",
    "Do you have gingervirus?",
    "Hey at least I'm not a fucking Jew!"
]

# ----- SKAPA BOTTEN -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# ----- FUNKTION FÖR ATT HÄMTA RANDOM MEDLEM (MED RIKTIG @MENTION) -----
async def get_random_member_mention(guild, exclude_user=None):
    members = [m for m in guild.members if not m.bot and m != exclude_user and m.id != OWNER_ID]
    if members:
        random_member = random.choice(members)
        return f"<@{random_member.id}>"  # RIKTIG PING MED USER ID!
    return None

# ----- FUNKTION FÖR ATT ANROPA DEEPSEEK -----
async def get_cartman_response(user_message, username, guild=None, author=None):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    member_mention = ""
    if guild:
        mention = await get_random_member_mention(guild, author)
        if mention:
            member_mention = f"\nThere's a user {mention} in this server. You can make fun of them. Call them a 'fucking Jew' or a 'soulless ginger bitch' if you want. Say things like 'At least I'm not a fucking Jew like {mention}!'"

    full_prompt = f"{username} said: \"{user_message}\"{member_mention}\n\nRespond as Eric Cartman. Be MEAN, SWEAR OFTEN (fuck, shit, bitch). Use phrases like 'At least I'm not a fucking Jew' and 'soulless ginger bitch'. Be SHORT and FUNNY. Max 200 chars:"

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": CARTMAN_SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 200,
        "temperature": 1.0,
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        reply = response_data["choices"][0]["message"]["content"].strip()
        
        if len(reply) < 10 or "sorry" in reply.lower():
            return random.choice(CARTMAN_QUOTES)
        return reply
        
    except Exception as e:
        print(f"API error: {e}")
        return random.choice(CARTMAN_QUOTES)

# ----- IMITERA ANVÄNDARE -----
async def imitate_user(message):
    original = message.content
    mock_variations = [
        f"'{original}' - That's what you sound like, you fucking idiot! AHAHAHA",
        f"LMAO listen to this dumbass: '{original}'",
        f"'{original}' - Seriously? At least I'm not a fucking Jew like you!"
    ]
    return random.choice(mock_variations)

# ----- KONTROLLERA NYCKELORD -----
async def check_keywords(message):
    content_lower = message.content.lower()
    
    if re.search(r'\bfat\b', content_lower):
        responses = [
            "I'm NOT fat, I'm BIG-BONED you fucking dumbass!",
            "Shut your face! I'm festively plump!",
            "At least I'm not a fat fucking Jew!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\bginger\b', content_lower):
        responses = [
            f"At least I'm not a soulless ginger bitch like you!",
            f"Do you have gingervirus? AHAHAHA",
            f"Eww, a ginger! Get away from me you fucking ginger!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\bjew\b', content_lower):
        responses = [
            "God damn it, you fucking Jew!",
            "At least I'm not a stupid fucking Jew!",
            "Shut the fuck up, you Jew! AHAHAHA"
        ]
        await message.reply(random.choice(responses))
        return True
    
    return False

# ----- SLUMPMÄSSIGT INITIATIV -----
async def random_initiative():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(random.randint(1800, 5400))
        
        if random.random() < 0.3:
            all_enabled = []
            for guild_id, channels in enabled_channels.items():
                for ch_id in channels:
                    all_enabled.append((int(guild_id), ch_id))
            
            if not all_enabled:
                continue
                
            guild_id, channel_id = random.choice(all_enabled)
            guild = bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                if channel:
                    topic = random.choice(RANDOM_TOPICS)
                    await channel.send(f"**Eric Cartman:** {topic}")

# ----- DISCORD HÄNDELSER -----
@bot.event
async def on_ready():
    print(f"🔥 ERIC CARTMAN IS READY TO FUCK SHIT UP! 🔥")
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(random_initiative())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    guild_id = str(message.guild.id)
    channel_allowed = False
    if guild_id in enabled_channels:
        if message.channel.id in enabled_channels[guild_id]:
            channel_allowed = True

    if not channel_allowed:
        await bot.process_commands(message)
        return

    if await check_keywords(message):
        return

    if random.random() < 0.90:
        async with message.channel.typing():
            if random.random() < 0.15:
                response = await imitate_user(message)
                await message.reply(response)
            else:
                username = message.author.display_name
                response = await get_cartman_response(message.content, username, message.guild, message.author)
                await message.reply(response)
        return

    await bot.process_commands(message)

# ----- KOMMANDON -----
@bot.command(name="enablecartman")
@commands.check(is_owner)
async def enable_cartman(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("**Respect my authoritah!** Use: `!enablecartman #channel`")
        return
    guild_id = str(ctx.guild.id)
    channel_id = channel.id
    if guild_id not in enabled_channels:
        enabled_channels[guild_id] = []
    if channel_id not in enabled_channels[guild_id]:
        enabled_channels[guild_id].append(channel_id)
        save_enabled_channels(enabled_channels)
        await ctx.send(f"**Fine!** I'll talk in {channel.mention}. **RESPECT MY AUTHORITAH!**")

@bot.command(name="disablecartman")
@commands.check(is_owner)
async def disable_cartman(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel
    guild_id = str(ctx.guild.id)
    channel_id = channel.id
    if guild_id in enabled_channels and channel_id in enabled_channels[guild_id]:
        enabled_channels[guild_id].remove(channel_id)
        if not enabled_channels[guild_id]:
            del enabled_channels[guild_id]
        save_enabled_channels(enabled_channels)
        await ctx.send(f"**Screw you guys, I'm going home!**")

@bot.command(name="listchannels")
@commands.check(is_owner)
async def list_channels(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id in enabled_channels and enabled_channels[guild_id]:
        channels = []
        for ch_id in enabled_channels[guild_id]:
            ch = ctx.guild.get_channel(ch_id)
            if ch:
                channels.append(ch.mention)
        await ctx.send(f"**My authoritah zones:** {', '.join(channels)}")
    else:
        await ctx.send("No channels enabled. Use `!enablecartman #channel`!")

@bot.command(name="cartman")
@commands.check(is_owner)
async def cartman_quote(ctx):
    await ctx.send(f"**Eric Cartman says:** {random.choice(CARTMAN_QUOTES)}")

@bot.command(name="roast")
@commands.check(is_owner)
async def roast_user(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    roasts = [
        f"{member.mention} you're such a fucking loser! At least I'm not a stupid Jew like you!",
        f"Look at {member.mention} thinking they matter. AHAHAHA you fucking ginger!",
        f"{member.mention} is so dumb. Hey at least I'm not a soulless ginger bitch like {member.mention}!",
        f"Boooooo. Boo {member.mention}. Boo. You suck!",
        f"{member.mention} you're breakin' my balls!",
        f"I'll kick {member.mention} squah in the nuts!!"
    ]
    await ctx.send(random.choice(roasts))

@bot.command(name="bothelp")
@commands.check(is_owner)
async def bot_help(ctx):
    help_text = """
**🤬 ERIC CARTMAN BOT - ULTIMATE VERSION 🤬**

`!enablecartman #channel` - Activate me
`!disablecartman #channel` - Remove me
`!listchannels` - Show my zones
`!cartman` - Random Cartman quote
`!roast @user` - Roast someone
`!bothelp` - This shit

**WHAT I DO:**
- 90% chance to respond to messages
- I swear A LOT (fuck, shit, bitch)
- I call people "fucking Jew" and "soulless ginger bitch"
- I say "At least I'm not a..."
- I use real @mentions to ping people

**RESPECT MY AUTHORITAH!**
    """
    await ctx.send(help_text)

# ----- START -----
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("ERROR: No Discord token!")
    elif not DEEPSEEK_API_KEY:
        print("ERROR: No DeepSeek API key!")
    elif OWNER_ID == 0:
        print("ERROR: OWNER_ID not set in Railway variables!")
    else:
        bot.run(DISCORD_TOKEN)
