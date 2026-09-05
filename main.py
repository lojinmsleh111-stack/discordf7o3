import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands


# =========================
# Render Port
# =========================

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


threading.Thread(target=run_web_server, daemon=True).start()


# =========================
# Bot Token
# =========================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN غير موجود في Environment Variables")


# =========================
# IDs
# =========================

ACTIVATION_CHANNEL_ID = 1536018619954110555

ACTIVATION_LOG_CHANNEL_ID = 1536166151003054190

ACTIVATION_ROLES = [
    1545033498908299324,
    1536733334795845672
]

ACTIVATION_REMOVE_ROLE = 1536154297916457120


# =========================
# Identity System
# =========================

IDENTITY_FILE = "identity.txt"

identity_lock = asyncio.Lock()


async def get_next_identity():
    """
    يعطي:
    1000
    1001
    1002
    1003
    ...
    """

    async with identity_lock:

        try:
            with open(IDENTITY_FILE, "r", encoding="utf-8") as file:
                identity = int(file.read().strip())

        except (FileNotFoundError, ValueError):
            identity = 1000

        # الرقم القادم
        next_identity = identity + 1

        with open(IDENTITY_FILE, "w", encoding="utf-8") as file:
            file.write(str(next_identity))

        return identity


# =========================
# Intents
# =========================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# Ready
# =========================

