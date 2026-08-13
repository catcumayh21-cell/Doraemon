import random
import asyncio
from datetime import date
import discord
from discord.ext import commands

# Cấu hình quyền hạn (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

# --- CẤU HÌNH HỆ THỐNG ---
OWNER_ID = 1448560066524610621  # THAY ID DISCORD CỦA BẠN VÀO ĐÂY
ALLOWED_ROLES = ["Admin", "Quản lý", "Mod"]  # Tên các Role được quyền dùng lệnh !addmoney

# Cơ sở dữ liệu lưu tạm thời
balances = {}
daily_tracker = {}
pending_battles = {}
inventories = {}
user_pets = {}
pray_cooldown = {}

# Danh sách vật phẩm trong Cửa Hàng
SHOP_ITEMS = {
    "nhan": {"name": "💍 Nhẫn Kim Cương", "price": 500},
    "xe": {"name": "🏎️ Siêu Xe", "price": 2000},
    "kiem": {"name": "🗡️ Kiếm Huyền Thoại", "price": 1000},
    "tra": {"name": "🧋 Trà Sữa Full Topping", "price": 50}
}

# Danh sách Pet, tỷ lệ rơi và ảnh minh họa
PET_DATABASE = {
    "meo": {
        "name": "Mèo Con Đáng Yêu",
        "rarity": "Common (Thường)",
        "rate": 45,
        "color": 0x95a5a6,
        "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600"
    },
    "cho": {
        "name": "Chó Shiba Ngáo",
        "rarity": "Common (Thường)",
        "rate": 35,
        "color": 0x3498db,
        "image": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=600"
    },
    "cao": {
        "name": "Cáo Tuyết Huyền Ảo",
        "rarity": "Rare (Hiếm)",
        "rate": 15,
        "color": 0x9b59b6,
        "image": "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=600"
    },
    "rong": {
        "name": "Rồng Lửa Cổ Đại",
        "rarity": "Legendary (Huyền Thoại)",
        "rate": 5,
        "color": 0xf1c40f,
        "image": "https://images.unsplash.com/photo-1577493340887-b7bdef550155?w=600"
    }
}

# --- CÁC HÀM TIỆN ÍCH ---
def get_balance(user_id):
    if user_id not in balances:
        balances[user_id] = 100
    return balances[user_id]

def get_inventory(user_id):
    if user_id not in inventories:
        inventories[user_id] = {}
    return inventories[user_id]

def get_user_pets(user_id):
    if user_id not in user_pets:
        user_pets[user_id] = {}
    return user_pets[user_id]

async def check_rich_kid(ctx, member: discord.Member):
    if get_balance(member.id) >= 1000000:
        role = discord.utils.get(ctx.guild.roles, name="Rich Kid")
        if role and role not in member.roles:
            try:
                await member.add_roles(role)
                await ctx.send(f"👑 Chúc mừng **{member.name}** đã đạt mốc **1.000.000 xu** và nhận danh hiệu **Rich Kid**! 🎩✨")
            except discord.Forbidden:
                pass

@bot.event
async def on_ready():
    print(f"Bot mini-game da online: {bot.user}")

# --- NHÓM LỆNH TIỀN TỆ & MINI-GAME ---

@bot.command()
async def tiền(ctx):
    bal = get_balance(ctx.author.id)
    await ctx.send(f"🪙 **{ctx.author.name}**, bạn đang có **{bal:,}** xu!")

@bot.command()
async def daily(ctx):
    user_id = ctx.author.id
    today = date.today()
    if user_id in daily_tracker and daily_tracker[user_id] == today:
        await ctx.send(f"❌ **{ctx.author.name}**, bạn đã nhận quà hôm nay rồi!")
        return
    bonus = random.randint(50, 200)
    balances[user_id] = get_balance(user_id) + bonus
    daily_tracker[user_id] = today
    await ctx.send(f"🎁 **{ctx.author.name}** đã điểm danh nhận **+{bonus}** xu!")
    await check_rich_kid(ctx, ctx.author)

@bot.command()
async def cf(ctx, bet: int = None, choice: str = None):
    if bet is None or choice is None:
        await ctx.send("👉 Cách chơi: `!cf <số_tiền> <ngua/sap>` (Ví dụ: `!cf 50 ngua`)")
        return
    choice = choice.lower()
    if choice not in ["ngua", "sap"]:
        await ctx.send("❌ Vui lòng chọn `ngua` hoặc `sap`!")
        return
    bal = get_balance(ctx.author.id)
    if bet <= 0 or bet > bal:
        await ctx.send("❌ Tiền cược không hợp lệ hoặc bạn không đủ tiền!")
        return
    result = random.choice(["ngua", "sap"])
    if choice == result:
        balances[ctx.author.id] += bet
        await ctx.send(f"🎉 Kết quả là **{result.upper()}**! Bạn THẮNG **+{bet:,}** xu!")
        await check_rich_kid(ctx, ctx.author)
    else:
        balances[ctx.author.id] -= bet
        await ctx.send(f"💀 Kết quả là **{result.upper()}**! Bạn THUA **-{bet:,}** xu!")

