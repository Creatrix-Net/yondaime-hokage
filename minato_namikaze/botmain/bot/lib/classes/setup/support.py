import discord
from discord.ext import menus

from ...util import perms_dict, support
from ..embed import Embed


class Support(menus.Menu):
    def __init__(self, bot, timeout, channel):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.channel = channel

    async def send_initial_message(self, ctx, channel):
        embed = Embed(
            title=f"Want to create a support system for the **{ctx.guild.name}** ?")
        embed.add_field(name="Yes", value=":white_check_mark:")
        embed.add_field(name="No", value=":negative_squared_cross_mark:")
        return await channel.send(embed=embed)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def on_add(self, payload):
        sup_roles = discord.utils.get(
            self.ctx.guild.roles, name="SupportRequired")
        if not sup_roles:
            sup_roles = await self.ctx.guild.create_role(name="SupportRequired")

        admin_roles, overwrite_dict = perms_dict(self.ctx)

        overwrite_dict.update({
            discord.utils.get(
                self.ctx.guild.roles, name="SupportRequired"): discord.PermissionOverwrite(
                    read_messages=True, read_message_history=True, send_messages=True, send_tts_messages=True, embed_links=True, attach_files=True, external_emojis=True
            ),
            self.ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False, send_messages=False)
        })

        sup = await self.ctx.guild.create_text_channel(
            "Support", overwrites=overwrite_dict,
            topic=support,
            category=discord.utils.get(
                self.ctx.guild.categories, name="Admin / Feedback")
        )

        a = '**This channel** will be used as the **support channel** who needs support!'
        b = f'Once the member uses the **`)support` command** they will be given a role of **{sup_roles.mention}** to **access this channel**'
        c = 'Then you can use **`)resolved`** command if the **issue has been resolved!**'
        d = 'Use `)chksupreq` to see **who still requires support**!'

        await self.channel.send(f'{sup.mention} channel **created** as the **support** channel for the {self.ctx.guild.name} server!')
        e = Embed(
            title='Important notes!',
            description=f'- {a} \n -{b} \n -{c} \n -{d}'
        )
        message_embed = await sup.send(embed=e)
        await message_embed.pin()
        return

    @menus.button('\N{NEGATIVE SQUARED CROSS MARK}')
    async def on_stop(self, payload):
        await self.channel.send(f'Okay, so no **support system** will be there for the **{self.ctx.guild.name}**')
        return
