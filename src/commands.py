import logging
from typing import Optional

import discord
from discord import app_commands

from src import client
from src.download_commands import download_video_command

discord_client = client.get_client_instance()

tree = discord_client.tree


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.context_menu(name="download-video")
async def download_video_link(
    interaction: discord.Interaction, message: discord.Message
):
    content = message.content
    await download_video_command(interaction, content)


@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.context_menu(name="secretly-download-video")
async def download_video_link_hidden(
    interaction: discord.Interaction, message: discord.Message
):
    content = message.content
    await download_video_command(interaction, content, is_ephemeral=True)


@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@tree.command(
    name="ping",
    description="shows the latency of the bot, useful for checking if the bot is online",
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Pong: {round(discord_client.latency * 1000)}ms",
        ephemeral=True,
    )


@tree.command(name="download-video", description="downloads a video from a link")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def download_video(
    interaction: discord.Interaction, url: str, include_title: Optional[bool] = None
):
    await download_video_command(interaction, url, include_title=include_title)

def setup_commands():
    logging.debug("Setting up commands")
    # we don't actually need to do anything here, the decorators do all the work
    # but this function is still needed to be called in main.py, since it will import this file
