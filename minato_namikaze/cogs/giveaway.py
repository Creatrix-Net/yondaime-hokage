from __future__ import annotations

import datetime
import logging
import random
from typing import List
from typing import Optional

import discord
from discord.ext import commands
from discord.ext import tasks
from sqlalchemy import select
from minato_namikaze.lib import has_permissions
from minato_namikaze.lib.database.models_giveaways import Giveaway
from minato_namikaze.lib.database.models_giveaways import GiveawayEntry
from minato_namikaze.lib.database.session import session_obj


log = logging.getLogger(__name__)



# Basic time parser if lib doesn't have a good one
def parse_time(time_str: str) -> int | None:
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    unit = time_str[-1].lower()
    if unit not in time_dict:
        return None
    try:
        val = int(time_str[:-1])
        return val * time_dict[unit]
    except ValueError:
        return None


class GiveawayView(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(
        label="🎉 Join Giveaway", style=discord.ButtonStyle.success, custom_id="gw_join"
    )
    async def join_giveaway(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # Using self.message_id because the button custom_id is static in this case
        # Wait, if custom_id is static, how does it know which giveaway?
        # interaction.message.id will have the message id!
        message_id = interaction.message.id


        async with session_obj() as session:
            # Fetch giveaway
            stmt = select(Giveaway).where(Giveaway.message_id == message_id)
            gw = (await session.execute(stmt)).scalar_one_or_none()


            if not gw or gw.ended:
                return await interaction.response.send_message(
                    "This giveaway has ended or doesn't exist.", ephemeral=True
                )

            # Check requirements
            if gw.requirements:
                req_role_id = gw.requirements.get("role_id")
                if req_role_id:
                    role = interaction.guild.get_role(int(req_role_id))
                    if role and role not in interaction.user.roles:
                        return await interaction.response.send_message(f"You need the **{role.name}** role to join this giveaway!", ephemeral=True)

            # Check weights
            entries = 1
            if gw.weights:
                for role_id_str, multiplier in gw.weights.items():
                    role = interaction.guild.get_role(int(role_id_str))
                    if role and role in interaction.user.roles:
                        if multiplier > entries:
                            entries = multiplier


            # Check if already joined
            stmt = select(GiveawayEntry).where(
                GiveawayEntry.giveaway_message_id == message_id,
                GiveawayEntry.user_id == interaction.user.id,
            )
            entry = (await session.execute(stmt)).scalar_one_or_none()

            if entry:
                # Remove entry (Toggle)
                await session.delete(entry)
                await session.commit()
                return await interaction.response.send_message(
                    "You have left the giveaway.", ephemeral=True
                )
            else:
                # Add entry
                new_entry = GiveawayEntry(
                    giveaway_message_id=message_id,
                    user_id=interaction.user.id,
                    entries=entries,
                )
                session.add(new_entry)
                await session.commit()
                return await interaction.response.send_message(
                    f"Successfully joined the giveaway with {entries} entries!",
                    ephemeral=True,
                )


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Advanced database-backed Giveaways"
        self.giveaway_loop.start()

    async def cog_load(self):
        # Register the view for all active giveaways
        # Since the button custom_id is statically "gw_join", we only need to register it once globally!
        # But to be safe and use message_id dynamically, we can use a regex dispatch or just register one view for all.
        # If we use a single custom_id="gw_join" across all giveaways, we just add_view(GiveawayView(0)) and it handles it.
        self.bot.add_view(GiveawayView(0))
        log.info("Giveaway persistent views registered.")

    def cog_unload(self):
        self.giveaway_loop.cancel()

    @commands.group(aliases=["gw", "g"], invoke_without_command=True)
    async def giveaway(self, ctx):
        """Advanced Giveaways Base Command"""
        await ctx.send_help(ctx.command)

    @giveaway.command(name="start")
    @has_permissions(manage_guild=True)
    async def start(self, ctx, duration: str, winners: int, *, prize: str):
        """Start a giveaway. Example: [p]gw start 10m 2 Discord Nitro"""
        seconds = parse_time(duration)
        if not seconds:
            return await ctx.send("Invalid duration. Use s/m/h/d/w (e.g., 10m, 1h).")


        ends_at = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)


        embed = discord.Embed(
            title=prize,
            description=f"React with the button below to enter!\nEnds: <t:{int(ends_at.timestamp())}:R>\nHosted by: {ctx.author.mention}",
            color=discord.Color.blue(),
            timestamp=ends_at,
        )
        embed.set_footer(text=f"{winners} Winner(s) | Ends at")

        view = GiveawayView(message_id=0) # message_id injected dynamically via interaction
        msg = await ctx.send("🎉 **GIVEAWAY** 🎉", embed=embed, view=view)


        async with session_obj() as session:
            gw = Giveaway(
                message_id=msg.id,
                channel_id=ctx.channel.id,
                guild_id=ctx.guild.id,
                host_id=ctx.author.id,
                prize=prize,
                winners_count=winners,
                ends_at=ends_at,
            )
            session.add(gw)
            await session.commit()

    @giveaway.command(name="req")
    @has_permissions(manage_guild=True)
    async def requirement(self, ctx, message: discord.Message, role: discord.Role):
        """Set a required role for an active giveaway."""
        async with session_obj() as session:
            stmt = select(Giveaway).where(Giveaway.message_id == message.id)
            gw = (await session.execute(stmt)).scalar_one_or_none()


            if not gw:
                return await ctx.send("Giveaway not found in database.")


            reqs = dict(gw.requirements)
            reqs["role_id"] = role.id
            gw.requirements = reqs
            await session.commit()

        await ctx.send(f"Success! Users must now have {role.name} to enter the giveaway.")

    @giveaway.command(name="weight")
    @has_permissions(manage_guild=True)
    async def weight(
        self, ctx, message: discord.Message, role: discord.Role, multiplier: int
    ):
        """Set a multiplier weight for a role in a giveaway."""
        if multiplier < 1:
            return await ctx.send("Multiplier must be at least 1.")


        async with session_obj() as session:
            stmt = select(Giveaway).where(Giveaway.message_id == message.id)
            gw = (await session.execute(stmt)).scalar_one_or_none()


            if not gw:
                return await ctx.send("Giveaway not found in database.")


            weights = dict(gw.weights)
            weights[str(role.id)] = multiplier
            gw.weights = weights
            await session.commit()

        await ctx.send(f"Success! Users with {role.name} will now receive {multiplier} entries.")

    @giveaway.command(name="end")
    @has_permissions(manage_guild=True)
    async def end_giveaway(self, ctx, message: discord.Message):
        """End a giveaway early."""
        async with session_obj() as session:
            stmt = select(Giveaway).where(Giveaway.message_id == message.id)
            gw = (await session.execute(stmt)).scalar_one_or_none()


            if not gw or gw.ended:
                return await ctx.send("Giveaway not found or already ended.")


            gw.ends_at = discord.utils.utcnow()
            await session.commit()


        await ctx.send("Giveaway ending shortly...")

    @giveaway.command(name="reroll")
    @has_permissions(manage_guild=True)
    async def reroll(self, ctx, message: discord.Message):
        """Reroll a winner for a past giveaway."""
        async with session_obj() as session:
            stmt = select(Giveaway).where(Giveaway.message_id == message.id)
            gw = (await session.execute(stmt)).scalar_one_or_none()


            if not gw or not gw.ended:
                return await ctx.send("Giveaway not found or hasn't ended yet.")

            stmt = select(GiveawayEntry).where(
                GiveawayEntry.giveaway_message_id == message.id
            )
            entries = (await session.execute(stmt)).scalars().all()


            if not entries:
                return await ctx.send("No valid entries to reroll from.")


            pool = []
            for entry in entries:
                pool.extend([entry.user_id] * entry.entries)


            winner = random.choice(pool)
            await ctx.send(
                f"🎉 The new winner for **{gw.prize}** is <@{winner}>! Congratulations!"
            )

    @tasks.loop(seconds=15)
    async def giveaway_loop(self):
        """Check for ended giveaways and pick winners."""
        now = discord.utils.utcnow()
        async with session_obj() as session:
            stmt = select(Giveaway).where(
                Giveaway.ended == False, Giveaway.ends_at <= now
            )
            ended_giveaways = (await session.execute(stmt)).scalars().all()


            for gw in ended_giveaways:
                gw.ended = True
                await session.commit()


                channel = self.bot.get_channel(gw.channel_id)
                if not channel:
                    continue


                try:
                    msg = await channel.fetch_message(gw.message_id)
                except discord.NotFound:
                    continue
                except discord.HTTPException:
                    continue

                stmt = select(GiveawayEntry).where(GiveawayEntry.giveaway_message_id == gw.message_id)
                entries = (await session.execute(stmt)).scalars().all()


                pool = []
                for entry in entries:
                    pool.extend([entry.user_id] * entry.entries)


                if not pool:
                    await channel.send(f"Nobody entered the giveaway for **{gw.prize}**.")

                    emb = msg.embeds[0]
                    emb.description = "Giveaway ended. Nobody entered."
                    await msg.edit(
                        content="🎉 **GIVEAWAY ENDED** 🎉", embed=emb, view=None
                    )
                    continue


                winners = []
                # Ensure unique winners if possible
                unique_pool = list(set(pool))
                winners_count = min(gw.winners_count, len(unique_pool))


                # Weighted random sample without replacement
                for _ in range(winners_count):
                    w = random.choice(pool)
                    winners.append(w)
                    pool = [x for x in pool if x != w]


                winners_mentions = ", ".join([f"<@{w}>" for w in winners])
                await channel.send(f"🎉 Congratulations {winners_mentions}! You won **{gw.prize}**!")

                emb = msg.embeds[0]
                emb.description = (
                    f"Winners: {winners_mentions}\nHosted by: <@{gw.host_id}>"
                )
                emb.color = discord.Color.dark_gray()
                await msg.edit(content="🎉 **GIVEAWAY ENDED** 🎉", embed=emb, view=None)

    @giveaway_loop.before_loop
    async def before_giveaway_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Giveaways(bot))
