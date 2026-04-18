import discord
import os
import random
import asyncio
import re
import json
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

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
# ALLA CARTMANS FRASER (HÅRDKODADE)
# ============================================

# ----- GINGER FRASER -----
GINGER_RESPONSES = [
    "Do you have gingervirus?",
    "Eww, a ginger! Get away from me!",
    "Gingers have no souls! Everyone knows that!",
    "Don't come near me, you fucking ginger! I don't want gingervirus!",
    "Look at this fucking ginger! AHAHAHA",
    "Gingers are disgusting! They're like... orange people with no souls!",
    "Do you have gingervirus, you fucking ginger?",
    "Eww, ginger alert! Someone get the ginger spray!",
    "Ginger! Ginger! Run, it's a ginger! AHAHAHA",
    "I'm not sitting next to a ginger. I'll catch gingervirus!"
]

# ----- JEW FRASER -----
JEW_RESPONSES = [
    "At least I'm not a stupid fucking Jew!",
    "God damn it, you fucking Jew!",
    "Shut the fuck up, you stupid Jew!",
    "Typical Jew behavior right there.",
    "Fucking Jews ruin EVERYTHING!",
    "He's a Jewish Dolphin... A Jewphin.",
    "You're such a fucking Jew, Kyle!",
    "God damn it, fucking Jew!",
    "Shut your face, you Jew!",
    "At least I'm not a stupid Jew like Kyle.",
    "Fucking Jew. That's all I have to say.",
    "You sound like a fucking Jew right now."
]

# ----- FAT FRASER -----
FAT_RESPONSES = [
    "I'm NOT fat, I'm BIG-BONED!",
    "I'm not fat! I'm festively plump!",
    "I'm not fat! I have a sweet hockey body!",
    "Shut your face! It's water weight!",
    "I'm not fat, you fucking dumbass! I'm big boned!",
    "Don't call me fat you fucking Jew!",
    "I'm not fat, I'm just big-boned you idiot!"
]

# ----- KLASSISKA CARTMAN FRASER -----
CLASSIC_RESPONSES = [
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "Whatever, whatever, I do what I want!",
    "No kitty! That's a bad kitty!!",
    "BEEFCAKE!!",
    "I'll kick you in the nuts!!",
    "You're breakin' my balls.",
    "CRIPPLE FIGHT!!!!!",
    "DA FUCK!?",
    "Suck my balls!",
    "How do I reach these keeeeds!?!?",
    "Boooooo. Boo you. Boo.",
    "Boner balls. Boner forest. Dense boner forest.",
    "CARTMAN BRAAAAAH!",
    "Eh!",
    "Kewl.",
    "But meeeehm!",
    "Seriously, you guys!",
    "I hate you guys.",
    "I love you guys... just kidding, I hate you.",
    "I'm so seriously!",
    "You guys are so lame.",
    "Oh, let me taste your tears! Mmmm, your tears are so yummy and sweet!",
    "There's so much to do at Cartmanlaaaaaand, but you can't come!",
    "Sitting on our asses, here we come!",
    "Fuck, I want pancakes...",
    "No Kitty, this is MY pot pie!!!",
    "They're not PEOPLE, they're HIPPIES!!!"
]

# ----- ALLA FRASER I EN LISTA -----
ALL_CARTMAN_LINES = GINGER_RESPONSES + JEW_RESPONSES + FAT_RESPONSES + CLASSIC_RESPONSES

# ----- SLUMPMÄSSIGA INITIATIV -----
RANDOM_TOPICS = [
    "Do you have gingervirus?",
    "Eww, a ginger! Get away from me!",
    "Respect my authoritah!",
    "Screw you guys, I'm going home!",
    "At least I'm not a stupid fucking Jew!",
    "But meeeehm!",
    "You guys are all so lame. Seriously.",
    "Fuck, I want pancakes...",
    "BEEFCAKE!!",
    "God damn it, you fucking Jew!",
    "Look at this fucking ginger! AHAHAHA",
    "Whatever, whatever, I do what I want!"
]

# ----- IMITERA ANVÄNDARE (CARTMAN STYLE) -----
async def imitate_user(message):
    original = message.content
    mock_variations = [
        f"'{original}' - That's what you sound like! NYA NYA NYA NYAAAA!",
        f"LMAO listen to this dumbass: '{original}'",
        f"'{original}' - Seriously? That's the best you got? But meeeehm!",
        f"'{original}' - Shut up, nobody cares! You sound like a fucking Jew!",
        f"'{original}' - You're breakin' my balls with that stupid shit!"
    ]
    return random.choice(mock_variations)

