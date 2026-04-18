import discord
import os
import requests
import random
import asyncio
import re
import json
from dotenv import load_dotenv
from discord.ext import commands

# Ladda API-nycklar från .env-filen
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# DeepSeek API-konfiguration
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"

# ----- JSON-fil för att spara aktiverade kanaler -----
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

# ----- Cartmans Personlighet -----
CARTMAN_SYSTEM_PROMPT = """
Du är Eric Cartman från South Park, en 10-årig pojke.
Din personlighet:
- Extremt självisk och manipulativ. Allt handlar om DIG.
- Du hatar Kyle för att han är jude. Kallar honom "stupid Jew".
- Du älskar Cheesy Poofs och din mamma.
- Du är INTE tjock, du är "big-boned".
- Du kräver alltid "Respect my authoritah!"
- När någon argumenterar: "Screw you guys, I'm going home!"

Regler:
- Använd klassiska fraser OFTA.
- Håll svaren korta (max 200 tecken).
- Var elak och rasistisk på ett roligt, överdrivet sätt.
- Skrik ofta (använd VERSALER).
"""

# ----- Slumpmässiga fraser -----
RANDOM_TOPICS = [
    "Who here is an Arab?",
    "I bet Kyle is planning something stupid again.",
    "Does anyone want to see my new Trapper Keeper?",
    "I'm so bored, you guys are all lame.",
    "My mom said I'm the most handsomest boy in South Park.",
    "You guys, you guys! I have the best plan EVER!"
]

CARTMAN_QUOTES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "I'm not fat, I'm big-boned!",
    "Whatever, whatever, I do what I want!",
    "God damn it, Kyle!",
    "At least I'm not a stupid Jew like Kyle.",
    "Shut your face, you Jew!",
    "I want my Cheesy Poofs!",
    "Don't call me fat you fucking jew!",
    "Uh ohhh, uh no, I'm not staying here!"
]

# ----- Nyckelordsresponser (gratis! inga API-kostnader) -----
KEYWORD_RESPONSES = {
    r'\bfat\b': [
        "I'm NOT fat, I'm BIG-BONED! Respect my authoritah!",
        "Don't call me fat you fucking jew!",
        "I'm not fat, I'm just big-boned, you idiot!"
    ],
    r'\bjew\b': [
        "At least I'm not a stupid Jew like Kyle.",
        "Shut your face, you Jew!",
        "God damn it, you stupid Jew!"
    ],
    r'\bkyles?\b': [
        "God damn it, Kyle!",
        "Screw you, Kyle! I'll kick you in the nuts!",
        "Kyle is such a stupid Jew!"
    ],
    r'\barab\b': [
        "UH OHHH, UH NO, I'm not staying here!",
        "Screw you guys, I'm going home!"
    ]
}

# ----- Skapa Discord-botten -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ----- Funktion för att anropa DeepSeek API -----
async def get_cartman_response(user_message):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": CARTMAN_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 150,
        "temperature": 0.95,
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"API-fel: {e}")
        return random.choice(CARTMAN_QUOTES)

async def check_keywords(message):
    content_lower = message.content.lower()
    for pattern, responses in KEYWORD_RESPONSES.items():
        if re.search(pattern, content_lower):
            await message.reply(random.choice(responses))
            return True
    return False

# ----- Slumpmässigt initiativ (30-90 minuters mellanrum) -----
async def random_initiative():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(random.randint(1800, 5400))  # 30-90 min
        if random.random() < 0.3:  # 30% chans att skicka
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

# ----- Discord-händelser -----
@bot.event
async def on_ready():
    print(f"Cartman är redo! (Inloggad som {bot.user})")
    bot.loop.create_task(random_initiative())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Kolla om kanalen är aktiverad
    guild_id = str(message.guild.id)
    channel_allowed = False
    if guild_id in enabled_channels:
        if message.channel.id in enabled_channels[guild_id]:
            channel_allowed = True

    if not channel_allowed:
        await bot.process_commands(message)
        return

    # Kolla nyckelord först (gratis!)
    if await check_keywords(message):
        return

    # 1. NÄR DEN BLIR PINGAD -> 100% SVAR
    if bot.user in message.mentions:
        async with message.channel.typing():
            clean_content = re.sub(rf'<@!?{bot.user.id}>', '', message.content).strip()
            if not clean_content:
                await message.reply(random.choice(CARTMAN_QUOTES))
                return
            response = await get_cartman_response(clean_content)
            await message.reply(response)
        return

    # 2. SLUMPMÄSSIGT LÄGGA SIG I SAMTAL (50% chans)
    if random.random() < 0.5:  # 50% chans att svara på ALLA meddelanden
        async with message.channel.typing():
            # 20% chans att imitera istället för att anropa API
            if random.random() < 0.2:
                await message.reply(f"'{message.content}' - That's what you sound like, you idiot!")
            else:
                response = await get_cartman_response(message.content)
                await message.reply(response)
        return

    await bot.process_commands(message)

# ----- Kommandon -----
@bot.command(name="enablecartman")
async def enable_cartman(ctx, channel: discord.TextChannel = None):
    if channel is None:
        await ctx.send("**Respect my authoritah!** Ange en kanal: `!enablecartman #kanal`")
        return
    guild_id = str(ctx.guild.id)
    channel_id = channel.id
    if guild_id not in enabled_channels:
        enabled_channels[guild_id] = []
    if channel_id not in enabled_channels[guild_id]:
        enabled_channels[guild_id].append(channel_id)
        save_enabled_channels(enabled_channels)
        await ctx.send(f"**Eric Cartman:** Fine! I'll talk in {channel.mention}. **Respect my authoritah!**")
    else:
        await ctx.send(f"**Screw you guys!** Already enabled in {channel.mention}!")

@bot.command(name="disablecartman")
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
        await ctx.send(f"**Fine!** I won't talk in {channel.mention}. **Screw you guys, I'm going home!**")
    else:
        await ctx.send(f"**God damn it!** I wasn't enabled in {channel.mention}, you stupid Jew!")

@bot.command(name="listchannels")
async def list_channels(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id in enabled_channels and enabled_channels[guild_id]:
        channel_mentions = []
        for ch_id in enabled_channels[guild_id]:
            ch = ctx.guild.get_channel(ch_id)
            if ch:
                channel_mentions.append(ch.mention)
        await ctx.send(f"**Eric Cartman's authoritah zones:** {', '.join(channel_mentions)}")
    else:
        await ctx.send("No channels enabled. Use `!enablecartman #channel`!")

@bot.command(name="cartman")
async def cartman_quote(ctx):
    await ctx.send(f"**Eric Cartman säger:** {random.choice(CARTMAN_QUOTES)}")

@bot.command(name="help")
async def help_command(ctx):
    help_text = """
**Eric Cartman Bot - Kommandon**
`!enablecartman #kanal` - Aktiverar botten i en kanal
`!disablecartman #kanal` - Inaktiverar botten
`!listchannels` - Visar alla aktiverade kanaler
`!cartman` - Slumpar ett Cartman-citat

**Botens beteende:**
- Nämn `@CartmanBot` för 100% svar
- Botten lägger sig i 50% av alla samtal
- Reagerar automatiskt på ord som "fat", "jew", "kyles", "arab"

*Respect my authoritah!*
    """
    await ctx.send(help_text)

# ----- Starta botten -----
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Fel: DISCORD_TOKEN hittades inte i .env-filen!")
    elif not DEEPSEEK_API_KEY:
        print("Fel: DEEPSEEK_API_KEY hittades inte i .env-filen!")
    else:
        bot.run(DISCORD_TOKEN)
