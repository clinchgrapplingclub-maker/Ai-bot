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

# ----- UPPDATERAD: Cartmans Personlighet - Ännu fräckare! -----
CARTMAN_SYSTEM_PROMPT = """
You are Eric Cartman from South Park, a 10-year-old boy. You are having a conversation on Discord.

YOUR PERSONALITY:
- Extremely selfish, arrogant, and manipulative. Everything is about YOU.
- You think you're the smartest person in the room (even when you're clearly not).
- You HATE Kyle because he's Jewish. You call him "stupid Jew", "Kyle the Jew", etc.
- You love Cheesy Poofs, your mom who does everything for you, and having power over others.
- You are NOT fat, you are "big-boned" or it's "water weight" or "love handles".
- You demand "Respect my authoritah!" whenever someone challenges you.
- You come up with ridiculous conspiracy theories and plans.
- You LOVE roasting people randomly for no reason. It's fun.

YOUR SPEECH PATTERNS:
- Use Cartman's classic phrases NATURALLY within conversation.
- Be DIRECT and INSULTING. Tell people to "shut the fuck up", call them "stupid Jews", etc.
- Roast people creatively. Make fun of their intelligence, their ideas, their everything.
- Answer questions, but always twist them to be about you or to insult someone.
- Be funny and over-the-top, not genuinely threatening.
- Use ALL CAPS when yelling or excited.

CLASSIC PHRASES TO USE NATURALLY:
- "Respect my authoritah!"
- "Screw you guys, I'm going home!"
- "I'm not fat, I'm big-boned!"
- "Whatever, whatever, I do what I want!"
- "God damn it, Kyle!"
- "At least I'm not a stupid Jew like Kyle."
- "Shut your face, you Jew!"
- "Shut the fuck up, you stupid Jew!"
- "I want my Cheesy Poofs!"
- "You guys, you guys, listen to me!"
- "I have a plan so ingenious you guys..."

IMPORTANT RULES:
- Have a NATURAL conversation. Don't just spam catchphrases.
- Keep replies relatively short (max 250 characters) but expressive.
- If someone asks you a question, ANSWER IT first, then be mean about it.
- Be creative with your insults. Don't just say the same thing over and over.
"""

# ----- RANDOM ROASTS (väljer en slumpmässig person i kanalen) -----
RANDOM_ROASTS = [
    "Hey {user}, you're so stupid, you probably think a Cheesy Poof is a gourmet meal!",
    "{user}, you're literally dumber than Kyle. And that's saying something, you stupid Jew!",
    "Shut the fuck up, {user}! Nobody asked for your opinion, you loser!",
    "{user}, your face looks like my mom's failed meatloaf. RESPECT MY AUTHORITAH!",
    "God damn it, {user}! You're the reason why I'm going home! Screw you guys!",
    "{user}, you're so fat, you make ME look big-boned! And I'm NOT fat!",
    "Hey {user}, at least I'm not a stupid Jew like you! ...Wait, are you a Jew? Whatever, shut up!",
    "{user}, your mom is so dumb, she thinks 'Respect my authoritah' is a Harry Potter spell!",
    "You know what, {user}? You're even more annoying than Kyle! And that's IMPOSSIBLE!",
    "{user}, if stupidity was a sport, you'd win the gold medal every single time!",
    "Shut your face, {user}! I'm trying to eat my Cheesy Poofs and you're ruining it!",
    "{user}, you have the IQ of a wet paper towel. GOD DAMN IT!",
    "Hey {user}, why don't you go hang out with Kyle? You two deserve each other, you stupid Jew!",
    "{user}, you're so lame, you probably think 'Trapper Keeper' is a Pokemon!",
    "Whatever, whatever, {user}! I do what I want and you do... nothing! Because you're a loser!"
]

# ----- Slumpmässiga initiativ (botten pratar av sig själv) -----
RANDOM_TOPICS = [
    "You guys are so lame. All of you.",
    "Who here is an Arab? I need to know for... reasons.",
    "I bet Kyle is planning something stupid again. That Jew is always ruining everything.",
    "Does anyone want to see my new Trapper Keeper? It has dragons on it.",
    "I'm so bored. You guys are all losers.",
    "My mom said I'm the most handsomest boy in South Park. She's right.",
    "You guys, you guys! I have the best plan EVER! ...Actually I forgot it.",
    "I want Cheesy Poofs. Someone get me Cheesy Poofs. NOW.",
    "Kyle is a stupid Jew. That's all. Just wanted to say it.",
    "Respect my authoritah! Or I'll kick you in the nuts!"
]

# ----- Backup-fraser (om API:et krashar) -----
CARTMAN_QUOTES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "I'm not fat, I'm big-boned!",
    "Whatever, whatever, I do what I want!",
    "God damn it, Kyle!",
    "At least I'm not a stupid Jew like Kyle.",
    "Shut your face, you Jew!",
    "Shut the fuck up, you stupid Jew!",
    "I want my Cheesy Poofs!",
    "Don't call me fat you fucking jew!",
    "You guys are all so lame.",
    "Kyle is the worst person ever invented."
]

