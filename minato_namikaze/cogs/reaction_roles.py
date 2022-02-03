import discord
from discord.ext import commands
import asyncio
from lib import reaction_roles_channel_name, database_category_name, Embed

class ReactionRolesButton(discord.ui.Button['ReactionPersistentView']):
    def __init__(self,database, message_id: int, emoji: discord.PartialEmoji):
        super().__init__(style=discord.ButtonStyle.secondary, emoji = emoji , custom_id=message_id)
        self.database = database

    # This function is called whenever this particular button is pressed
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        data = await self.database.get(interaction.message.id)
        if data is None:
            return
        unique = bool(data.get('limit_to_one'))
        if unique:
            roles_id_list = [data.get('reactions')[i] for i in data.get('reactions')]
            if list(map(lambda i: i.id, interaction.user.roles)) in roles_id_list:
                await interaction.response.send_message('You cannot have more than 1 role from this message', ephemeral=True)
                return
        
        for i in data.get('reactions'):
            digit = f"{ord(i):x}"
            if self.emoji is discord.PartialEmoji(name=f"\\U{digit:>08}"):
                role_id = data.get('reactions')[i]
                role_model = discord.utils.get(interaction.guild.roles, id=role_id)
                await interaction.user.add_roles(role_model, reason="Reaction Roles", atomic=True)
                try:
                    await interaction.response.send_message('You cannot have more than 1 role from this message', ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message('I don\'t have the `Manage Roles` permissions', ephemeral=True)
                except discord.HTTPException:
                    await interaction.response.send_message('Adding roles failed', ephemeral=True)
                return


class ReactionPersistentView(discord.ui.View):
    def __init__(self, reactions_dict: dict, database, message_id: int):
        super().__init__(timeout=None)
        for i in reactions_dict:
            digit = f"{ord(i):x}"
            self.add_item(ReactionRolesButton(database=database, message_id=message_id, emoji=discord.PartialEmoji(name=f"\\U{digit:>08}")))


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Setup some reaction roles"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="discord_certified_moderator",id=922030031146995733)

    async def database_class(self):
        return await self.bot.db.new(database_category_name,reaction_roles_channel_name)
    
    # set delay
    @commands.command(name="new", aliases=["create"])
    async def new(self, ctx):
        """Create a new reaction"""
        if not await ctx.prompt(
                "Welcome to the Reaction Light creation program. Please provide the required information once requested. If you would like to abort the creation then click cancel",
                author_id=ctx.author.id,
        ):
            return
        
        error_messages = []
        user_messages = []
        rl_object={}
        sent_reactions_message = await ctx.send(
        "Attach roles and emojis separated by one space (one combination"
        " per message). When you are done type `done`. Example:\n:smile:"
        " `@Role`"
        )
        rl_object["reactions"] = {}
        def check(message):
            return (
                message.author.id == ctx.message.author.id and message.content != ""
            )
        try:
            while True:
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

                    if reaction in rl_object["reactions"]:
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
                            rl_object["reactions"][reaction] = role
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
                rl_object["limit_to_one"] = 1
            else:
                rl_object["limit_to_one"] = 0
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
                        rl_object[
                            "target_channel"
                        ] = channel_message.channel_mentions[0].id
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
                    msg_values[0] if msg_values[0].lower(
                    ) != "none" else None
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
                    target_channel = ctx.bot.get_channel(rl_object["target_channel"])
                    sent_final_message = None
                    try:
                        sent_final_message = await target_channel.send(
                            content=selector_msg_body, embed=selector_embed
                        )
                        rl_object["message"] = dict(
                            message_id=sent_final_message.id,
                            channel_id=sent_final_message.channel.id,
                            guild_id=sent_final_message.guild.id,
                        )
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
        database = await self.database_class()
        await database.set(sent_final_message.id, rl_object)
        await sent_final_message.edit(view=ReactionPersistentView(reactions_dict=rl_object['reactions'],message_id=sent_final_message.id,database=database))
        await ctx.send('```json\n{}\n```'.format(rl_object))

def setup(bot):
    bot.add_cog(ReactionRoles(bot))