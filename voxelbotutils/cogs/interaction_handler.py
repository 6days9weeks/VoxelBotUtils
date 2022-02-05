import io

import discord
from discord.ext import commands

from . import utils as vbu


class InteractionHandler(vbu.Cog, command_attrs={"hidden": False, "add_slash_command": False}):
    @vbu.Cog.listener()
    async def on_component_interaction(self, interaction: discord.Interaction):
        if not interaction.component.custom_id.startswith("RUNCOMMAND"):
            return
        command_name = interaction.component.custom_id[len("RUNCOMMAND ") :]
        command = self.bot.get_command(command_name)
        ctx = await self.bot.get_slash_context(interaction=interaction)
        ctx.invoked_with = command_name
        ctx.command = command
        if self.bot.blacklisted_users.get(int(interaction.user.id), None) is not None:
            await ctx.interaction.response.send_message(
                "You are blacklisted from using this bot.", ephemeral=True
            )
            return
        await self.bot.invoke(ctx)

    @vbu.command(aliases=["addslashcommands", "addslashcommand", "addapplicationcommand"])
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addapplicationcommands(self, ctx, guild_id: int = None, *commands: str):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        guild = guild_id if guild_id is None else discord.Object(guild_id)
        added_commands = await self.bot.register_application_commands(guild=guild)
        output_strings = "\n".join([f"\N{BULLET} `{i!r}`" for i in added_commands])
        output = f"Added **{len(added_commands)}** slash commands:\n{output_strings}\n"
        file = None
        if len(output) >= 2000:
            file = discord.File(io.StringIO(output_strings), filename="CommandsAdded.txt")
            output = f"Added **{len(added_commands)}** slash commands."
        await ctx.send(output, file=file)

    @vbu.command(
        aliases=[
            "removeslashcommands",
            "removeslashcommand",
            "removeapplicationcommand",
        ]
    )
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def removeapplicationcommands(self, ctx, guild_id: int = None, *commands: str):
        """
        Removes the bot's interaction commands from the global interaction handler.
        """

        guild = guild_id if guild_id is None else discord.Object(guild_id)
        await self.bot.register_application_commands(commands=None, guild=guild)
        await vbu.embeddify(ctx, "Removed slash commands.")


def setup(bot: vbu.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
