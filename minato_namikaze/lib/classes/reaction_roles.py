import discord

class ReactionRolesButton(discord.ui.Button['ReactionPersistentView']):
    def __init__(self,database, custom_id: int, emoji, y:int):
        super().__init__(style=discord.ButtonStyle.primary , emoji=emoji,custom_id=custom_id, row=y)
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
            if self.emoji == discord.PartialEmoji(name=i):
                role_id = data.get('reactions')[i]
                role_model = discord.utils.get(interaction.guild.roles, id=role_id)
                if role_model in interaction.user.roles:
                    try:
                        await interaction.user.remove_roles(role_model, reason="Reaction Roles", atomic=True)
                        await interaction.response.send_message(f'Removed {role_model.mention} role', ephemeral=True)
                        return
                    except discord.Forbidden:
                        await interaction.response.send_message('I don\'t have the `Manage Roles` permissions', ephemeral=True)
                    except discord.HTTPException:
                        await interaction.response.send_message('Removing roles failed', ephemeral=True)
                try:
                    await interaction.user.add_roles(role_model, reason="Reaction Roles", atomic=True)
                    await interaction.response.send_message(f'Added {role_model.mention} role', ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message('I don\'t have the `Manage Roles` permissions', ephemeral=True)
                except discord.HTTPException:
                    await interaction.response.send_message('Adding roles failed', ephemeral=True)


class ReactionPersistentView(discord.ui.View):
    def __init__(self, reactions_dict: dict, database, custom_id: list):
        super().__init__(timeout=None)
        for count,i in enumerate(reactions_dict):
            self.add_item(ReactionRolesButton(database=database, custom_id=custom_id[count], emoji=i, y=(count//5)+1))