import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands
from discord import app_commands


# ==========================================
# Render Port
# ==========================================

PORT = int(os.getenv("PORT", "10000"))


class HealthCheck(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        return


def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheck)
    print(f"Web server running on port {PORT}")
    server.serve_forever()


threading.Thread(
    target=run_web_server,
    daemon=True
).start()


# ==========================================
# Token
# ==========================================

TOKEN = os.getenv("BOT_TOKEN")


# ==========================================
# إعدادات التفعيل
# ==========================================

ACTIVATION_CHANNEL_ID = 1536018619954110555

# الرتب التي يحصل عليها العضو عند التفعيل
ACTIVATION_ROLES = [
    1545033498908299324,
    1536733334795845672
]

# الرتبة التي تنشال عند التفعيل
ACTIVATION_REMOVE_ROLE = 1536154297916457120


# ==========================================
# نظام الهويات
# ==========================================

IDENTITY_FILE = "identity.txt"


def get_next_identity():

    # أول هوية = 1000
    if not os.path.exists(IDENTITY_FILE):

        current_identity = 1000

        with open(IDENTITY_FILE, "w") as file:
            file.write("1001")

        return current_identity

    try:

        with open(IDENTITY_FILE, "r") as file:
            current_identity = int(file.read().strip())

    except:

        current_identity = 1000

    # حفظ الرقم التالي
    with open(IDENTITY_FILE, "w") as file:
        file.write(str(current_identity + 1))

    return current_identity


# ==========================================
# إعداد Discord
# ==========================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# Bot Ready
# ==========================================

