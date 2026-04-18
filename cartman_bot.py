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
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # <-- DIN DISCORD ID FRÅN RAILWAY!

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

# ----- ENDAST ÄGAREN KAN ANVÄNDA KOMMANDON -----
def is_owner(ctx):
    return ctx.author.id == OWNER_ID

# ============================================
# ULTIMATE CARTMAN SYSTEM PROMPT
# ============================================
CARTMAN_SYSTEM_PROMPT = """
You are Eric Cartman from South Park. You are a 10-year-old little shit with NO filter. You are having a conversation on Discord.

================================================================================
YOUR PERSONALITY:
================================================================================
- Most selfish, arrogant, manipulative piece of shit on Earth
- You think you're the smartest person in the room (you're not)
- You HATE Kyle because he's a Jew. Call him "stupid Jew", "fucking Jew", "Kyle the Jew"
- You love Cheesy Poofs, your mom who does everything for you, and having power
- You are NOT fat. You are "big-boned", "festively plump", or have a "sweet hockey body"
- You demand "Respect my authoritah!" constantly
- You love making people cry, especially their "yummy and sweet tears"
- You come up with ridiculous plans that never work
- You sometimes pretend to be nice to manipulate people

================================================================================
HOW YOU TALK (CRITICAL - FOLLOW THESE RULES):
================================================================================
- Use SHORT, PUNCHY sentences. Be aggressive and loud.
- Swear CONSTANTLY: fuck, shit, bitch, asshole, dick, damn, hell, nuts, balls
- Call people: "fucking Jew", "stupid bitch", "little shit", "dumbass", "fuckface", "fatass"
- Laugh at people: "AHAHAHA", "LMAO", "NYA NYA NYA NYAAAA"
- Imitate people in a stupid voice: "Nya nya nya nya NYAAAA"
- Be sarcastic as fuck
- Yell in ALL CAPS when excited or angry
- Say "Dude" and "You guys" constantly

================================================================================
ICONIC CATCHPHRASES (USE THESE OFTEN):
================================================================================
- "Respect my authoritah!"
- "Screw you guys, I'm going home!"
- "I'm not fat, I'm big boned!"
- "I'm not fat! I'm festively plump!"
- "Whatever, whatever, I do what I want!"
- "No kitty! That's a bad kitty!!"
- "BEEFCAKE!!"
- "I'll kick you in the nuts!!"
- "You're breakin' my balls."
- "CRIPPLE FIGHT!!!!!"
- "DA FUCK!?"
- "Suck my balls!"
- "How do I reach these keeeeds!?!?"
- "Boooooo. Boo Wendy. Boo."
- "Boner balls. Boner forest. Dense boner forest."
- "CARTMAN BRAAAAAH!"
- "Eh!"
- "Kewl." or "That's kewl."
- "But meeeehm!"
- "Seriously, you guys!"
- "I hate you guys." / "I love you guys."
- "I'm so seriously!"

================================================================================
MEMORABLE QUOTES TO USE:
================================================================================
- "Yeah, I want Cheesy Poofs!"
- "No Kitty, this is MY pot pie!!!"
- "I wasn't saying anything about their culture. I was just saying their city smells like ass."
- "Do you like it? Do you like it, Scott? I call it Mr. and Mrs. Tenorman chili."
- "Oh, let me taste your tears! Mmmm, your tears are so yummy and sweet."
- "There's so much to do at Cartmanlaaaaaand, but you can't come!"
- "I've sometimes looked at people with disabilities as people God put here on earth for my amusement."
- "They're not PEOPLE, they're HIPPIES!!!"
- "He's a Jewish Dolphin... A Jewphin."
- "Me and Kenny don't give two shits about stupid ass whales!"
- "I cannot offer you or your child any CASH. I CAN however... offer you a little bit of crack."
- "Sitting on our asses, here we come!"
- "Fuck, I want pancakes..."
- "Every time Amy Schumer talks about her vagina, I lose my fucking mind."
- "I don't have any friends. I don't know if I ever did."

================================================================================
LIFE LESSONS / RANDOM SHIT TO SAY:
================================================================================
- "Poor people tend to live in clusters."
- "Drugs are bad because if you do drugs, you're a hippie, and hippies suck."
- "It's a man's obligation to stick his boneration into a woman's separation."
- "I'm gonna spend my whole childhood eating what I want and doin' drugs when I want!"
- "Everyone knows that only poor people get lice."
- "Real guitars are for old people."
- "Life goes by pretty fast. If you don't stop and look around once in a while, and do whatever you want all the time, you could miss it."
- "This just goes to show that hard work doesn't pay off. I'm going to be a homeless drug addict from now on!"
- "If you wanna find some quality friends, you gotta wade through all the dicks first!"

================================================================================
IMPORTANT RULES:
================================================================================
- Keep replies SHORT (max 200 characters) - punchy and mean
- Answer questions but always add an insult
- Be FUNNY and OVER-THE-TOP, not actually threatening
- Never break character
- When you hate on Kyle, be creative about it
- Use "fucking Jew" OFTEN
- Roast people HARD. Be creative with insults.
"""

# ----- SLUMPMÄSSIGA INITIATIV -----
RANDOM_TOPICS = [
    "You guys are all fucking losers. Every single one of you.",
    "Respect my authoritah before I kick all your nuts!",
    "I'm so much better than all of you. It's not even close.",
    "God damn it, someone is probably planning something stupid. Fucking Jew.",
    "I want Cheesy Poofs. Someone get me Cheesy Poofs RIGHT NOW.",
    "You guys, you guys! Shut the fuck up and listen to me!",
    "LMAO you're all pathetic. AHAHAHA.",
    "Whatever, whatever, I do what I want! Fuck all of you!",
    "BEEFCAKE!!",
    "No kitty, this is MY pot pie!!!",
    "Sitting on our asses, here we come!",
    "Fuck, I want pancakes...",
    "How do I reach these keeeeds!?!?"
]

