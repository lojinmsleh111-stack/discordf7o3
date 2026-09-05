import os
import discord
from discord.ext import commands
from discord import app_commands


# ==========================================
# الإعدادات
# ==========================================

TOKEN = os.getenv("BOT_TOKEN")

ACTIVATION_CHANNEL_ID = 1536018619954110555

# الرتب التي يعطيها التفعيل تلقائياً
ACTIVATION_ROLES = [
    1545033498908299324,
    1536733334795845672
]

# الرتبة التي تزال عند التفعيل
ACTIVATION_REMOVE_ROLE = 1536154297916457120


# ==========================================
# إعداد البوت
# ==========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# عند تشغيل البوت
# ==========================================

@bot.event
async def on_ready():

    print(f"تم تشغيل البوت: {bot.user}")
    print(f"ID: {bot.user.id}")

    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} أمر سلاش")
    except Exception as e:
        print(f"خطأ في مزامنة الأوامر: {e}")


# ==========================================
# نظام التفعيل
# ==========================================

@bot.event
async def on_message(message):

    # تجاهل رسائل البوتات
    if message.author.bot:
        return

    # لا يعمل إلا في روم التفعيل
    if message.channel.id != ACTIVATION_CHANNEL_ID:
        await bot.process_commands(message)
        return

    member = message.author

    # اسم حساب Roblox
    roblox_username = message.content.strip()

    # تجاهل الرسائل الفارغة
    if not roblox_username:
        return

    # ======================================
    # إعطاء رتب التفعيل
    # ======================================

    for role_id in ACTIVATION_ROLES:

        role = message.guild.get_role(role_id)

        if role is None:
            print(f"الرتبة غير موجودة: {role_id}")
            continue

        try:
            await member.add_roles(role)
        except discord.Forbidden:
            print(f"لا أستطيع إعطاء الرتبة: {role_id}")

    # ======================================
    # إزالة رتبة التفعيل القديمة
    # ======================================

    old_role = message.guild.get_role(ACTIVATION_REMOVE_ROLE)

    if old_role is not None:

        try:
            await member.remove_roles(old_role)
        except discord.Forbidden:
            print(f"لا أستطيع إزالة الرتبة: {ACTIVATION_REMOVE_ROLE}")

    # ======================================
    # تغيير اسم العضو
    # ======================================

    new_nickname = f"HL | {roblox_username} | هويه"

    try:
        await member.edit(nick=new_nickname)
    except discord.Forbidden:
        print(f"لا أستطيع تغيير اسم العضو: {member}")

    # ======================================
    # حذف رسالة العضو فقط
    # ======================================

    try:
        await message.delete()
    except discord.NotFound:
        pass
    except discord.Forbidden:
        print("البوت لا يملك صلاحية حذف الرسائل")

    await bot.process_commands(message)


# ==========================================
# /اعطاء_رتب
# يعطي حتى 20 رتبة
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

    roles = [role for role in roles if role is not None]

    if not roles:
        await interaction.response.send_message(
            "❌ يجب اختيار رتبة واحدة على الأقل.",
            ephemeral=True
        )
        return

    added = []
    failed = []

    for role in roles:

        # البوت لا يستطيع إدارة رتبة مساوية أو أعلى من رتبته
        if role >= interaction.guild.me.top_role:
            failed.append(role.name)
            continue

        try:
            await العضو.add_roles(role)
            added.append(role.name)

        except discord.Forbidden:
            failed.append(role.name)

    text = f"✅ تم إعطاء {العضو.mention} عدد **{len(added)}** رتبة."

    if failed:
        text += f"\n⚠️ تعذر إعطاء **{len(failed)}** رتبة بسبب صلاحيات البوت."

    await interaction.response.send_message(text)


# ==========================================
# /ازالة_رتب
# يشيل حتى 20 رتبة
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

    roles = [role for role in roles if role is not None]

    if not roles:
        await interaction.response.send_message(
            "❌ يجب اختيار رتبة واحدة على الأقل.",
            ephemeral=True
        )
        return

    removed = []
    failed = []

    for role in roles:

        # البوت لا يستطيع إدارة رتبة مساوية أو أعلى من رتبته
        if role >= interaction.guild.me.top_role:
            failed.append(role.name)
            continue

        try:
            await العضو.remove_roles(role)
            removed.append(role.name)

        except discord.Forbidden:
            failed.append(role.name)

    text = f"✅ تم إزالة **{len(removed)}** رتبة من {العضو.mention}."

    if failed:
        text += f"\n⚠️ تعذر إزالة **{len(failed)}** رتبة بسبب صلاحيات البوت."

    await interaction.response.send_message(text)


# ==========================================
# تشغيل البوت
# ==========================================

if not TOKEN:
    raise RuntimeError(
        "لم يتم العثور على BOT_TOKEN في Environment Variables"
    )

bot.run(TOKEN)
