from __future__ import annotations

from typing import List
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from minato_namikaze.cogs.reaction_roles import Reaction_Roles


class ReactionRolesButton(discord.ui.Button["ReactionPersistentView"]):
    """The Reaction Roles Button"""

    def __init__(self, custom_id: int, emoji, role, y: int):
        self.role = role
        super().__init__(
            style=discord.ButtonStyle.primary,
            emoji=emoji,
            custom_id=custom_id,
            row=y,
        )

    # This function is called whenever this particular button is pressed
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        if self.view.data.limit_to_one:
            roles_id_list = [
                self.view.data.reactions[i] for i in self.view.data.reactions
            ]
            if list(map(lambda i: i.id, interaction.user.roles)) in roles_id_list:
                await interaction.response.send_message(
                    "You cannot have more than 1 role from this message",
                    ephemeral=True,
                )
                return

        for i in self.view.data.reactions:
            if str(self.emoji) == str(discord.PartialEmoji(name=i)):
                role_id = self.view.data.reactions[i]
                role_model = discord.utils.get(interaction.guild.roles, id=role_id)
                if role_model in interaction.user.roles:
                    try:
                        await interaction.user.remove_roles(
                            role_model,
                            reason="Reaction Roles",
                            atomic=True,
                        )
                        await interaction.response.send_message(
                            f"Removed {role_model.mention} role",
                            ephemeral=True,
                        )
                        return
                    except discord.Forbidden:
                        await interaction.response.send_message(
                            "I don't have the `Manage Roles` permissions",
                            ephemeral=True,
                        )
                    except discord.HTTPException:
                        await interaction.response.send_message(
                            "Removing roles failed",
                            ephemeral=True,
                        )
                try:
                    await interaction.user.add_roles(
                        role_model,
                        reason="Reaction Roles",
                        atomic=True,
                    )
                    await interaction.response.send_message(
                        f"Added {role_model.mention} role",
                        ephemeral=True,
                    )
                except discord.Forbidden:
                    await interaction.response.send_message(
                        "I don't have the `Manage Roles` permissions",
                        ephemeral=True,
                    )
                except discord.HTTPException:
                    await interaction.response.send_message(
                        "Adding roles failed",
                        ephemeral=True,
                    )


class ReactionPersistentView(discord.ui.View):
    """Persistant view for the Reaction Role using buton"""

    children: list[ReactionRolesButton]

    def __init__(self, data: Reaction_Roles):
        self.data = data
        super().__init__(timeout=None)
        for count, i in enumerate(data.reactions):
            self.add_item(
                ReactionRolesButton(
                    custom_id=data.custom_id[count],
                    emoji=i,
                    role=data.reactions[i],
                    y=(count // 5) + 1,
                ),
            )
