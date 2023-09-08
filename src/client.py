from datetime import datetime

import discord

from Constants import CYAN, DELETED_MESSAGES_CHANNEL_ID, GENERAL_CHAT_ID, BOSS_BOT_CHANNEL_ID
from src import GPT
from src.helper_functions import get_general_channel
from src.logging_system import DEBUG, WARNING, log
from src.Read import json_read
from src.Tasks import start_tasks

custom_responses = json_read('responses.json')
birthdays = json_read('birthdays.json')


# noinspection PyMethodMayBeStatic
class MyClient(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.deleted = False
        self.synced = False
        self.old_channel = None

    async def on_ready(self):
        await self.wait_until_ready()
        from src import commands
        tree = commands.get_tree_instance()
        if not self.synced:
            await tree.sync()
            start_tasks()
            self.synced = True
        print('Logged on as', self.user)
        log(f"Logged on as {self.user}", level=DEBUG)

    async def on_member_join(self, member: discord.Member):
        print(member.name, "Katıldı! ")
        log(f"{member.name}, joined {member.guild.name}", level=DEBUG)
        general_channel = get_general_channel(member.guild)
        if general_channel is not None:
            await general_channel.send(
                f"Zeki bir insan valrlığı olan {member.mention} Bu saçmalık {member.guild} serverına katıldı. Hoşgeldin!")

    async def on_member_remove(self, member: discord.Member):
        log(f"{member.name}, left {member.guild.name}", DEBUG)
        channel = get_general_channel(member.guild)
        if isinstance(channel, discord.TextChannel):
            await channel.send("Zeki bir insan valrlığı olan " + "**" + str(member) +
                            "**" + " Bu saçmalık serverdan ayrıldı")
        print(member, "Ayrıldı! ")

    async def on_guild_channel_create(self, channel):
        print(channel, "Oluşturuldu")
        log(f"At {channel.guild.name}, {channel} was created.", DEBUG)

        deleted_messages_channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)
        if isinstance(deleted_messages_channel, discord.TextChannel):
            await deleted_messages_channel.send(
                f"**{channel}** adlı kanal oluşturuldu")

    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        log(f"At {channel.guild.name}, {channel} was deleted.", DEBUG)
        deleted_messages_channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)
        if isinstance(deleted_messages_channel, discord.TextChannel):
            message = await deleted_messages_channel.send(
                f"**{channel}** adlı kanal silindi geri oluşturmak için reaksiyon verin (içindeki yazı kurtarılamıyor, sadece son silinen kanal kurtarılabilir)")
            await message.add_reaction("🔙")
            self.old_channel = channel
            self.deleted = True

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        embed = discord.Embed(title="Biri profilini deiğiştirdi amk.", description=after.mention, color=CYAN)
        
        if before.nick != after.nick:
            log(f"{before.name}'s nickname changed from {before.nick} to {after.nick}", DEBUG)
            embed.add_field(name="Eski Nick:", value=before.nick, inline=False)
            embed.add_field(name="Yeni Nick:", value=after.nick, inline=False)

        if before.avatar != after.avatar:
            log(f"{before.name}'s profile picture changed.", DEBUG)

            if before.avatar is None:
                embed.add_field(name="Eski Profil Fotoğrafı:", value="Yok", inline=False)
            else:
                if after.avatar is None:
                    embed.set_thumbnail(url=before.avatar.url)
                else:
                    embed.add_field(name="Eski Profil Fotoğrafı:", value=before.avatar.url, inline=False)
            if after.avatar is None:
                embed.add_field(name="Yeni Profil Fotoğrafı:", value="Yok", inline=False)
            else:
                embed.set_thumbnail(url=after.avatar.url)

        if before.roles != after.roles:
            log(f"{before.name}'s roles changed.", DEBUG)

        for role in before.roles:
            if role not in after.roles:
                embed.add_field(name="Rol Silindi:", value=role.mention, inline=False)

        for role in after.roles:
            if role not in before.roles:
                embed.add_field(name="Rol Eklendi:", value=role.mention, inline=False)

        if before.status != after.status:
            log(f"{before.name}'s status changed from {before.status} to {after.status}", DEBUG)
            embed.add_field(name="Eski Durum:", value=before.status, inline=False)
            embed.add_field(name="Yeni Durum:", value=after.status, inline=False)

        if before.activity != after.activity:
            log(f"{before.name}'s activity changed from {before.activity} to {after.activity}", DEBUG)
            embed.add_field(name="Eski Aktivite:", value=before.activity, inline=False)
            embed.add_field(name="Yeni Aktivite:", value=after.activity, inline=False)
        
        if before.display_name != after.display_name:
            log(f"{before.name}'s name changed from {before.name} to {after.name}", DEBUG)
            embed.add_field(name="Eski İsim:", value=before.display_name, inline=False)
            embed.add_field(name="Yeni İsim:", value=after.display_name, inline=False)

        if before.discriminator != after.discriminator:
            log(f"{before.name}'s discriminator changed from {before.discriminator} to {after.discriminator}", DEBUG)
            embed.add_field(name="Eski Discriminator:", value=before.discriminator, inline=False)
            embed.add_field(name="Yeni Discriminator:", value=after.discriminator, inline=False)
        
        if before.premium_since != after.premium_since:
            log(f"{before.name}'s boost status changed from {before.premium_since} to {after.premium_since}", DEBUG)
            embed.add_field(name="Eski Boost Durumu:", value=before.premium_since, inline=False)
            embed.add_field(name="Yeni Boost Durumu:", value=after.premium_since, inline=False)
        
        if before.accent_color != after.accent_color:
            log(f"{before.name}'s accent color changed from {before.accent_color} to {after.accent_color}", DEBUG)
            embed.add_field(name="Eski Renk:", value=before.accent_color, inline=False)
            embed.add_field(name="Yeni Renk:", value=after.accent_color, inline=False)

        if before.desktop_status != after.desktop_status:
            log(f"{before.name}'s desktop status changed from {before.desktop_status} to {after.desktop_status}", DEBUG)
            embed.add_field(name="Eski Masaüstü Durumu:", value=before.desktop_status, inline=False)
            embed.add_field(name="Yeni Masaüstü Durumu:", value=after.desktop_status, inline=False)

        if before.mobile_status != after.mobile_status:
            log(f"{before.name}'s mobile status changed from {before.mobile_status} to {after.mobile_status}", DEBUG)
            embed.add_field(name="Eski Mobil Durumu:", value=before.mobile_status, inline=False)
            embed.add_field(name="Yeni Mobil Durumu:", value=after.mobile_status, inline=False)
        
        if before.web_status != after.web_status:
            log(f"{before.name}'s web status changed from {before.web_status} to {after.web_status}", DEBUG)
            embed.add_field(name="Eski Web Durumu:", value=before.web_status, inline=False)
            embed.add_field(name="Yeni Web Durumu:", value=after.web_status, inline=False)
        
        channel = self.get_channel(BOSS_BOT_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel Not Found! Searched id: {BOSS_BOT_CHANNEL_ID}")
        if len(embed.fields) == 0:
            log(f"{before.name}'s profile was updated, but nothing changed, we probably missed something.", WARNING)
            return
        await channel.send(embed=embed)

    async def on_member_ban(self, guild: discord.Guild, user: discord.Member):
        channel = get_general_channel(guild)
        log(f"{user.name} was banned from {guild.name}", DEBUG)
        if isinstance(channel, discord.TextChannel):
            await channel.send("Ah Lan " + str(user) + " Adlı kişi " + str(guild) +
                                " serverından banlandı ")
            return
        raise ValueError(f"Kanal Bulunamadı: aranan id: {GENERAL_CHAT_ID}")

    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        log(f"{user.name} was unbanned from {guild.name}", DEBUG)
        channel = self.get_channel(GENERAL_CHAT_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(
                f"{user.name} bu mal gibi {guild.name} sunucusuna geri girebilme hakkı kazanmılştır"
            )
        text_channel = guild.text_channels[0]  # type: ignore  # why tf is this warning me that i can't get[0] of a list
        invite = await text_channel.create_invite(target_user=user,
                                                            reason="Ban kaldırıldı, sunucuya geri davet ediliyor", max_uses=1)
        try:
            await user.send(f"artık {guild.name} sunucusuna geri girebilirsin. giriş linkin: {invite}")
        except discord.Forbidden:
            log(f"Couldn't send message to {user.name}")
        channel = self.get_channel(GENERAL_CHAT_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(
                f"{user.name} bu mal gibi {guild.name} sunucusuna geri girebilme hakkı kazanmılştır"
                )

    async def on_message_edit(self, before, message):
        if message.author == self.user:
            return
        if before.content == message.content:
            return

        embed = discord.Embed(title="Mesaj Düzenlendi", description="Biri Mesajını Düzenlendi", color=CYAN)

        embed.add_field(name="Kanal: ", value=message.channel, inline=False)
        embed.add_field(name="Kişi: ", value=message.author, inline=False)
        embed.add_field(name="Eski Mesaj: ", value=before.content, inline=False)
        embed.add_field(name="Yeni Mesaj: ", value=message.content, inline=False)

        channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(embed=embed)

    async def on_message_delete(self, message: discord.Message):
        if message.author == self.user:
            return

        channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)

        if message.guild is not None:
            async for entry in message.guild.audit_logs(
                action=discord.AuditLogAction.message_delete, limit=10):
                print(f'{entry.user} deleted {entry.target} at {entry.created_at}')
                who_deleted = entry.user
                break
            else:
                who_deleted = None
        else:
            who_deleted = None
        embed = discord.Embed(
        title="Mesaj silindi.", description="Silinen Mesaj: " + str(message.content),
        color=CYAN)

        embed.add_field(name="Silinen kanal:", value=message.channel, inline=False)
        embed.add_field(name="Gönderen kişi:", value=message.author, inline=False)

        if who_deleted is not None:
            embed.add_field(name="Silen kişi:", value=who_deleted, inline=False)

        if message.attachments is not None:
            if len(message.attachments) == 1:
                embed.set_image(url=message.attachments[0].url)
            else:
                for attachment in message.attachments:
                    embed.add_field(name="Eklentiler:", value=attachment.url, inline=False)
        if message.embeds is not None:
            embeds2 = message.embeds
        else:
            embeds2 = None
        if isinstance(channel, discord.TextChannel) and embeds2 is not None:
            await channel.send(embeds=embeds2)

    async def on_message(self, message: discord.Message):
        message_content = message.content
        message_content_lower = message_content.lower()
        user = message.author
        channel = message.channel
        guild = message.guild

        time = datetime.now().strftime("%H:%M:")
        if guild is None:
            guild = "DM"
        data = f'{str(time)} {str(guild)} {str(channel)} {str(user.name)}: {str(message_content)}'
        print(data)
        if message.embeds is None:
            log(data)

        if message.author == self.user:
            return

        if custom_responses.get(message_content) is not None:
            await message.reply(custom_responses[message.content])

        if isinstance(channel, discord.DMChannel) or message.guild is None:
            answer = GPT.question("You are talking on a dm channel!" + message_content, message.author.name)
            if answer != -1:
                await message.reply("Botta bir hata oluştu, Lütfen tekrar dene!")
                return
            await message.reply(str(answer))
            return

        if time == "06:11:":  # 9:11 for +3 timezone
            await channel.send("🛫🛬💥🏢🏢")

        son_mesaj = message.content.lower().split(" ")[-1]
        if son_mesaj == "nerde" or son_mesaj == "nerede" or son_mesaj == (
        "neredesin") or son_mesaj == "nerdesin":
            print(son_mesaj)
            await message.reply(
                f'Ebenin amında. Ben sonu "{son_mesaj}" diye biten bütün mesajlara cevap vermek için kodlanmış bi botum. Seni kırdıysam özür dilerim.'
            )

        if 'tuna' in message_content_lower:
            await message.channel.send("<@725318387198197861>")  # tuna tag

        if 'kaya' in message_content_lower:
            await message.reply("Zeka Kübü <@474944711358939170>")  # kaya tag

        if message_content_lower == "ping":
            await message.reply(f"PONG, ping: {round(self.latency * 1000)}ms")

        if message_content_lower == "katıl":
            if not isinstance(user, discord.Member) or guild == "DM":
                await message.reply("bu komut sadece sunucukarda kullanılabilir.")
                return
            if user.voice is None:
                await message.reply("herhangi bir ses kanalında değilsin!")
                return
            kanal = user.voice.channel
            if kanal is not None:
                print(kanal.mention + "a katılınıyor")
                await kanal.connect()
            else:
                print("Kanal bulunamadı")

        if message_content_lower == "söyle":
            if len(message.content.split(" ")) > 1:
                await message.channel.send(" ".join(message.content.split(" ")[1:]))
            else:
                await message.reply("Ne söyleyeyim?")


client = MyClient()


def get_client_instance():
    return client


def get_custom_responses():
    return custom_responses


def get_birthdays():
    return birthdays