@bot.command()
async def give(ctx, member: discord.Member = None, amount: int = None):
    if member is None or amount is None:
        await ctx.send("👉 Cách dùng: `!give @tag_người_nhận <số_tiền>`")
        return
    if member.id == ctx.author.id or amount <= 0 or amount > get_balance(ctx.author.id):
        await ctx.send("❌ Số tiền hoặc người nhận không hợp lệ!")
        return
    balances[ctx.author.id] -= amount
    balances[member.id] = get_balance(member.id) + amount
    await ctx.send(f"💸 **{ctx.author.name}** đã chuyển **{amount:,}** xu cho **{member.name}**!")
    await check_rich_kid(ctx, member)

# --- NHÓM LỆNH CỬA HÀNG & TÚI ĐỒ ---

@bot.command()
async def shop(ctx):
    msg = "🛒 **CỬA HÀNG VẬT PHẨM** 🛒\n\n"
    for item_id, info in SHOP_ITEMS.items():
        msg += f"• **{info['name']}** (Mã: `{item_id}`) — Giá: **{info['price']:,}** xu\n"
    msg += "\n👉 Gõ `!buy <mã_vật_phẩm>` để mua đồ."
    await ctx.send(msg)

@bot.command()
async def buy(ctx, item_id: str = None):
    if item_id is None:
        await ctx.send("👉 Cách mua: `!buy <mã_vật_phẩm>`")
        return
    item_id = item_id.lower()
    if item_id not in SHOP_ITEMS:
        await ctx.send("❌ Vật phẩm không tồn tại!")
        return
    item = SHOP_ITEMS[item_id]
    user_bal = get_balance(ctx.author.id)
    if user_bal < item["price"]:
        await ctx.send(f"❌ Bạn không đủ xu để mua **{item['name']}**!")
        return
    balances[ctx.author.id] -= item["price"]
    inv = get_inventory(ctx.author.id)
    inv[item_id] = inv.get(item_id, 0) + 1
    await ctx.send(f"🎉 **{ctx.author.name}** đã mua thành công **{item['name']}**!")

@bot.command(aliases=["bag", "inventory"])
async def inv(ctx):
    inv = get_inventory(ctx.author.id)
    if not inv:
        await ctx.send(f"🎒 Túi đồ của **{ctx.author.name}** hiện đang trống rỗng!")
        return
    msg = f"🎒 **TÚI ĐỒ CỦA {ctx.author.name.upper()}**:\n"
    for item_id, quantity in inv.items():
        item_name = SHOP_ITEMS[item_id]["name"]
        msg += f"• {item_name}: x{quantity}\n"
    await ctx.send(msg)

# --- NHÓM LỆNH THÚ NUÔI (PET) ---

@bot.command()
async def hunt(ctx):
    pet_keys = list(PET_DATABASE.keys())
    weights = [PET_DATABASE[k]["rate"] for k in pet_keys]
    chosen_key = random.choices(pet_keys, weights=weights, k=1)[0]
    pet = PET_DATABASE[chosen_key]

    pets = get_user_pets(ctx.author.id)
    pets[chosen_key] = pets.get(chosen_key, 0) + 1

    embed = discord.Embed(
        title="🌲 BẠN ĐÃ BẮT ĐƯỢC MỘT PET MỚI! 🌲",
        description=f"Chúc mừng **{ctx.author.name}** đã thu phục được **{pet['name']}**!",
        color=pet["color"]
    )
    embed.add_field(name="Độ hiếm", value=f"⭐ {pet['rarity']}", inline=True)
    embed.add_field(name="Mã Pet", value=f"`{chosen_key}`", inline=True)
    embed.set_image(url=pet["image"])
    embed.set_footer(text="Gõ !zoo để xem chuồng thú hoặc !petinfo <mã> để xem thông tin")
    await ctx.send(embed=embed)

