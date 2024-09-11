import logging

import discord
from discord import app_commands


# noinspection PyMethodMayBeStatic
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.deleted = False
        self.synced = False
        self.old_channel = None
        self._tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await self._tree.sync()
            self.synced = True
        logging.info("Logged on as %s", self.user)

    @property
    def tree(self):
        return self._tree

client = MyClient()


def get_client_instance():
    return client