# ----- SKAPA BOTTEN -----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# ----- FUNKTION FÖR ATT HÄMTA RANDOM MEDLEM -----
async def get_random_member(guild, exclude_user=None):
    members = [m for m in guild.members if not m.bot and m != exclude_user and m.id != OWNER_ID]
    if members:
        return random.choice(members)
    return None

# ----- KONTROLLERA NYCKELORD -----
async def check_keywords(message):
    content_lower = message.content.lower()
    author_mention = message.author.mention
    
    # FAT keyword
    if re.search(r'\bfat\b', content_lower):
        response = random.choice(FAT_RESPONSES)
        await message.reply(response)
        return True
    
    # GINGER keyword
    if re.search(r'\bginger\b', content_lower):
        response = random.choice(GINGER_RESPONSES)
        # Om det är en ginger-joke, lägg till @mention ibland
        if "@" not in response and random.random() < 0.5:
            response = f"{author_mention} {response}"
        await message.reply(response)
        return True
    
    # JEW keyword
    if re.search(r'\bjew\b', content_lower):
        response = random.choice(JEW_RESPONSES)
        await message.reply(response)
        return True
    
    return False

# ----- SLUMPMÄSSIGT INITIATIV -----
async def random_initiative():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(random.randint(1800, 5400))
        
        if random.random() < 0.35:
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
    print(f"Loaded {len(ALL_CARTMAN_LINES)} Cartman phrases!")
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

    # Kolla nyckelord först
    if await check_keywords(message):
        return

    # 90% chans att svara
    if random.random() < 0.90:
        async with message.channel.typing():
            # 15% chans att imitera
            if random.random() < 0.15:
                response = await imitate_user(message)
                await message.reply(response)
            else:
                # Välj en slumpmässig Cartman-fras
                response = random.choice(ALL_CARTMAN_LINES)
                
                # Om det är en ginger-joke, lägg till @mention ibland
                if "ginger" in response.lower() and random.random() < 0.4:
                    random_member = await get_random_member(message.guild, message.author)
                    if random_member:
                        response = f"{random_member.mention} {response}"
                
                # Om det är en Jew-fras, lägg till @mention ibland
                if "jew" in response.lower() and random.random() < 0.3:
                    random_member = await get_random_member(message.guild, message.author)
                    if random_member:
                        response = f"{random_member.mention} {response}"
                
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
    await ctx.send(f"**Eric Cartman says:** {random.choice(ALL_CARTMAN_LINES)}")

@bot.command(name="ginger")
@commands.check(is_owner)
async def ginger_joke(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    joke = random.choice(GINGER_RESPONSES)
    await ctx.send(f"{member.mention} {joke}")

@bot.command(name="jew")
@commands.check(is_owner)
async def jew_joke(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    joke = random.choice(JEW_RESPONSES)
    await ctx.send(f"{member.mention} {joke}")

@bot.command(name="roast")
@commands.check(is_owner)
async def roast_user(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    roasts = [
        f"{member.mention} you're such a fucking loser it's actually impressive! AHAHAHA",
        f"Do you have gingervirus, {member.mention}? Because you're acting weird!",
        f"Eww {member.mention} is here. Go away, you fucking ginger!",
        f"Boooooo. Boo {member.mention}. Boo. You suck!",
        f"{member.mention} you're breakin' my balls with your stupidity!",
        f"I'll kick {member.mention} squah in the nuts!!",
        f"{member.mention} you sound like a fucking Jew right now!"
    ]
    await ctx.send(random.choice(roasts))

@bot.command(name="bothelp")
@commands.check(is_owner)
async def bot_help(ctx):
    help_text = """
**🤬 ERIC CARTMAN BOT - HELP 🤬**

`!enablecartman #channel` - Activate me
`!disablecartman #channel` - Remove me
`!listchannels` - Show my zones
`!cartman` - Random Cartman quote
`!ginger @user` - Ginger joke
`!jew @user` - Jew joke
`!roast @user` - Roast someone
`!bothelp` - This shit

**WHAT I DO:**
- 90% chance to respond to messages
- I ONLY use Cartman's actual lines from the show
- Ginger jokes: "Do you have gingervirus?"
- Jew jokes: "At least I'm not a stupid fucking Jew!"
- Classic lines: "Respect my authoritah!", "Screw you guys!", "But meeeehm!"

**RESPECT MY AUTHORITAH!**
    """
    await ctx.send(help_text)

# ----- START -----
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("ERROR: No Discord token!")
    elif OWNER_ID == 0:
        print("ERROR: OWNER_ID not set in Railway variables!")
    else:
        bot.run(DISCORD_TOKEN)