@bot.command(aliases=["zoo", "mypet"])
async def pets(ctx):
    user_pet_list = get_user_pets(ctx.author.id)
    if not user_pet_list:
        await ctx.send(f"🐾 **{ctx.author.name}** chưa có pet nào! Hãy gõ `!hunt` để đi săn.")
        return
    embed = discord.Embed(
        title=f"🐾 VƯỜN THÚ CỦA {ctx.author.name.upper()} 🐾",
        color=0x2ecc71
    )
    for pet_id, count in user_pet_list.items():
        pet_info = PET_DATABASE[pet_id]
        embed.add_field(
            name=f"{pet_info['name']} (x{count})",
            value=f"• Độ hiếm: {pet_info['rarity']}\n• Mã: `{pet_id}`",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def petinfo(ctx, pet_id: str = None):
    if pet_id is None:
        await ctx.send("👉 Cách dùng: `!petinfo <mã_pet>` (Ví dụ: `!petinfo meo`)")
        return
    pet_id = pet_id.lower()
    if pet_id not in PET_DATABASE:
        await ctx.send("❌ Không tìm thấy pet này trong hệ thống!")
        return
    pet = PET_DATABASE[pet_id]
    user_count = get_user_pets(ctx.author.id).get(pet_id, 0)
    embed = discord.Embed(
        title=f"📖 THÔNG TIN PET: {pet['name'].upper()}",
        color=pet["color"]
    )
    embed.add_field(name="Độ hiếm", value=pet["rarity"], inline=True)
    embed.add_field(name="Đang sở hữu", value=f"x{user_count}", inline=True)
    embed.set_image(url=pet["image"])
    await ctx.send(embed=embed)

# --- TÍNH NĂNG CẦU NGUYỆN / MỞ QUÀ (PRAY) ---

@bot.command(aliases=["curse", "crate"])
async def pray(ctx):
    user_id = ctx.author.id
    current_time = asyncio.get_event_loop().time()

    if user_id in pray_cooldown and current_time - pray_cooldown[user_id] < 300:
        remaining = int(300 - (current_time - pray_cooldown[user_id]))
        await ctx.send(f"⏳ **{ctx.author.name}**, bạn cần chờ **{remaining} giây** nữa để tiếp tục cầu nguyện.")
        return

    pray_cooldown[user_id] = current_time
    event_type = random.choices(["cash", "pet", "item", "nothing"], weights=[40, 35, 20, 5], k=1)[0]

    if event_type == "cash":
        reward_money = random.randint(100, 500)
        balances[user_id] = get_balance(user_id) + reward_money
        await ctx.send(f"✨ Lời cầu nguyện linh ứng! **{ctx.author.name}** nhận được **+{reward_money}** xu! 🪙")
        await check_rich_kid(ctx, ctx.author)

    elif event_type == "pet":
        pet_keys = list(PET_DATABASE.keys())
        chosen_pet_key = random.choice(pet_keys)
        pet = PET_DATABASE[chosen_pet_key]
        pets = get_user_pets(user_id)
        pets[chosen_pet_key] = pets.get(chosen_pet_key, 0) + 1

        embed = discord.Embed(
            title="✨ ĐƯỢC THẦN LINH BAN THÚ NUÔI! ✨",
            description=f"**{ctx.author.name}** cầu nguyện và nhận được **{pet['name']}**!",
            color=pet["color"]
        )
        embed.set_image(url=pet["image"])
        await ctx.send(embed=embed)

    elif event_type == "item":
        item_keys = list(SHOP_ITEMS.keys())
        chosen_item_key = random.choice(item_keys)
        item = SHOP_ITEMS[chosen_item_key]
        inv = get_inventory(user_id)
        inv[chosen_item_key] = inv.get(chosen_item_key, 0) + 1
        await ctx.send(f"🎁 Thần linh ban thưởng! **{ctx.author.name}** nhận được **{item['name']}** (đã vào `!inv`)!")

    else:
        await ctx.send(f"💨 Lời cầu nguyện của **{ctx.author.name}** không được phản hồi, không có gì xảy ra...")

# --- LỆNH DÀNH CHO QUẢN TRỊ VIÊN ---

@bot.command()
async def chotien(ctx, member: discord.Member = None, amount: int = None):
    is_owner = ctx.author.id == OWNER_ID
    is_admin = ctx.author.guild_permissions.administrator
    has_mod_role = any(role.name in ALLOWED_ROLES for role in ctx.author.roles)

    if not (is_owner or is_admin or has_mod_role):
        await ctx.send("❌ Bạn không có quyền quản lý để dùng lệnh này!")
        return

    if member is None or amount is None:
        await ctx.send("👉 Cú pháp: `!addmoney @tag_người_nhận <số_tiền>`")
        return

    if amount <= 0:
        await ctx.send("❌ Số tiền cộng phải lớn hơn 0!")
        return

    balances[member.id] = get_balance(member.id) + amount
    await ctx.send(f"✅ Quản lý **{ctx.author.name}** đã cộng **{amount:,}** xu cho **{member.name}**!")
    await check_rich_kid(ctx, member)

# Thay Token bot Discord của bạn vào đây
bot.run("MTUzNzA2MzkxMjEwNzY3OTgzNQ.GL-_o_.EDhs0Iw8s8a2VRKPVLK5h0Rsn_oVZLdzX-aMqU")