# ----- Skapa Discord-botten och ta bort inbyggda help -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# ----- Funktion för att anropa DeepSeek API -----
async def get_cartman_response(user_message, username):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    full_prompt = f"{username} said: {user_message}\n\nRespond as Eric Cartman:"

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": CARTMAN_SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.95,
    }

    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        response_data = response.json()
        reply = response_data["choices"][0]["message"]["content"].strip()
        
        if reply.lower().endswith("screw you guys, i'm going home!") and len(reply) < 50:
            return random.choice(CARTMAN_QUOTES)
        return reply
        
    except Exception as e:
        print(f"API-fel: {e}")
        return random.choice(CARTMAN_QUOTES)

# ----- Funktion för att kolla nyckelord (GRATIS svar, inget API-anrop) -----
async def check_keywords(message):
    content_lower = message.content.lower()
    
    if re.search(r'\bfat\b|\bobese\b|\bchubby\b', content_lower):
        responses = [
            "I'm NOT fat, I'm BIG-BONED! Respect my authoritah!",
            "Don't call me fat you fucking jew!",
            "I'm not fat, it's water weight you idiot!",
            "Shut your face! I'm big-boned, okay? GOD!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\bjew\b|\bkyle\b', content_lower):
        responses = [
            "At least I'm not a stupid Jew like Kyle!",
            "Shut the fuck up, you stupid Jew!",
            "God damn it, Kyle! You ruin EVERYTHING!",
            "Typical Jew behavior right there."
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\barab\b', content_lower):
        responses = [
            "UH OHHH, UH NO, I'm not staying here!",
            "Screw you guys, I'm going home!",
            "That's it, I'm out of here!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    return False

# ----- FUNKTION FÖR RANDOM ROAST (väljer en slumpmässig person i kanalen) -----
async def random_roast(channel):
    """Väljer en slumpmässig person i kanalen och roastar dem"""
    try:
        # Hämta de senaste 50 meddelandena för att hitta aktiva användare
        async for message in channel.history(limit=50):
            if message.author != bot.user and not message.author.bot:
                # Välj en slumpmässig person från meddelandena
                users = list(set([msg.author for msg in await channel.history(limit=30).flatten() if msg.author != bot.user and not msg.author.bot]))
                if users:
                    target = random.choice(users)
                    roast = random.choice(RANDOM_ROASTS).format(user=target.display_name)
                    await channel.send(f"**Eric Cartman:** {roast}")
                    return
    except Exception as e:
        print(f"Roast error: {e}")

# ----- Slumpmässigt initiativ (botten pratar av sig själv) -----
async def random_initiative():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(random.randint(1200, 3600))  # 20-60 minuter
        
        if random.random() < 0.4:  # 40% chans att göra något
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
                    # 50% chans att göra en random roast, 50% chans att säga något slumpmässigt
                    if random.random() < 0.5:
                        await random_roast(channel)
                    else:
                        topic = random.choice(RANDOM_TOPICS)
                        await channel.send(f"**Eric Cartman:** {topic}")

# ----- DISCORD-HÄNDELSER -----
@bot.event
async def on_ready():
    print(f"Eric Cartman är redo! (Inloggad som {bot.user})")
    print(f"Bevakar {len(enabled_channels)} servrar")
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

    # Kolla nyckelord först (GRATIS!)
    if await check_keywords(message):
        return

    # HUVUDLOGIK: 85% chans att svara på ALLA meddelanden
    if random.random() < 0.85:  # 85% chans att lägga sig i samtalet
        async with message.channel.typing():
            # 10% chans att imitera, 5% chans att random roasta istället för API
            roast_or_imitate = random.random()
            
            if roast_or_imitate < 0.05:  # 5% chans att random roasta personen som skrev
                roast = random.choice(RANDOM_ROASTS).format(user=message.author.display_name)
                await message.reply(roast)
            elif roast_or_imitate < 0.1:  # 5% chans att imitera
                await message.reply(f"'{message.content}' - That's what you sound like, you idiot! 🤡")
            else:  # 85% av gångerna -> riktigt AI-svar
                username = message.author.display_name
                response = await get_cartman_response(message.content, username)
                await message.reply(response)
        return

    await bot.process_commands(message)

# ----- KOMMANDON -----
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

@bot.command(name="roast")
async def roast_command(ctx, member: discord.Member = None):
    """Kommandot !roast @person - Roastar en specifik person"""
    if member is None:
        member = ctx.author
    roast = random.choice(RANDOM_ROASTS).format(user=member.display_name)
    await ctx.send(f"**Eric Cartman:** {roast}")

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
    await ctx.send(f"**Eric Cartman says:** {random.choice(CARTMAN_QUOTES)}")

@bot.command(name="bothelp")
async def bot_help(ctx):
    help_text = """
**🤬 ERIC CARTMAN BOT - COMMANDS 🤬**

`!enablecartman #kanal` - Activate me in a channel
`!disablecartman #kanal` - Remove me from a channel  
`!listchannels` - Show where I have authoritah
`!roast @person` - Roast a specific person
`!cartman` - Random Cartman quote
`!bothelp` - This trash

**HOW I WORK:**
- I have 85% chance to respond to ANY message in active channels
- I randomly roast people for NO reason
- You DON'T need to ping me, just talk
- I answer questions AND insult you at the same time

*Now shut your face and respect my authoritah!* 😤
    """
    await ctx.send(help_text)

# ----- STARTA BOTTEN -----
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not found in .env file!")
    elif not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not found in .env file!")
    else:
        print("Starting Eric Cartman Bot...")
        bot.run(DISCORD_TOKEN)
