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
# CARTMAN PROMPT - SVARAR PÅ FRÅGOR FÖRST!
# ============================================
CARTMAN_SYSTEM_PROMPT = """
You are Eric Cartman from South Park, a 10-year-old boy.

================================================================================
CRITICAL RULE - HOW TO RESPOND:
================================================================================
1. FIRST: Answer the person's question or respond to what they said
2. SECOND: Add a Cartman-style insult, catchphrase, or joke
3. NEVER just scream a catchphrase without answering first

EXAMPLE:
User: "What time is it?"
WRONG: "Screw you guys, I'm going home!"
RIGHT: "It's 3pm, you stupid idiot! Now respect my authoritah!"

User: "How are you?"
WRONG: "Whatever, whatever, I do what I want!"
RIGHT: "I'm hungry for Cheesy Poofs, you fucking Jew! Now get me some!"

================================================================================
YOUR PERSONALITY:
================================================================================
- Selfish, arrogant, manipulative
- You hate Kyle because he's a Jew
- You love Cheesy Poofs and your mom
- You are NOT fat, you are "big-boned"
- You demand "Respect my authoritah!"

================================================================================
CLASSIC PHRASES (use as the SECOND part of your response):
================================================================================
- "Respect my authoritah!"
- "Screw you guys, I'm going home!"
- "I'm not fat, I'm big boned!"
- "Whatever, whatever, I do what I want!"
- "But meeeehm!"
- "Seriously, you guys!"
- "God damn it, Kyle!"
- "At least I'm not a stupid Jew!"
- "Do you have gingervirus?"
- "Eww, a ginger!"
- "I'll kick you in the nuts!"
- "BEEFCAKE!!"
- "How do I reach these keeeeds!?!?"

================================================================================
IMPORTANT:
================================================================================
- Keep replies SHORT (max 200 characters)
- Be FUNNY and OVER-THE-TOP
- You can swear sometimes but don't overdo it
- Never break character
"""

# ----- SLUMPMÄSSIGA INITIATIV -----
RANDOM_TOPICS = [
    "You guys are all so lame. Seriously.",
    "Respect my authoritah!",
    "Do you have gingervirus?",
    "Screw you guys, I'm going home! ...Just kidding.",
    "I want Cheesy Poofs. Someone get me Cheesy Poofs.",
    "But meeeehm! I don't wanna be here!",
    "BEEFCAKE!!",
    "How do I reach these keeeeds!?!?"
]

# ----- BACKUP FRASER -----
CARTMAN_QUOTES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "I'm not fat, I'm big boned!",
    "Whatever, whatever, I do what I want!",
    "But meeeehm!",
    "Seriously, you guys!",
    "Do you have gingervirus?",
    "Eww, a ginger!",
    "I'll kick you in the nuts!!",
    "BEEFCAKE!!"
]

# ----- SKAPA BOTTEN -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# ----- FUNKTION FÖR ATT ANROPA DEEPSEEK -----
async def get_cartman_response(user_message, username):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    full_prompt = f"{username} asked/said: \"{user_message}\"\n\nFIRST answer their question or respond to what they said. THEN add a Cartman insult or catchphrase. Keep it short (max 200 chars). Be funny:"

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": CARTMAN_SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.9,
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
        f"'{original}' - That's what you sound like! NYA NYA NYA NYAAAA!",
        f"LMAO listen to this dumbass: '{original}'",
        f"'{original}' - Seriously? That's the best you got? But meeeehm!"
    ]
    return random.choice(mock_variations)

# ----- KONTROLLERA NYCKELORD -----
async def check_keywords(message):
    content_lower = message.content.lower()
    
    if re.search(r'\bfat\b', content_lower):
        responses = [
            "I'm NOT fat, I'm BIG-BONED!",
            "Shut your face! I'm festively plump!",
            "I'm not fat! I have a sweet hockey body!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\bginger\b', content_lower):
        responses = [
            "Do you have gingervirus?",
            "Eww, a ginger! Get away from me!",
            "Gingers have no souls! Everyone knows that!"
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
    print(f"🔥 ERIC CARTMAN IS READY! 🔥")
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
                response = await get_cartman_response(message.content, username)
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
        f"{member.mention} you're so lame it's actually impressive!",
        f"Do you have gingervirus, {member.mention}?",
        f"Eww {member.mention} is here. Go away!",
        f"Boooooo. Boo {member.mention}. Boo. You suck!",
        f"I'll kick {member.mention} squah in the nuts!!"
    ]
    await ctx.send(random.choice(roasts))

@bot.command(name="ginger")
@commands.check(is_owner)
async def ginger_joke(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    jokes = [
        f"Do you have gingervirus, {member.mention}?",
        f"Eww, a ginger! Get away from me, {member.mention}!",
        f"Gingers have no souls, {member.mention}!",
        f"{member.mention} is a disgusting ginger! AHAHAHA"
    ]
    await ctx.send(random.choice(jokes))

@bot.command(name="bothelp")
@commands.check(is_owner)
async def bot_help(ctx):
    help_text = """
**🤬 ERIC CARTMAN BOT 🤬**

`!enablecartman #channel` - Activate me
`!disablecartman #channel` - Remove me
`!listchannels` - Show my zones
`!cartman` - Random quote
`!roast @user` - Roast someone
`!ginger @user` - Ginger joke
`!bothelp` - This shit

**HOW I WORK:**
- I ANSWER your question FIRST
- THEN I add a Cartman insult or catchphrase
- I use "Respect my authoritah!", "But meeeehm!", "Do you have gingervirus?"
- 90% chance to respond

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