@bot.event
async def on_ready():

    print("=" * 40)
    print(f"Bot: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("=" * 40)

    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أوامر سلاش")

    except Exception as e:
        print(f"❌ خطأ في مزامنة أوامر السلاش: {e}")


# =========================
# Activation
# =========================

@bot.event
async def on_message(message):

    # تجاهل البوتات
    if message.author.bot:
        return

    # فقط قناة التفعيل
    if message.channel.id != ACTIVATION_CHANNEL_ID:
        await bot.process_commands(message)
        return

    member = message.author

    # اسم Roblox
    roblox_username = message.content.strip()

    # إذا الرسالة فاضية
    if not roblox_username:
        return

    try:

        # =========================
        # Identity
        # =========================

        identity_number = await get_next_identity()

        # الاسم الجديد
        new_nickname = f"HL | {identity_number} | {roblox_username}"

        # =========================
        # Change Nickname
        # =========================

        try:
            await member.edit(nick=new_nickname)
        except discord.Forbidden:
            print(f"❌ لا أستطيع تغيير اسم {member}")
        except Exception as e:
            print(f"❌ خطأ في تغيير الاسم: {e}")

        # =========================
        # Add Roles
        # =========================

        roles_added = []

        for role_id in ACTIVATION_ROLES:

            role = message.guild.get_role(role_id)

            if role is None:
                print(f"❌ الرتبة غير موجودة: {role_id}")
                continue

            try:
                await member.add_roles(role)

                roles_added.append(role.name)

            except discord.Forbidden:
                print(f"❌ لا أستطيع إعطاء الرتبة: {role.name}")

            except Exception as e:
                print(f"❌ خطأ في إعطاء الرتبة {role.name}: {e}")


        # =========================
        # Remove Old Role
        # =========================

        removed_role_name = None

        old_role = message.guild.get_role(ACTIVATION_REMOVE_ROLE)

        if old_role is not None:

            if old_role in member.roles:

                try:
                    await member.remove_roles(old_role)

                    removed_role_name = old_role.name

                except discord.Forbidden:
                    print(f"❌ لا أستطيع إزالة الرتبة: {old_role.name}")

                except Exception as e:
                    print(f"❌ خطأ في إزالة الرتبة: {e}")


        # =========================
        # DM Member
        # =========================

        try:

            dm_message = (
                "✅ **تم تفعيل حسابك بنجاح!**\n\n"
                f"🪪 **رقم الهوية:** `{identity_number}`\n"
                f"👤 **اسمك الجديد:** `{new_nickname}`\n"
                f"🎮 **Roblox:** `{roblox_username}`"
            )

            await member.send(dm_message)

            print(f"✅ تم إرسال DM إلى {member}")

        except discord.Forbidden:
            print(f"⚠️ لا يمكن إرسال DM إلى {member}")

        except Exception as e:
            print(f"❌ خطأ في إرسال DM: {e}")


        # =========================
        # Activation Log
        # =========================

        try:

            log_channel = bot.get_channel(ACTIVATION_LOG_CHANNEL_ID)

            # إذا لم يجد القناة في الكاش
            if log_channel is None:

                try:
                    log_channel = await bot.fetch_channel(
                        ACTIVATION_LOG_CHANNEL_ID
                    )

                except Exception as e:
                    print(f"❌ لم أستطع الحصول على قناة اللوق: {e}")
                    log_channel = None


            if log_channel is not None:

                embed = discord.Embed(
                    title="✅ تم تفعيل عضو",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )

                embed.add_field(
                    name="👤 العضو",
                    value=f"{member.mention}\n`{member.id}`",
                    inline=False
                )

                embed.add_field(
                    name="🎮 Roblox",
                    value=f"`{roblox_username}`",
                    inline=True
                )

                embed.add_field(
                    name="🪪 رقم الهوية",
                    value=f"`{identity_number}`",
                    inline=True
                )

                embed.add_field(
                    name="📛 الاسم الجديد",
                    value=f"`{new_nickname}`",
                    inline=False
                )

                embed.add_field(
                    name="➕ الرتب المضافة",
                    value=(
                        "\n".join(
                            f"• {role_name}"
                            for role_name in roles_added
                        )
                        if roles_added
                        else "لا يوجد"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="➖ الرتبة المحذوفة",
                    value=(
                        removed_role_name
                        if removed_role_name
                        else "لا يوجد"
                    ),
                    inline=False
                )

                embed.set_thumbnail(
                    url=member.display_avatar.url
                )

                embed.set_footer(
                    text="Activation Logs"
                )

                await log_channel.send(embed=embed)

                print(
                    f"✅ تم إرسال لوق التفعيل إلى "
                    f"#{log_channel.name}"
                )

            else:
                print(
                    f"❌ قناة اللوق غير موجودة: "
                    f"{ACTIVATION_LOG_CHANNEL_ID}"
                )

        except discord.Forbidden:
            print(
                "❌ البوت لا يملك صلاحية إرسال الرسائل "
                "أو Embed Links في قناة اللوق"
            )

        except Exception as e:
            print(
                f"❌ فشل إرسال لوق التفعيل: "
                f"{type(e).__name__}: {e}"
            )


        # =========================
        # Delete ONLY User Message
        # =========================

        try:

            await message.delete()

            print(
                f"🗑️ تم حذف رسالة التفعيل الخاصة بـ {member}"
            )

        except discord.NotFound:
            pass

        except discord.Forbidden:
            print(
                "❌ البوت لا يملك صلاحية حذف الرسائل"
            )

        except Exception as e:
            print(
                f"❌ خطأ في حذف رسالة العضو: {e}"
            )


    except Exception as e:

        print(
            f"❌ خطأ أثناء تفعيل {member}: "
            f"{type(e).__name__}: {e}"
        )


    # معالجة أوامر البريفكس
    await bot.process_commands(message)


# =========================
# /اعطاء_رتب
# =========================

@bot.tree.command(
    name="اعطاء_رتب",
    description="إعطاء عضو حتى 20 رتبة"
)
async def give_roles(
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
        رتبة1,
        رتبة2,
        رتبة3,
        رتبة4,
        رتبة5,
        رتبة6,
        رتبة7,
        رتبة8,
        رتبة9,
        رتبة10,
        رتبة11,
        رتبة12,
        رتبة13,
        رتبة14,
        رتبة15,
        رتبة16,
        رتبة17,
        رتبة18,
        رتبة19,
        رتبة20
    ]

    roles = [role for role in roles if role is not None]

    added = []

    for role in roles:

        if role >= interaction.guild.me.top_role:
            continue

        try:
            await العضو.add_roles(role)
            added.append(role.name)

        except discord.Forbidden:
            continue

        except Exception:
            continue


    if added:

        await interaction.response.send_message(
            f"✅ تم إعطاء {العضو.mention} عدد **{len(added)}** رتبة."
        )

    else:

        await interaction.response.send_message(
            "❌ لم يتم إعطاء أي رتبة."
        )


# =========================
# /ازالة_رتب
# =========================

@bot.tree.command(
    name="ازالة_رتب",
    description="إزالة حتى 20 رتبة من عضو"
)
async def remove_roles(
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
        رتبة1,
        رتبة2,
        رتبة3,
        رتبة4,
        رتبة5,
        رتبة6,
        رتبة7,
        رتبة8,
        رتبة9,
        رتبة10,
        رتبة11,
        رتبة12,
        رتبة13,
        رتبة14,
        رتبة15,
        رتبة16,
        رتبة17,
        رتبة18,
        رتبة19,
        رتبة20
    ]

    roles = [role for role in roles if role is not None]

    removed = []

    for role in roles:

        if role >= interaction.guild.me.top_role:
            continue

        try:
            await العضو.remove_roles(role)
            removed.append(role.name)

        except discord.Forbidden:
            continue

        except Exception:
            continue


    if removed:

        await interaction.response.send_message(
            f"✅ تم إزالة **{len(removed)}** رتبة من {العضو.mention}."
        )

    else:

        await interaction.response.send_message(
            "❌ لم يتم إزالة أي رتبة."
        )


# =========================
# Run Bot
# =========================

print("🚀 Starting bot...")

bot.run(TOKEN)
