import discord

from .vars import ban, feedback, support, unban, warns


def perms_dict(ctx):
    admin_roles = [
        role for role in ctx.guild.roles if role.permissions.manage_guild and not role.managed
    ]
    overwrite_dict = {}
    for i in admin_roles:
        overwrite_dict[i] = discord.PermissionOverwrite(read_messages=True)
    overwrite_dict.update({ctx.guild.default_role: discord.PermissionOverwrite(
        read_messages=False), ctx.guild.me: discord.PermissionOverwrite(read_messages=True)})
    return admin_roles, overwrite_dict


async def channel_creation(ctx):
    admin_roles, overwrite_dict = perms_dict(ctx)

    category = discord.utils.get(ctx.guild.categories, name="Admin / Feedback") if discord.utils.get(
        ctx.guild.categories, name="Admin / Feedback") else False

    # Feedback Channel
    if discord.utils.get(ctx.guild.text_channels, topic=feedback):
        feed_channel = discord.utils.get(
            ctx.guild.text_channels,
            topic=feedback
        )
    else:
        feed_channel = False

    # Ban
    if discord.utils.get(ctx.guild.text_channels, topic=ban):
        ban_channel = discord.utils.get(
            ctx.guild.text_channels,
            topic=ban
        )
    else:
        ban_channel = False

    # Unban
    if discord.utils.get(ctx.guild.text_channels, topic=unban):
        unban_channel = discord.utils.get(
            ctx.guild.text_channels,
            topic=unban,
        )
    else:
        unban_channel = False

    # Warns
    if discord.utils.get(ctx.guild.text_channels, topic=warns):
        warns_channel = discord.utils.get(
            ctx.guild.text_channels,
            topic=warns,
        )
    else:
        warns_channel = False

    # Support
    if discord.utils.get(ctx.guild.text_channels, topic=support):
        support_channel = discord.utils.get(
            ctx.guild.text_channels,
            topic=support
        )
    else:
        support_channel = False

    support_channel_roles = discord.utils.get(ctx.guild.roles, name="SupportRequired") if discord.utils.get(
        ctx.guild.roles, name="SupportRequired") else False

    if isinstance(support_channel, bool) or isinstance(unban, bool) or isinstance(ban, bool) or isinstance(feed_channel, bool) or isinstance(warns, bool):
        if isinstance(category, bool):
            category = await ctx.guild.create_category("Admin / Feedback", overwrites=overwrite_dict, reason="To log the admin and feedback events")

    # Bot Setup
    if not discord.utils.get(category.channels, name="bot-setup"):
        botask = discord.utils.get(category.channels, name="bot-setup")
    else:
        botask = False

    return feed_channel, support_channel, support_channel_roles, ban_channel, unban_channel, warns_channel, botask
