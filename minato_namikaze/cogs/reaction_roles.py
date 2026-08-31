from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from minato_namikaze.lib import Embed
from minato_namikaze.lib import has_permissions
from minato_namikaze.lib import LinksAndVars
from minato_namikaze.lib.database.config_api import Config

log = logging.getLogger(__name__)


class RoleButton(discord.ui.Button):
    def __init__(self, emoji, role_id, view_data):
        self.role_id = role_id
        self.limit_to_one = view_data.get("limit_to_one", False)
        self.all_roles = list(view_data.get("reactions", {}).values())

        super().__init__(
            emoji=emoji,
            style=discord.ButtonStyle.primary,
            custom_id=f"rr_{view_data['message_id']}_{role_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message(
                "Role not found.",
                ephemeral=True,
            )

        if self.limit_to_one:
            roles_to_remove = [
                interaction.guild.get_role(r)
                for r in self.all_roles
                if r != self.role_id and interaction.guild.get_role(r) and interaction.guild.get_role(r) in interaction.user.roles
            ]
            if roles_to_remove:
                try:
                    await interaction.user.remove_roles(*roles_to_remove)
                except discord.Forbidden:
                    pass

        try:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"Removed {role.name}!",
                    ephemeral=True,
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Added {role.name}!",
                    ephemeral=True,
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permissions to manage that role.",
                ephemeral=True,
            )


class PersistentRoleView(discord.ui.View):
    def __init__(self, data: dict):
        super().__init__(timeout=None)
        self.data = data
        for emoji, role_id in data.get("reactions", {}).items():
            self.add_item(RoleButton(emoji=emoji, role_id=role_id, view_data=data))


