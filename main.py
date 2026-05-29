import discord
from discord.ext import commands
import json
import os

# ✅ 봇 설정
TOKEN = os.getenv("TOKEN1")
DATA_FILE = "join_count.json"
CONFIG_FILE = "config.json"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ── 데이터 로드 / 저장 ──────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# ── 이벤트: 봇 준비 ────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ {bot.user} 로그인 완료")


# ── 이벤트: 멤버 입장 ──────────────────────────────────────────
@bot.event
async def on_member_join(member):
    data = load_data()
    user_id = str(member.id)

    if user_id not in data:
        data[user_id] = {"name": str(member), "join_count": 0, "leave_count": 0}

    data[user_id]["join_count"] += 1
    data[user_id]["name"] = str(member)
    save_data(data)

    config = load_config()
    channel_id = config.get(str(member.guild.id))
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(
                f"✅ **{member}** 님이 입장했어요! "
                f"(총 입장 횟수: {data[user_id]['join_count']}회)"
            )


# ── 이벤트: 멤버 퇴장 ──────────────────────────────────────────
@bot.event
async def on_member_remove(member):
    data = load_data()
    user_id = str(member.id)

    if user_id not in data:
        data[user_id] = {"name": str(member), "join_count": 0, "leave_count": 0}

    data[user_id]["leave_count"] += 1
    data[user_id]["name"] = str(member)
    save_data(data)

    config = load_config()
    channel_id = config.get(str(member.guild.id))
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(
                f"❌ **{member}** 님이 퇴장했어요! "
                f"(총 퇴장 횟수: {data[user_id]['leave_count']}회)"
            )


# ── 명령어: !들낙로그 #채널 ────────────────────────────────────
@bot.command(name="들낙로그")
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    config = load_config()
    config[str(ctx.guild.id)] = channel.id
    save_config(config)
    await ctx.send(f"✅ 들낙 로그 채널이 {channel.mention} 으로 설정됐어요!")


# ── 명령어: !입퇴장 @유저 ───────────────────────────────────────
@bot.command(name="입퇴장")
async def check_join_leave(ctx, member: discord.Member):
    data = load_data()
    user_id = str(member.id)

    if user_id not in data:
        await ctx.send(f"**{member}** 님의 기록이 없어요. (봇 추가 이후 기록부터 집계돼요)")
        return

    info = data[user_id]
    await ctx.send(
        f"📊 **{member}** 님 입퇴장 기록\n"
        f"입장 횟수: **{info['join_count']}회**\n"
        f"퇴장 횟수: **{info['leave_count']}회**"
    )


bot.run(TOKEN)
