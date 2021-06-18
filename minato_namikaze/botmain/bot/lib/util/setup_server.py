import discord

def perms_dict(ctx):
    admin_roles = [role for role in ctx.guild.roles if role.permissions.administrator and not role.managed]
    overwrite_dict = {}
    for i in admin_roles:
        overwrite_dict[i] = discord.PermissionOverwrite(read_messages=True)
    overwrite_dict.update({ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),ctx.guild.me: discord.PermissionOverwrite(read_messages=True)})
    return admin_roles, overwrite_dict

async def channel_creation(ctx):
    admin_roles, overwrite_dict = perms_dict(ctx)
    
    category = discord.utils.get(ctx.guild.categories, name="Admin / Feedback") if discord.utils.get(ctx.guild.categories, name="Admin / Feedback") else False
    bingo = discord.utils.get(ctx.guild.categories, name="Bingo Book") if discord.utils.get(ctx.guild.categories, name="Bingo Book") else False
    if not category:category = await ctx.guild.create_category("Admin / Feedback", overwrites = overwrite_dict, reason="To log the admin and feedback events")

    #Setup / Feedback
    botask = discord.utils.get(category.channels, name="bot-setup") if discord.utils.get(category.channels, name="bot-setup") else False
    feed_channel = discord.utils.get(category.channels, name="feedback") if discord.utils.get(category.channels, name="feedback") else False

    #Bingo Book
    try: ban = discord.utils.get(bingo.channels, name="ban") if discord.utils.get(bingo.channels, name="ban") else False
    except: ban = False
        
    try: unban = discord.utils.get(bingo.channels, name="unban") if discord.utils.get(bingo.channels, name="unban") else False
    except: unban = False

    #Support
    support_channel = discord.utils.get(category.channels, name="support") if discord.utils.get(category.channels, name="support") else False
    support_channel_roles = discord.utils.get(ctx.guild.roles, name="SupportRequired") if discord.utils.get(ctx.guild.roles, name="SupportRequired") else False
    
    return feed_channel,support_channel,support_channel_roles,ban,unban,botask
    