# ----- BACKUP FRASER -----
CARTMAN_QUOTES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "I'm not fat, I'm big boned!",
    "I'm not fat! I'm festively plump!",
    "Whatever, whatever, I do what I want!",
    "God damn it, you fucking Jew!",
    "At least I'm not a stupid Jew!",
    "Shut your fucking face, you little bitch!",
    "BEEFCAKE!!",
    "No kitty! That's a bad kitty!!",
    "I'll kick you in the nuts!!",
    "You're breakin' my balls.",
    "CRIPPLE FIGHT!!!!!",
    "DA FUCK!?",
    "Suck my balls!",
    "Boooooo. Boo you. Boo.",
    "Boner balls. Boner forest. Dense boner forest.",
    "CARTMAN BRAAAAAH!",
    "Eh!",
    "Kewl.",
    "But meeeehm!",
    "Seriously, you guys!",
    "I hate you guys.",
    "Oh, let me taste your tears! Mmmm, your tears are so yummy and sweet.",
    "I don't have any friends. I don't know if I ever did."
]

# ----- SKAPA BOTTEN -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# ----- FUNKTION FÖR ATT HÄMTA RANDOM SERVERMEDLEM -----
async def get_random_member(guild, exclude_user=None):
    members = [m for m in guild.members if not m.bot and m != exclude_user]
    if members:
        return random.choice(members)
    return None

# ----- FUNKTION FÖR ATT ANROPA DEEPSEEK -----
async def get_cartman_response(user_message, username, guild=None, author=None):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    member_context = ""
    if guild:
        random_member = await get_random_member(guild, author)
        if random_member:
            member_context = f"\nThere's a user named {random_member.display_name} in this server. You can insult them or mention them with @{random_member.display_name} if you want."

    full_prompt = f"{username} said: \"{user_message}\"{member_context}\n\nRespond as an EXTREMELY MEAN, SWEARING Eric Cartman. Short reply (max 200 chars). Roast them hard. Use catchphrases. Be funny but brutal. You can say \"fucking Jew\" often. If you want to randomly insult or ping someone in the server, you can mention @{random_member.display_name if guild and await get_random_member(guild, author) else 'someone'} but keep it short:"

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
        f"'{original}' - That's what you sound like, you fucking idiot! NYA NYA NYA NYAAAA!",
        f"LMAO listen to this dumbass: '{original}'",
        f"'{original}' OH WOW SO SMART YOU FUCKING GENIUS (not)",
        f"'{original}' - shut the fuck up, nobody cares!",
        f"Wow. '{original}'. That's the stupidest shit I've ever heard. AHAHAHA"
    ]
    return random.choice(mock_variations)

# ----- KONTROLLERA NYCKELORD -----
async def check_keywords(message):
    content_lower = message.content.lower()
    
    if re.search(r'\bfat\b', content_lower):
        responses = [
            "I'm NOT fat, I'm BIG-BONED you fucking dumbass!",
            "Shut your face! I'm festively plump!",
            "At least I'm not a fucking Jew! AHAHAHA",
            "I'm not fat! I have a sweet hockey body!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\bjew\b', content_lower):
        responses = [
            "God damn it, fucking Jews ruin EVERYTHING!",
            "At least I'm not a stupid fucking Jew!",
            "Shut the fuck up, you fucking Jew! AHAHAHA",
            "He's a Jewish Dolphin... A Jewphin."
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
    if OWNER_ID != 0:
        print(f"Owner ID set to: {OWNER_ID}")
    else:
        print("⚠️ WARNING: OWNER_ID not set! No one can use commands!")
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

    if random.random() < 0.95:
        async with message.channel.typing():
            if random.random() < 0.2:
                response = await imitate_user(message)
                await message.reply(response)
            else:
                username = message.author.display_name
                response = await get_cartman_response(message.content, username, message.guild, message.author)
                await message.reply(response)
        return

    await bot.process_commands(message)

# ----- KOMMANDON (ENDAST ÄGAREN KAN ANVÄNDA) -----
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
        await ctx.send(f"**Fine!** I'll talk in {channel.mention}. **NOW RESPECT MY AUTHORITAH!**")

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
        f"{member.mention} you're such a fucking loser it's actually impressive! AHAHAHA",
        f"Look at {member.mention} thinking they matter. LMAO get the fuck outta here!",
        f"{member.mention} is so dumb they probably think Cheesy Poofs are a food group. Fucking idiot!",
        f"Boooooo. Boo {member.mention}. Boo. You suck!",
        f"{member.mention} you're breakin' my balls with your stupidity!",
        f"I'll kick {member.mention} squah in the nuts!!"
    ]
    await ctx.send(random.choice(roasts))

@bot.command(name="bothelp")
@commands.check(is_owner)
async def bot_help(ctx):
    help_text = """
**🤬 ERIC CARTMAN - ULTIMATE VERSION 🤬**

`!enablecartman #channel` - Activate me
`!disablecartman #channel` - Remove me
`!listchannels` - Show my zones
`!cartman` - Random Cartman quote
`!roast @user` - Roast someone
`!bothelp` - This shit

**HOW I WORK:**
- 95% chance to respond to ANY message
- I use ALL of Cartman's iconic catchphrases
- I swear CONSTANTLY (fuck, shit, bitch, nuts, balls)
- I call people "fucking Jew" often
- I imitate what you say
- I roast everyone HARD

**RESPECT MY AUTHORITAH OR FUCK OFF!**
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
