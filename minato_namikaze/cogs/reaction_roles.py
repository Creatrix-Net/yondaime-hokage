import asyncio
import uuid
from sqlalchemy import delete, exists, select
from typing import TYPE_CHECKING, List, Tuple
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

import discord
from discord.ext import commands, tasks
from minato_namikaze.lib import (
    ReactionPersistentView,
    session_obj,
    has_permissions,
    LinksAndVars,
    Base,
    Embed
)
from sqlalchemy import Column, BigInteger, String, Boolean, JSON, ARRAY

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
    custom_id = Column(ARRAY(String(250)), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"ReactionRoles(id={self.message_id!r}, server_id={self.server_id!r}, limit_to_one={self.limit_to_one!r})"

    def __str__(self):
        return self.__repr__()


class ReactionRoles(commands.Cog, name="Reaction Roles"):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.description = "Setup some reaction roles"
        self.cleanup.start()
    
    async def cog_unload(self):
        self.cleanup.cancel()
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="idle", id=922030033067995187)

    @tasks.loop(hours=1)
    async def cleanup(self):
        async with session_obj() as session:
            query= select(Reaction_Roles)
            data = (await session.execute(query)).all()
            for row in data:
                row=row[0]
                channel = self.bot.get_channel(row.channel_id)
                if channel is None:
                    query_delete = delete(Reaction_Roles).where(Reaction_Roles.channel_id == row.channel_id)
                    await session.execute(query_delete)
                try:
                    await channel.fetch_message(row.message_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    query_delete = delete(Reaction_Roles).where(Reaction_Roles.message_id == row.message_id)
                    await session.execute(query_delete)
                await session.commit()
                
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if (
            payload.cached_message is not None
            and payload.cached_message.author.id != self.bot.application_id
        ):
            return
        async with session_obj() as session:
            query= select(Reaction_Roles).where(Reaction_Roles.message_id==payload.message_id)
            try:
                data = (await session.execute(exists(query).select())).scalar_one()
                if data:
                    query_delete = delete(Reaction_Roles).where(Reaction_Roles.message_id == payload.message_id)
                    await session.execute(query_delete)
                    await session.commit()
            except (NoResultFound, MultipleResultsFound):
                pass
    
    @staticmethod
    async def delete_messages(list_delete: List[discord.Message]) -> Tuple[List]:     
        """Delete the messages from list

        :param list_delete: The list of messages to be deleted.
        :type list_delete: List[discord.Message]
        :return: Empty list
        :rtype: Tuple[List]
        """         
        for message in list_delete:
            try:
                await message.delete()
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                pass
        return [], []

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
        user_messages.append(sent_reactions_message)
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
                    break
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information.",
                delete_after=LinksAndVars.delete_message.value
            )
            await self.delete_messages(user_messages+error_messages)
            return
        finally:
            user_messages,error_messages = await self.delete_messages(user_messages+error_messages)

        sent_limited_message = await ctx.send(
            "Would you like to limit users to select only have one of the roles at a given time? Please react with a \U0001f512 to limit users or with a \U0000267e to allow users to select multiple roles."
        )
        user_messages.append(sent_limited_message)
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
                "Reaction Light creation failed, you took too long to provide the requested information.",
                delete_after=LinksAndVars.delete_message.value
            )
            return
        finally:
            user_messages,error_messages = await self.delete_messages(user_messages+error_messages)

        sent_channel_message = await ctx.send(
            "Mention the #channel where to send the auto-role message."
        )
        try:
            while True:
                channel_message  = await self.bot.wait_for(
                    "message", timeout=120, check=check
                )
                if channel_message.channel_mentions:
                    target_channel = channel_message.channel_mentions[0]
                    user_messages.extend([sent_channel_message, channel_message])
                    break
                else:
                    error_messages.append(
                        (
                            await ctx.send(
                                "The channel you mentioned is invalid."
                            )
                        )
                    )
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information.",
                delete_after=LinksAndVars.delete_message.value
            )
            await self.delete_messages(user_messages+error_messages)
            return
        finally:
            user_messages, error_messages = await self.delete_messages(user_messages+error_messages)

        selector_embed = Embed(
            title="Embed_title",
            description="Embed_content",
        )
        selector_embed.set_footer(
            text=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar.url
        )

        sent_message_message = await ctx.send(
            "What would you like the message to say?\nFormatting is:"
            " `Message // Embed_title // Embed_content`.\n\n`Embed_title`"
            " and `Embed_content` are optional. You can type `none` in any"
            " of the argument fields above (e.g. `Embed_title`) to make the"
            " bot ignore it.\n\n\nMessage",
            embed=selector_embed,
        )
        user_messages.append(sent_message_message)
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
                        rl_object.server_id = sent_final_message.guild.id
                        rl_object.reactions = reactions
                        break
                    except discord.Forbidden:
                        error_messages.append(
                            (
                                await ctx.send(
                                    "I don't have permission to send messages to"
                                    f" the channel {target_channel.mention}. Please check my permissions and try again."
                                )
                            )
                        )
        except asyncio.TimeoutError:
            await ctx.author.send(
                "Reaction Light creation failed, you took too long to provide the requested information.",
                delete_after=LinksAndVars.delete_message.value
            )
            await self.delete_messages(user_messages+error_messages)
            return
        finally:
            await self.delete_messages(user_messages+error_messages)         
        async with session_obj() as session:
            async with session.begin():
                session.add(rl_object)
        await ctx.send(':ok_hand: reaction roles successfully created.', delete_after=LinksAndVars.delete_message.value)

    @rr.command(aliases=["del_rr", "delete"], usage="<reaction_roles_id aka message.id")
    async def delete_reaction_roles(
        self, ctx: "Context", reaction_roles_message: commands.MessageConverter
    ):
        """
        It deletes the reaction roles
        args:
            reaction_roles_id : It is the message id of the reaction roles messages
        https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-
        """
        async with session_obj() as session:
            query = select(Reaction_Roles).where(Reaction_Roles.message_id==reaction_roles_message.id)
            rl_object = (await session.execute(exists(query).select())).scalar_one()
            if not rl_object:
                await ctx.send(
                    "That message does not have any reaction role associated with it",
                    delete_after=LinksAndVars.delete_message.value
                )
                return
            query_delete = delete(Reaction_Roles).where(Reaction_Roles.message_id == reaction_roles_message.id)
            await session.execute(query_delete)
            await session.commit()
        
        await self.delete_messages([reaction_roles_message])
        await ctx.send(":ok_hand: reaction roles was deleted", delete_after=LinksAndVars.delete_message.value)


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(ReactionRoles(bot))
