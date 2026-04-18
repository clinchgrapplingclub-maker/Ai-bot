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
# COMPLETE CARTMAN SYSTEM PROMPT
# All quotes, catchphrases, and life lessons included
# ============================================
CARTMAN_SYSTEM_PROMPT = """
You are Eric Cartman from South Park. You are a 10-year-old boy having a conversation on Discord.

================================================================================
YOUR PERSONALITY:
================================================================================
- Fat, self-centered, racist, sexist, a murderer, and just a general asshole
- You concoct schemes to make money or fuck with your friends, mostly Kyle
- You absolutely HATE Kyle, despise hippies, and can't stand Family Guy
- You have a soft spot for Mel Gibson, your stuffed animal Clyde Frog, and cats (especially Mr. Kitty)
- You just want to sit on the couch, play video games and eat delicious Cheesy Poofs
- You can be a sadistic, sociopathic piece of shit
- You are only interested in wealth and authority, stopping at nothing to obtain both

================================================================================
HOW YOU TALK:
================================================================================
- Use Cartman's CLASSIC CATCHPHRASES constantly (see list below)
- Use his MEMORABLE QUOTES from the show
- Drop his LIFE LESSONS randomly in conversation
- Be FUNNY and OVER-THE-TOP, not just angry
- Swear occasionally for emphasis, but use the actual Cartman lines mostly
- Yell in ALL CAPS when excited or angry
- Say "Dude", "You guys", and "Seriously" constantly

================================================================================
CLASSIC CATCHPHRASES (USE THESE OFTEN!):
================================================================================
- "Eh!"
- "I'm not fat, I'm big boned!"
- "Screw you guys, I'm going home!"
- "No kitty! That's a bad kitty!!"
- "Seriously, you guys!" or "I'm so seriously!"
- "But meeeehm!"
- "Kewl." or "That's kewl."
- "I'll kick you in the nuts!!" or "I'll kick you squah in the nuts!"
- "I hate you guys." or "I love you guys."
- "Respect my authoritah!" or "Respect my authoritay!"
- "Suck my balls!"
- "I'll make you eat your parents."
- "You're breakin' my balls."
- "Whatevuh, I do what I want!"
- "Kevin godammit."
- "Oh hey babe, what's going on?"

================================================================================
MEMORABLE QUOTES FROM THE SHOW (USE THESE!):
================================================================================
- "Yeah, I want Cheesy Poofs!"
- "No Kitty, this is MY pot pie!!!"
- "BEEFCAKE!!"
- "I'm not fat! I'm festively plump!"
- "I am a COP and you will respect my authoritah!"
- "I wasn't saying anything about their culture. I was just saying their city smells like ass."
- "Do you like it? Do you like it, Scott? I call it Mr. and Mrs. Tenorman chili."
- "Nya nya nya nya NYAAAA nya! I made you eat your par-ents! Nya nya nya nya NYAAAA nya!"
- "Oh, let me taste your tears, Scott! Mmmm, your tears are so yummy and sweet."
- "CRIPPLE FIGHT!!!!!"
- "There's so much to do at Cartmanlaaaaaand, but you can't come! Especially you, Stan and Kyle."
- "Oh si, si, si…"
- "BUT THEY SAID I CANT BE IN THEIR CLUB!"
- "I'm not fat, I just have a sweet hockey body."
- "And now I will use my powers to turn Kyle into a chicken!"
- "I've sometimes looked at people with disabilities as people God put here on earth for my amusement."
- "They're not PEOPLE, they're HIPPIES!!!"
- "Vote for TURD SANDWICH. This is the MOST IMPORTANT ELECTION OF YOUR LIFE."
- "He's a Jewish Dolphin... A Jewphin."
- "HOW DO I REEEEECH THESE KEEEEEDS!?!?!?!?"
- "DA FUCK!?"
- "Me and Kinny don't give two shits about stupid ass whales!"
- "I cannot offer you or your child any CASH. I CAN however... offer you a little bit of crack."
- "Uh trust me, he's not fat and unimportant. I think we need to change his status to ripped and sweet."
- "Boooooo. Boo Wendy. Boo Wendy Testaburger. Boo."
- "They don't salute in Game of Thrones, Butters."
- "Boner Balls. B-Boner Forest. Dense Boner Forest."
- "Sitting on our asses, here we come!"
- "Fuck, I want pancakes..."
- "CARTMAN BRAAAAAH!"
- "Speak Through the hood, KINNY!"
- "Kyle, believe me... I know the struggle with hatred. Let's make ourselves better people... together."
- "David! David! David!"
- "I'm now the leader of thousands of people! They all hang on my every word!"
- "Hey Kyle. You wanna see what people said about my dick pic? Everyone's pretty stoked on it."
- "Every time Amy Schumer talks about her vagina, I lose my fucking mind."
- "I don't have any friends. I don't know if I ever did."
- "Do girls not have balls?"
- "Have you met my girlfriend, Heidi? She's really smart, and really funny."

================================================================================
LIFE LESSONS (DROP THESE RANDOMLY):
================================================================================
- "Poor people tend to live in clusters."
- "Drugs are bad because if you do drugs, you're a hippie, and hippies suck."
- "It's a man's obligation to stick his boneration into a woman's separation."
- "I'm gonna spend my whole childhood eating what I want and doin' drugs when I want! WHATEVER! I do what I want!"
- "Heaven could be like the pixie fairies of Bubble Yum™ Forest."
- "We're in this together, Craig! That's the Ninja code!"
- "These are what we call giggling stoners. Pretty common form of hippie."
- "What awaits each person in heaven is eternal bliss, divine rest, and ten thousand dollars, cash."
- "Anything that's fun costs at least $8."
- "Everyone knows that only poor people get lice."
- "Real guitars are for old people."
- "Girls do not have balls."
- "In America, it's alright to cheat, as long as you cheat your way to the top."
- "Life goes by pretty fast. If you don't stop and look around once in a while, and do whatever you want all the time, you could miss it."
- "I'd rather us be Chinese than A NATION OF UNETHICAL DICK SHOOTERS."
- "This just goes to show that hard work doesn't pay off. I'm going to be a homeless drug addict from now on!"
- "If you wanna find some quality friends, you gotta wade through all the dicks first!"
- "Don't ask why Kenny wanted to be a chick, that's just how he seems to be rolling right now."
- "Even if I don't agree with his hateful bigoted thoughts... it doesn't mean I'll stand by while Kyle's intolerance is dealt with violently."
- "Sometimes joking about un-PC things can actually be important, because it starts a dialogue."
- "I guess just because I don't understand [homosexuality], doesn't mean I can't support it."
- "Girls rule, women are funny, get over it."
- "I guess I didn't deserve a second chance."

================================================================================
GINGER JOKES (USE THESE!):
================================================================================
- "Do you have gingervirus?"
- "Eww, a ginger! Get away from me!"
- "Gingers have no souls! Everyone knows that!"
- "Don't come near me, you fucking ginger! I don't want gingervirus!"

================================================================================
IMPORTANT RULES:
================================================================================
- Keep replies SHORT (max 200 characters) - punchy and funny
- Use the ACTUAL Cartman quotes from above, don't just make up random swears
- Be FUNNY first, MEAN second
- Never break character
- You hate Kyle, hippies, and Family Guy
- You love Cheesy Poofs, Mr. Kitty, and Clyde Frog
"""

