import asyncio
import uuid
from sqlalchemy import delete
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks
from DiscordUtils import Embed
from minato_namikaze.lib import (
    ReactionPersistentView,
    has_permissions,
    LinksAndVars,
    Base,
    Session
)
from sqlalchemy import Column, BigInteger, String, Boolean, JSON

if TYPE_CHECKING:
    from minato_namikaze.lib import Context

    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class Reaction_Roles(Base):
    __tablename__ = "reaction_roles"

    message_id = Column(BigInteger, primary_key=True, index=True, nullable=False, unique=True)
    server_id = Column(BigInteger, index=True, nullable=False)
    channel_id = Column(BigInteger, index=True, nullable=False)
    reactions = Column(JSON, nullable=False, default="'{}'::jsonb")
    limit_to_one = Column(Boolean, nullable=False, index=True)
    custom_id = Column(String(250), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"ReactionRoles(id={self.message_id!r}, server_id={self.server_id!r}, limit_to_one={self.limit_to_one!r})"

    def __str__(self):
        return self.__repr__()


class ReactionRoles(commands.Cog, name="Reaction Roles"):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.description = "Setup some reaction roles"
    
    async def setup_hook(self):
        self.cleanup.start()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="idle", id=922030033067995187)

    @tasks.loop(hours=1)
    async def cleanup(self):
        session = Session.session_manager()
        data = await session.query(Reaction_Roles).all()
        for row in data:
            channel = self.bot.get_channel(row.channel_id)
            if channel is None:
                query_delete = delete(Reaction_Roles).where(Reaction_Roles.channel_id == row.channel_id)
                await session.execute(query_delete)
            try:
                await channel.fetch_message(row.message_id)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                query_delete = delete(Reaction_Roles).where(Reaction_Roles.message_id == row.message_id)
                await session.execute(query_delete)
                
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if (
            payload.cached_message is not None
            and payload.cached_message.author.id != self.bot.application_id
        ):
            return
        session = Session.get_session()
        data = await session.query(Reaction_Roles).filter(message_id=payload.message_id).get()
        if data is not None:
            query_delete = delete(Reaction_Roles).where(Reaction_Roles.message_id == payload.message_id)
            await session.execute(query_delete)
        return

    @commands.hybrid_group(invoke_without_command=True, aliases=["reaction_roles"])
    @commands.guild_only()
    @has_permissions(manage_roles=True)
    @commands.cooldown(2, 60, commands.BucketType.guild)
    async def rr(self, ctx: "Context", command=None):
        """Reaction Roles releated commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @rr.command(name="new", aliases=["create"])
    async def new(self, ctx: "Context"):
        """
        Create a new reaction role using some interactive setup.

        ``Note: You can have upto 15 reaction buttons in a message, if it exceeds that it will automatically proceed to next step``
        """
        if not await ctx.prompt(
            "Welcome to the Reaction Light creation program. Please provide the required information once requested. If you would like to abort the creation then click cancel",
            author_id=ctx.author.id,
        ):
            return

        error_messages = []
        user_messages = []
        rl_object = Reaction_Roles()
        sent_reactions_message = await ctx.send(
            "Attach roles and emojis separated by one space (one combination"
            " per message). When you are done type `done`. Example:\n:smile:"
            " `@Role`"
        )
        reactions = {}

        def check(message):
            return message.author.id == ctx.message.author.id and message.content != ""

        try:
            n = 0
            while True:
                if n > 15:
                    break
                reactions_message = await self.bot.wait_for(
                    "message", timeout=120, check=check
                )
                user_messages.append(reactions_message)
                if reactions_message.content.lower() != "done":
                    reaction = (reactions_message.content.split())[0]
                    try:
                        role = reactions_message.role_mentions[0].id
                    except IndexError:
                        error_messages.append(
                            (
                                await ctx.send(
                                    "Mention a role after the reaction. Example:\n:smile:"
                                    " `@Role`"
                                )
                            )
                        )
                        continue

                    if reaction in reactions:
                        error_messages.append(
                            (
                                await ctx.send(
                                    "You have already used that reaction for another role. Please choose another reaction"
                                )
                            )
                        )
                        continue
                    else:
                        try:
                            await reactions_message.add_reaction(reaction)
                            reactions[reaction] = role
                            n += 1
                        except discord.HTTPException:
                            error_messages.append(
                                (
                                    await ctx.send(
                                        "You can only use reactions uploaded to servers the bot has"
                                        " access to or standard emojis."
                                    )
                                )
                            )
                            continue
                else:
                    print(reactions)
                    break
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information."
            )
            return
        finally:
            await sent_reactions_message.delete()
            for message in error_messages + user_messages:
                await message.delete()

        sent_limited_message = await ctx.send(
            "Would you like to limit users to select only have one of the roles at a given time? Please react with a \U0001f512 to limit users or with a \U0000267e to allow users to select multiple roles."
        )

        def reaction_check(payload):
            return (
                payload.member.id == ctx.message.author.id
                and payload.message_id == sent_limited_message.id
                and str(payload.emoji) in ("\U0001f512", "\U0000267e")
            )

        try:
            await sent_limited_message.add_reaction("\U0001f512")
            await sent_limited_message.add_reaction("\U0000267e")
            limited_message_response_payload = await self.bot.wait_for(
                "raw_reaction_add", timeout=120, check=reaction_check
            )

            if str(limited_message_response_payload.emoji) == "\U0001f512":
                rl_object.limit_to_one = 1
            else:
                rl_object.limit_to_one = 0
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information."
            )
            return
        finally:
            await sent_limited_message.delete()

        sent_channel_message = await ctx.send(
            "Mention the #channel where to send the auto-role message."
        )
        try:
            while True:
                channel_message = await self.bot.wait_for(
                    "message", timeout=120, check=check
                )
                if channel_message.channel_mentions:
                    target_channel = channel_message.channel_mentions[0]
                    break
                else:
                    error_messages.append(
                        (
                            await message.channel.send(
                                "The channel you mentioned is invalid."
                            )
                        )
                    )
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information."
            )
            return
        finally:
            await sent_channel_message.delete()
            for message in error_messages:
                await message.delete()

        error_messages = []
        selector_embed = Embed(
            title="Embed_title",
            description="Embed_content",
        )
        selector_embed.set_footer(
            text=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar.url
        )

        sent_message_message = await message.channel.send(
            "What would you like the message to say?\nFormatting is:"
            " `Message // Embed_title // Embed_content`.\n\n`Embed_title`"
            " and `Embed_content` are optional. You can type `none` in any"
            " of the argument fields above (e.g. `Embed_title`) to make the"
            " bot ignore it.\n\n\nMessage",
            embed=selector_embed,
        )
        try:
            while True:
                message_message = await self.bot.wait_for(
                    "message", timeout=120, check=check
                )
                # I would usually end up deleting message_message in the end but users usually want to be able to access the
                # format they once used incase they want to make any minor changes
                msg_values = message_message.content.split(" // ")
                # This whole system could also be re-done using wait_for to make the syntax easier for the user
                # But it would be a breaking change that would be annoying for thoose who have saved their message commands
                # for editing.
                selector_msg_body = (
                    msg_values[0] if msg_values[0].lower() != "none" else None
                )
                selector_embed = Embed()
                selector_embed.set_footer(
                    text=self.bot.user.name,
                    icon_url=self.bot.user.display_avatar.url,
                )

                if len(msg_values) > 1:
                    if msg_values[1].lower() != "none":
                        selector_embed.title = msg_values[1]
                    if len(msg_values) > 2 and msg_values[2].lower() != "none":
                        selector_embed.description = msg_values[2]

                    # Prevent sending an empty embed instead of removing it
                selector_embed = (
                    selector_embed
                    if selector_embed.title or selector_embed.description
                    else None
                )
                if selector_msg_body or selector_embed:
                    sent_final_message = None
                    try:
                        custom_id = [str(uuid.uuid4()) for i in reactions]
                        sent_final_message = await target_channel.send(
                            content=selector_msg_body,
                            embed=selector_embed,
                            # view=ReactionPersistentView(
                            #     reactions_dict=reactions,
                            #     custom_id=custom_id,
                            # ),
                        )
                        rl_object.custom_id = custom_id
                        rl_object.message_id = sent_final_message.id
                        rl_object.channel_id = sent_final_message.channel.id
                        rl_object.server_id = sent_final_message.guild
                        rl_object.reactions = reactions
                        break
                    except discord.Forbidden:
                        error_messages.append(
                            (
                                await message.channel.send(
                                    "I don't have permission to send messages to"
                                    f" the channel {target_channel.mention}. Please check my permissions and try again."
                                )
                            )
                        )
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information."
            )
            return
        finally:
            await sent_message_message.delete()
            for message in error_messages:
                await message.delete()
        async with Session.session_manager() as session:
            async with session.begin():
                await session.add(rl_object)

    @rr.command(aliases=["del_rr"], usage="<reaction_roles_id aka message.id")
    async def delete_reaction_roles(
        self, ctx: "Context", reaction_roles_id: commands.MessageConverter
    ):
        """
        It deletes the reaction roles
        args:
            reaction_roles_id : It is the message id of the reaction roles messages
        https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-
        """
        async with Session.session_manager() as session:
            async with session.begin():
                rl_object = await session.query(ReactionRoles).filter(message_id=reaction_roles_id.id).get()
                if rl_object is None:
                    await ctx.send(
                        "That message does not have any reaction role associated with it",
                        ephemeral=True,
                    )
                    return
                query_delete = delete(Reaction_Roles).where(Reaction_Roles.message_id == reaction_roles_id.id)
                await session.execute(query_delete)
        
        await ctx.send(":ok_hand:", delete_after=LinksAndVars.delete_message.value)


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(ReactionRoles(bot))