class ReactionRoles(commands.Cog, name="Reaction Roles"):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Setup some reaction roles using persistent buttons"
        self.config = Config("ReactionRoles", "views")

    async def cog_load(self):
        views = await self.config.global_().get_attr("views", {})
        for message_id_str, data in views.items():
            try:
                self.bot.add_view(
                    PersistentRoleView(data=data),
                    message_id=int(message_id_str),
                )
            except Exception as e:
                log.error(f"Failed to load view for {message_id_str}: {e}")
        log.info("Reaction roles persistent views added.")

    @staticmethod
    async def delete_messages(list_delete: list[discord.Message]) -> tuple[list, list]:
        for message in list_delete:
            try:
                await message.delete()
            except:
                pass
        return [], []

    @commands.group(aliases=["rr"], invoke_without_command=True)
    @has_permissions(manage_roles=True)
    async def reactionroles(self, ctx: commands.Context):
        """Reaction Roles Base Command"""
        await ctx.send_help(ctx.command)

    @reactionroles.command(aliases=["make", "setup"])
    @has_permissions(manage_roles=True)
    async def new(self, ctx: commands.Context):
        """Create a new reaction role using interactive setup."""
        if not await ctx.prompt(
            "Welcome to the Reaction Light creation program. Proceed?",
            author_id=ctx.author.id,
        ):
            return

        user_messages = []
        error_messages = []

        sent_reactions_message = await ctx.send(
            "Attach roles and emojis separated by one space (one combination per message). When done type `done`. Example:\n:smile: `@Role`",
        )
        user_messages.append(sent_reactions_message)

        reactions = {}

        def check(message):
            return message.author.id == ctx.message.author.id and message.content != ""

        n = 0
        while True:
            if n > 15:
                break
            try:
                msg = await self.bot.wait_for("message", timeout=120, check=check)
                user_messages.append(msg)

                if msg.content.lower() == "done":
                    break

                parts = msg.content.split()
                if not parts:
                    continue

                reaction = parts[0]
                try:
                    role = msg.role_mentions[0].id
                except IndexError:
                    error_messages.append(
                        await ctx.send("Mention a role after the reaction."),
                    )
                    continue

                if reaction in reactions:
                    error_messages.append(await ctx.send("Reaction already used!"))
                    continue

                try:
                    await msg.add_reaction(reaction)
                    reactions[reaction] = role
                    n += 1
                except discord.HTTPException:
                    error_messages.append(
                        await ctx.send("Invalid or inaccessible emoji!"),
                    )
                    continue
            except asyncio.TimeoutError:
                await ctx.author.send("Creation failed, timeout.")
                await self.delete_messages(user_messages + error_messages)
                return

        if not reactions:
            await ctx.send("No reactions added.")
            await self.delete_messages(user_messages + error_messages)
            return

        sent_limit_message = await ctx.send(
            "Limit to one role per user? React 🔒 for yes, 🔓 for no.",
        )
        user_messages.append(sent_limit_message)
        await sent_limit_message.add_reaction("🔒")
        await sent_limit_message.add_reaction("🔓")

        def reaction_check(payload):
            return payload.user_id == ctx.author.id and payload.message_id == sent_limit_message.id

        try:
            payload = await self.bot.wait_for(
                "raw_reaction_add",
                timeout=120,
                check=reaction_check,
            )
            limit_to_one = str(payload.emoji) == "🔒"
        except asyncio.TimeoutError:
            await ctx.author.send("Timeout.")
            await self.delete_messages(user_messages + error_messages)
            return

        sent_channel_message = await ctx.send(
            "Mention the #channel where to send the auto-role message.",
        )
        user_messages.append(sent_channel_message)

        try:
            while True:
                msg = await self.bot.wait_for("message", timeout=120, check=check)
                user_messages.append(msg)
                if msg.channel_mentions:
                    target_channel = msg.channel_mentions[0]
                    break
                error_messages.append(await ctx.send("Invalid channel."))
        except asyncio.TimeoutError:
            await ctx.author.send("Timeout.")
            await self.delete_messages(user_messages + error_messages)
            return

        selector_embed = Embed(title="Embed_title", description="Embed_content")
        sent_message_message = await ctx.send(
            "What would you like the message to say?\nFormatting is: `Message // Embed_title // Embed_content`.\nType `none` to omit.",
            embed=selector_embed,
        )
        user_messages.append(sent_message_message)

        try:
            msg = await self.bot.wait_for("message", timeout=120, check=check)
            user_messages.append(msg)

            vals = msg.content.split(" // ")
            content = vals[0] if vals[0].lower() != "none" else None

            emb = Embed()
            if len(vals) > 1 and vals[1].lower() != "none":
                emb.title = vals[1]
            if len(vals) > 2 and vals[2].lower() != "none":
                emb.description = vals[2]

            emb = emb if (emb.title or emb.description) else None

            if content or emb:
                data = {
                    "channel_id": target_channel.id,
                    "server_id": ctx.guild.id,
                    "limit_to_one": limit_to_one,
                    "reactions": reactions,
                    "message_id": 0,  # updated below
                }

                try:
                    sent_final = await target_channel.send(
                        content=content,
                        embed=emb,
                        view=PersistentRoleView(data=data),
                    )
                    data["message_id"] = sent_final.id

                    new_view = PersistentRoleView(data=data)
                    await sent_final.edit(view=new_view)

                    views = await self.config.global_().get_attr("views", {})
                    views[str(sent_final.id)] = data
                    await self.config.global_().set_attr("views", views)

                except discord.Forbidden:
                    error_messages.append(
                        await ctx.send(
                            "I don't have permission to send to that channel.",
                        ),
                    )
        except asyncio.TimeoutError:
            await ctx.author.send("Timeout.")
        finally:
            await self.delete_messages(user_messages + error_messages)

        await ctx.send(
            ":ok_hand: reaction roles successfully created.",
            delete_after=LinksAndVars.delete_message.value,
        )

    @reactionroles.command(aliases=["del_rr", "delete"], usage="<reaction_roles_id>")
    @has_permissions(manage_roles=True)
    async def delete_reaction_roles(
        self,
        ctx: commands.Context,
        reaction_roles_message: commands.MessageConverter,
    ):
        """Deletes the reaction roles setup"""
        views = await self.config.global_().get_attr("views", {})
        msg_id_str = str(reaction_roles_message.id)

        if msg_id_str not in views:
            return await ctx.send(
                "That message does not have any reaction role associated with it",
                delete_after=LinksAndVars.delete_message.value,
            )

        del views[msg_id_str]
        await self.config.global_().set_attr("views", views)

        await self.delete_messages([reaction_roles_message])
        await ctx.send(
            ":ok_hand: reaction roles was deleted",
            delete_after=LinksAndVars.delete_message.value,
        )


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