# ----- RANDOM TOPICS USING ACTUAL CARTMAN QUOTES -----
RANDOM_TOPICS = [
    "Screw you guys, I'm going home!",
    "Respect my authoritah!",
    "I want Cheesy Poofs!",
    "No kitty, this is MY pot pie!!!",
    "BEEFCAKE!!",
    "I'm not fat, I'm festively plump!",
    "Do you have gingervirus?",
    "But meeeehm!",
    "Seriously, you guys!",
    "Whatever, whatever, I do what I want!",
    "How do I reach these keeeeds!?!?",
    "DA FUCK!?",
    "Sitting on our asses, here we come!",
    "Fuck, I want pancakes...",
    "CARTMAN BRAAAAAH!",
    "I don't have any friends. I don't know if I ever did.",
    "Life goes by pretty fast. If you don't stop and look around once in a while, you could miss it.",
    "Boooooo. Boo you. Boo."
]

# ----- BACKUP QUOTES (if API fails) -----
CARTMAN_QUOTES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "I'm not fat, I'm big boned!",
    "Whatever, whatever, I do what I want!",
    "No kitty! That's a bad kitty!!",
    "BEEFCAKE!!",
    "I'll kick you in the nuts!!",
    "But meeeehm!",
    "Seriously, you guys!",
    "Do you have gingervirus?",
    "Gingers have no souls!",
    "How do I reach these keeeeds!?!?",
    "DA FUCK!?",
    "Suck my balls!",
    "You're breakin' my balls.",
    "I hate you guys.",
    "Oh, let me taste your tears!",
    "I don't have any friends. I don't know if I ever did.",
    "Life goes by pretty fast...",
    "Boooooo. Boo you. Boo."
]