@bot.event
async def on_ready():

    print("--------------------------------")
    print(f"Bot: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("--------------------------------")

    try:

        synced = await bot.tree.sync()

        print(
            f"تم مزامنة {len(synced)} أوامر سلاش"
        )

    except Exception as e:

        print(
            f"خطأ في مزامنة أوامر السلاش: {e}"
        )


# ==========================================
# نظام التفعيل
# ==========================================

@bot.event
async def on_message(message):

    # تجاهل البوتات
    if message.author.bot:
        return

    # ======================================
    # لا يعمل إلا داخل روم التفعيل
    # ======================================

    if message.channel.id != ACTIVATION_CHANNEL_ID:

        await bot.process_commands(message)

        return

    # ======================================
    # اسم Roblox
    # ======================================

    roblox_username = message.content.strip()

    # إذا الرسالة فارغة
    if not roblox_username:

        return

    member = message.author


    # ======================================
    # إعطاء رقم الهوية
    # ======================================

    identity_number = get_next_identity()


    # ======================================
    # الاسم الجديد
    #
    # HL | هويه | user
    # مثال:
    # HL | 1000 | RobloxUser
    # ======================================

    new_nickname = (
        f"HL | {identity_number} | {roblox_username}"
    )


    # ======================================
    # تغيير اسم العضو
    # ======================================

    try:

        await member.edit(
            nick=new_nickname
        )

    except discord.Forbidden:

        print(
            f"لا أستطيع تغيير اسم: {member}"
        )


    # ======================================
    # إعطاء الرتب
    # ======================================

    for role_id in ACTIVATION_ROLES:

        role = message.guild.get_role(role_id)

        if role is None:

            print(
                f"الرتبة غير موجودة: {role_id}"
            )

            continue

        try:

            await member.add_roles(role)

        except discord.Forbidden:

            print(
                f"لا أستطيع إعطاء الرتبة: {role_id}"
            )


    # ======================================
    # إزالة الرتبة القديمة
    # ======================================

    old_role = message.guild.get_role(
        ACTIVATION_REMOVE_ROLE
    )

    if old_role is not None:

        try:

            await member.remove_roles(
                old_role
            )

        except discord.Forbidden:

            print(
                f"لا أستطيع إزالة الرتبة: "
                f"{ACTIVATION_REMOVE_ROLE}"
            )


    # ======================================
    # إرسال رسالة خاصة للعضو
    # ======================================

    try:

        await member.send(
            "✅ **تم تفعيل حسابك بنجاح!**\n\n"
            f"🪪 **رقم الهوية:** `{identity_number}`\n"
            f"👤 **اسمك الجديد:** `{new_nickname}`"
        )

    except discord.Forbidden:

        print(
            f"لا أستطيع إرسال خاص إلى: {member}"
        )


    # ======================================
    # حذف رسالة العضو الحالية فقط
    #
    # مهم:
    # لا يوجد purge
    # لا يوجد حذف رسائل أخرى
    # ======================================

    try:

        await message.delete()

    except discord.NotFound:

        pass

    except discord.Forbidden:

        print(
            "البوت لا يملك صلاحية حذف الرسائل"
        )


    # ======================================
    # معالجة أوامر البوت
    # ======================================

    await bot.process_commands(message)


# ==========================================
# /اعطاء_رتب
# حتى 20 رتبة
# ==========================================

@bot.tree.command(
    name="اعطاء_رتب",
    description="إعطاء عضو حتى 20 رتبة"
)
@app_commands.describe(
    العضو="العضو الذي تريد إعطاءه الرتب",
    رتبة1="الرتبة الأولى",
    رتبة2="الرتبة الثانية",
    رتبة3="الرتبة الثالثة",
    رتبة4="الرتبة الرابعة",
    رتبة5="الرتبة الخامسة",
    رتبة6="الرتبة السادسة",
    رتبة7="الرتبة السابعة",
    رتبة8="الرتبة الثامنة",
    رتبة9="الرتبة التاسعة",
    رتبة10="الرتبة العاشرة",
    رتبة11="الرتبة 11",
    رتبة12="الرتبة 12",
    رتبة13="الرتبة 13",
    رتبة14="الرتبة 14",
    رتبة15="الرتبة 15",
    رتبة16="الرتبة 16",
    رتبة17="الرتبة 17",
    رتبة18="الرتبة 18",
    رتبة19="الرتبة 19",
    رتبة20="الرتبة 20"
)
async def اعطاء_رتب(
    interaction: discord.Interaction,
    العضو: discord.Member,
    رتبة1: discord.Role = None,
    رتبة2: discord.Role = None,
    رتبة3: discord.Role = None,
    رتبة4: discord.Role = None,
    رتبة5: discord.Role = None,
    رتبة6: discord.Role = None,
    رتبة7: discord.Role = None,
    رتبة8: discord.Role = None,
    رتبة9: discord.Role = None,
    رتبة10: discord.Role = None,
    رتبة11: discord.Role = None,
    رتبة12: discord.Role = None,
    رتبة13: discord.Role = None,
    رتبة14: discord.Role = None,
    رتبة15: discord.Role = None,
    رتبة16: discord.Role = None,
    رتبة17: discord.Role = None,
    رتبة18: discord.Role = None,
    رتبة19: discord.Role = None,
    رتبة20: discord.Role = None
):

    roles = [
        رتبة1, رتبة2, رتبة3, رتبة4, رتبة5,
        رتبة6, رتبة7, رتبة8, رتبة9, رتبة10,
        رتبة11, رتبة12, رتبة13, رتبة14, رتبة15,
        رتبة16, رتبة17, رتبة18, رتبة19, رتبة20
    ]

    roles = [
        role for role in roles
        if role is not None
    ]

    if not roles:

        await interaction.response.send_message(
            "❌ اختر رتبة واحدة على الأقل.",
            ephemeral=True
        )

        return

    added = 0

    for role in roles:

        # البوت لا يستطيع إدارة رتبة
        # أعلى أو مساوية لرتبته
        if role >= interaction.guild.me.top_role:

            continue

        try:

            await العضو.add_roles(role)

            added += 1

        except discord.Forbidden:

            continue

    await interaction.response.send_message(
        f"✅ تم إعطاء {العضو.mention} "
        f"**{added}** رتبة."
    )


# ==========================================
# /ازالة_رتب
# حتى 20 رتبة
# ==========================================

@bot.tree.command(
    name="ازالة_رتب",
    description="إزالة حتى 20 رتبة من عضو"
)
@app_commands.describe(
    العضو="العضو الذي تريد إزالة الرتب منه",
    رتبة1="الرتبة الأولى",
    رتبة2="الرتبة الثانية",
    رتبة3="الرتبة الثالثة",
    رتبة4="الرتبة الرابعة",
    رتبة5="الرتبة الخامسة",
    رتبة6="الرتبة السادسة",
    رتبة7="الرتبة السابعة",
    رتبة8="الرتبة الثامنة",
    رتبة9="الرتبة التاسعة",
    رتبة10="الرتبة العاشرة",
    رتبة11="الرتبة 11",
    رتبة12="الرتبة 12",
    رتبة13="الرتبة 13",
    رتبة14="الرتبة 14",
    رتبة15="الرتبة 15",
    رتبة16="الرتبة 16",
    رتبة17="الرتبة 17",
    رتبة18="الرتبة 18",
    رتبة19="الرتبة 19",
    رتبة20="الرتبة 20"
)
async def ازالة_رتب(
    interaction: discord.Interaction,
    العضو: discord.Member,
    رتبة1: discord.Role = None,
    رتبة2: discord.Role = None,
    رتبة3: discord.Role = None,
    رتبة4: discord.Role = None,
    رتبة5: discord.Role = None,
    رتبة6: discord.Role = None,
    رتبة7: discord.Role = None,
    رتبة8: discord.Role = None,
    رتبة9: discord.Role = None,
    رتبة10: discord.Role = None,
    رتبة11: discord.Role = None,
    رتبة12: discord.Role = None,
    رتبة13: discord.Role = None,
    رتبة14: discord.Role = None,
    رتبة15: discord.Role = None,
    رتبة16: discord.Role = None,
    رتبة17: discord.Role = None,
    رتبة18: discord.Role = None,
    رتبة19: discord.Role = None,
    رتبة20: discord.Role = None
):

    roles = [
        رتبة1, رتبة2, رتبة3, رتبة4, رتبة5,
        رتبة6, رتبة7, رتبة8, رتبة9, رتبة10,
        رتبة11, رتبة12, رتبة13, رتبة14, رتبة15,
        رتبة16, رتبة17, رتبة18, رتبة19, رتبة20
    ]

    roles = [
        role for role in roles
        if role is not None
    ]

    if not roles:

        await interaction.response.send_message(
            "❌ اختر رتبة واحدة على الأقل.",
            ephemeral=True
        )

        return

    removed = 0

    for role in roles:

        if role >= interaction.guild.me.top_role:

            continue

        try:

            await العضو.remove_roles(role)

            removed += 1

        except discord.Forbidden:

            continue

    await interaction.response.send_message(
        f"✅ تم إزالة **{removed}** رتبة "
        f"من {العضو.mention}."
    )


# ==========================================
# تشغيل البوت
# ==========================================

if not TOKEN:

    raise RuntimeError(
        "BOT_TOKEN غير موجود في Environment Variables"
    )


bot.run(TOKEN)
