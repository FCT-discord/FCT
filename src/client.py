import logging
import os
from datetime import UTC, datetime, timedelta

import discord
import requests

from Constants import (BOSS_BOT_CHANNEL_ID, CYAN, DELETED_MESSAGES_CHANNEL_ID,
                       GENERAL_CHAT_ID)
from src import GPT
from src.Helpers.helper_functions import DiskDict, get_general_channel
from src.Tasks import start_tasks

custom_responses = DiskDict('responses.json')
birthdays = DiskDict("birthdays.json")


# noinspection PyMethodMayBeStatic
class MyClient(discord.Client):

    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.deleted = False
        self.synced = False
        self.old_channel = None

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            import src.commands as commands  # pylint: disable=import-outside-toplevel # to avoid circular imports
            tree = commands.get_tree_instance()
            await tree.sync()
            start_tasks()
            self.synced = True
        logging.info("Logged on as %s", self.user)

    async def on_member_join(self, member: discord.Member):
        logging.debug("%s, joined %s",member.name, member.guild.name)
        general_channel = get_general_channel(member.guild)
        if general_channel is not None:
            await general_channel.send(
                f"Zeki bir insan valrlığı olan {member.mention} Bu saçmalık {member.guild} serverına katıldı. Hoşgeldin!")

    async def on_member_remove(self, member: discord.Member):
        logging.debug("%s, left %s", member.name, member.guild.name)
        channel = get_general_channel(member.guild)
        if isinstance(channel, discord.TextChannel):
            await channel.send("Zeki bir insan valrlığı olan " + "**" + str(member) +
                               "**" + " Bu saçmalık serverdan ayrıldı")

    async def on_guild_channel_create(self, channel):
        logging.debug("At %s, %s was created.",channel.guild.name, channel)

        deleted_messages_channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)
        if isinstance(deleted_messages_channel, discord.TextChannel):
            await deleted_messages_channel.send(
                f"**{channel}** adlı kanal oluşturuldu")

    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        logging.debug("At %s, %s was deleted.", channel.guild.name, channel)
        deleted_messages_channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)
        if isinstance(deleted_messages_channel, discord.TextChannel):
            message = await deleted_messages_channel.send(
                f"**{channel}** adlı kanal silindi geri oluşturmak için reaksiyon verin (içindeki yazı kurtarılamıyor, sadece son silinen kanal kurtarılabilir)")
            await message.add_reaction("🔙")
            self.old_channel = channel
            self.deleted = True

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        embed = discord.Embed(title=f"{after.mention} adlı kişi profilini değiştirdi", color=CYAN)
        avatar = after.avatar if after.avatar is not None else after.default_avatar
        embed.set_thumbnail(url=avatar.url)

        await member_handlers.handle_profile_change(before,after, embed)

        channel = self.get_channel(BOSS_BOT_CHANNEL_ID)
        if not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel Not Found! Searched id: {BOSS_BOT_CHANNEL_ID}")
        if len(embed.fields) == 0:
            logging.warning(f"{before.name}'s profile was updated, but nothing changed, we probably missed something.")
            return
        await channel.send(embed=embed)

    async def on_member_ban(self, guild: discord.Guild, user: discord.Member):
        channel = get_general_channel(guild)
        logging.debug(f"{user.name} was banned from {guild.name}")
        if isinstance(channel, discord.TextChannel):
            await channel.send("Ah Lan " + str(user) + " Adlı kişi " + str(guild) +
                               " serverından banlandı ")
            return
        raise ValueError(f"Kanal Bulunamadı: aranan id: {GENERAL_CHAT_ID}")

    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        logging.debug(f"{user.name} was unbanned from {guild.name}")
        embed = discord.Embed(title=f"{user.name} bu mal gibi sunucuya geri girme hakkı kazandı", color=CYAN)
        channel = self.get_channel(GENERAL_CHAT_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(
                f"{user.name} bu mal gibi {guild.name} sunucusuna geri girebilme hakkı kazanmılştır"
            )
        text_channel = guild.text_channels[0]
        invite = await text_channel.create_invite(reason="Ban kaldırıldı, sunucuya geri davet ediliyor", max_uses=1)
        try:
            await user.send(f"Artık {guild.name} sunucusuna geri girebilirsin! işte giriş linkin: {invite}")
            embed.description = "Davet linki kişiye gönderildi"
        except discord.Forbidden:
            logging.info(f"Couldn't send message to {user.name}")
            embed.description = "Davet linki kişiye gönderilemedi, lütfen gönderin"
        channel = self.get_channel(GENERAL_CHAT_ID)
        if isinstance(channel, discord.TextChannel):
            await channel.send(embed=embed)

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

        send_channel = self.get_channel(DELETED_MESSAGES_CHANNEL_ID)

        if not isinstance(send_channel, discord.TextChannel):
            logging.critical("Text Channel Not Found! Searched id: %d",DELETED_MESSAGES_CHANNEL_ID)
            return

        if message.guild is not None:
            async for entry in message.guild.audit_logs(action=discord.AuditLogAction.message_delete, after=datetime.now(UTC) - timedelta(minutes=2)):
                logging.debug(f'{entry.user} deleted {entry.target} at {entry.created_at}')
                who_deleted = entry.user
                if who_deleted is None:
                    continue
                break
            else:
                # if it isn't in the audit log, it was probably deleted by the user
                who_deleted = message.author
        else:
            who_deleted = message.author
        embed = discord.Embed(
            title="Mesaj silindi.", description=f"Silinen Mesaj: {message.content} ",
            color=CYAN)

        embed.add_field(name="Silinen kanal:", value=message.channel, inline=False)
        embed.add_field(name="Gönderen kişi:", value=message.author, inline=False)

        if who_deleted is not None:
            embed.add_field(name="Silen kişi:", value=who_deleted, inline=False)

        if message.attachments is not None:
            files = []
            #downlad the attachment and reupload it
            for attachment in message.attachments:
                file_name = attachment.filename
                file_path = os.path.join("downloads", "attachments", file_name)
                try:
                    file_data = requests.get(attachment.url, timeout=5).content
                except requests.exceptions.RequestException:
                    logging.error("Couldn't download attachment %s", attachment.url)
                    continue
                with open(file_path, "wb") as file:
                    file.write(file_data)
                files.append(discord.File(file_path, filename=file_name, spoiler=attachment.is_spoiler()))
                
                if len(message.attachments) == 1:
                    embed.set_image(url="attachment://" + file_name)
                else:
                    embed.add_field(name="Eklentiler:", value="attachment://" + file_name, inline=False)
        
        await send_channel.send(embeds=[embed] + message.embeds, files=files)

    async def on_message(self, message: discord.Message):
        message_content = message.content
        message_content_lower = message_content.lower()
        user = message.author
        channel = message.channel
        guild = message.guild

        time = datetime.now().strftime("%H:%M:")
        if guild is None:
            guild = "DM"
        data = f'{str(guild)} {str(channel)} / {str(user.name)}: {str(message_content)}'
        logging.getLogger("chat").debug(data)

        if message.author == self.user:
            return

        if custom_responses.get(message_content) is not None:
            await message.reply(custom_responses[message.content])

        if isinstance(channel, discord.DMChannel) or message.guild is None:
            async with channel.typing():
                await self.on_dm(message)
            return

        if time == "06:11:":  # 9:11 for +3 timezone
            await channel.send("🛫🛬💥🏢🏢")

        son_mesaj = message.content.lower().split(" ")[-1]
        if son_mesaj == "nerde" or son_mesaj == "nerede" or son_mesaj == "neredesin" or son_mesaj == "nerdesin":
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
                logging.debug(f"Joining {kanal.name}")
                await kanal.connect()
            else:
                logging.debug("User is not in a voice channel.")
                await message.reply("herhangi bir ses kanalında değilsin!")

        if message_content_lower == "söyle":
            if len(message.content.split(" ")) > 1:
                await message.channel.send(" ".join(message.content.split(" ")[1:]))
            else:
                await message.reply("Ne söyleyeyim?")

    @staticmethod
    async def on_dm(message: discord.Message):
        if not isinstance(message.channel, discord.DMChannel):
            raise ValueError("This function is only for DMs")
        answer = GPT.chat(message.content, (await GPT.create_message_history(message.channel, limit=8)))
        await message.reply(str(answer)) # not using an embed because it's easier to parse history this way.


client = MyClient()


def get_client_instance():
    return client


def get_custom_responses():
    return custom_responses


def get_birthdays():
    return birthdays