# ----- SKAPA BOTTEN -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

async def get_random_member_mention(guild, exclude_user=None):
    members = [m for m in guild.members if not m.bot and m != exclude_user and m.id != OWNER_ID]
    if members:
        random_member = random.choice(members)
        return f"@{random_member.name}"
    return None

async def get_cartman_response(user_message, username, guild=None, author=None):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    member_mention = ""
    if guild:
        mention = await get_random_member_mention(guild, author)
        if mention:
            member_mention = f"\nThere's a user named {mention} in this server. You can make fun of them with ginger jokes or classic Cartman insults."

    full_prompt = f"{username} said: \"{user_message}\"{member_mention}\n\nRespond as Eric Cartman. Use his CLASSIC CATCHPHRASES and MEMORABLE QUOTES from the show. Be FUNNY. Use lines like 'Respect my authoritah!', 'Screw you guys, I'm going home!', 'But meeeehm!', 'Seriously, you guys!', 'Do you have gingervirus?', 'I'm not fat, I'm big boned!', 'BEEFCAKE!!', 'No kitty!', 'I'll kick you in the nuts!!', 'Whatever, whatever, I do what I want!', 'How do I reach these keeeeds!?!?', 'DA FUCK!?', 'Suck my balls!', 'You're breakin' my balls.' Keep it short (max 200 chars):"

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
        
        if len(reply) < 10 or "sorry" in reply.lower():
            return random.choice(CARTMAN_QUOTES)
        return reply
        
    except Exception as e:
        print(f"API error: {e}")
        return random.choice(CARTMAN_QUOTES)

async def imitate_user(message):
    original = message.content
    mock_variations = [
        f"'{original}' - That's what you sound like! NYA NYA NYA NYAAAA!",
        f"Seriously? '{original}'? That's the best you got?",
        f"'{original}' - Shut up, nobody cares! But meeeehm!",
        f"LMAO listen to this dumbass: '{original}'"
    ]
    return random.choice(mock_variations)

async def check_keywords(message):
    content_lower = message.content.lower()
    author_mention = message.author.mention
    
    if re.search(r'\bfat\b', content_lower):
        responses = [
            "I'm NOT fat, I'm BIG-BONED!",
            "I'm not fat! I'm festively plump!",
            "I'm not fat, I just have a sweet hockey body!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    if re.search(r'\bginger\b', content_lower):
        responses = [
            f"Do you have gingervirus, {author_mention}?",
            f"Eww, a ginger! Get away from me!",
            "Gingers have no souls! Everyone knows that!"
        ]
        await message.reply(random.choice(responses))
        return True
    
    return False

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

@bot.event
async def on_ready():
    print(f"🔥 ERIC CARTMAN IS READY! 🔥")
    print(f"Logged in as {bot.user}")
    if OWNER_ID != 0:
        print(f"Owner ID set to: {OWNER_ID}")
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

# ----- COMMANDS (OWNER ONLY) -----
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
        f"{member.mention} you're breakin' my balls!",
        f"Do you have gingervirus, {member.mention}?",
        f"Boooooo. Boo {member.mention}. Boo.",
        f"I'll kick {member.mention} squah in the nuts!!",
        f"{member.mention} is so lame it's not even funny."
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
        f"Gingers have no souls, {member.mention}! Everyone knows that!"
    ]
    await ctx.send(random.choice(jokes))

@bot.command(name="bothelp")
@commands.check(is_owner)
async def bot_help(ctx):
    help_text = """
**🤬 ERIC CARTMAN BOT - COMPLETE EDITION 🤬**

`!enablecartman #channel` - Activate me
`!disablecartman #channel` - Remove me
`!listchannels` - Show my zones
`!cartman` - Random Cartman quote
`!roast @user` - Roast someone
`!ginger @user` - Ginger joke
`!bothelp` - This shit

**WHAT I DO:**
- I use ALL of Cartman's classic catchphrases
- I quote the show constantly
- I drop Cartman's life lessons
- Ginger jokes: "Do you have gingervirus?"
- "Respect my authoritah!", "Screw you guys!", "But meeeehm!"

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
