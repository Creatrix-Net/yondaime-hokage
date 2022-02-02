from typing import Optional, Union

import discord
from discord.ext import commands

BLANK = "\U0001f533"
CIRCLE = "\U0000274c"
CROSS = "\U0000274c"


class Tictactoe:
    def __init__(self, cross: discord.Member, circle: discord.Member) -> None:
        self.cross = cross
        self.circle = circle
        self.board = [[BLANK for __ in range(3)] for __ in range(3)]
        self.turn = self.cross
        self.winner = None
        self.message = None
        self._controls = [
            "\N{DIGIT ONE}\U000020e3",
            "\N{DIGIT TWO}\U000020e3",
            "\N{DIGIT THREE}\U000020e3",
            "\N{DIGIT FOUR}\U000020e3",
            "\N{DIGIT FIVE}\U000020e3",
            "\N{DIGIT SIX}\U000020e3",
            "\N{DIGIT SEVEN}\U000020e3",
            "\N{DIGIT EIGHT}\U000020e3",
            "\N{DIGIT NINE}\U000020e3",
        ]
        self._conversion = {
            "\N{DIGIT ONE}\U000020e3": (0, 0),
            "\N{DIGIT TWO}\U000020e3": (0, 1),
            "\N{DIGIT THREE}\U000020e3": (0, 2),
            "\N{DIGIT FOUR}\U000020e3": (1, 0),
            "\N{DIGIT FIVE}\U000020e3": (1, 1),
            "\N{DIGIT SIX}\U000020e3": (1, 2),
            "\N{DIGIT SEVEN}\U000020e3": (2, 0),
            "\N{DIGIT EIGHT}\U000020e3": (2, 1),
            "\N{DIGIT NINE}\U000020e3": (2, 2),
        }
        self._EmojiToPlayer = {
            CIRCLE: self.circle,
            CROSS: self.cross,
        }
        self._PlayerToEmoji = {
            self.cross: CROSS,
            self.circle: CIRCLE,
        }

    def BoardString(self) -> str:
        board = ""
        for row in self.board:
            board += "".join(row) + "\n"
        return board

    async def make_embed(self) -> discord.Embed:
        embed = discord.Embed()
        if not await self.GameOver():
            embed.description = f"**Turn:** {self.turn.name}\n**Piece:** `{self._PlayerToEmoji[self.turn]}`"
        else:
            status = f"{self.winner} won!" if self.winner else "Tie"
            embed.description = f"**Game over**\n{status}"
        return embed

    async def MakeMove(self, emoji: str, user: discord.Member) -> list:

        if emoji not in self._controls:
            raise KeyError("Provided emoji is not one of the valid controls")
        x, y = self._conversion[emoji]
        piece = self._PlayerToEmoji[user]
        self.board[x][y] = piece
        self.turn = self.circle if user == self.cross else self.cross
        self._conversion.pop(emoji)
        self._controls.remove(emoji)
        return self.board

    async def GameOver(self) -> bool:

        if not self._controls:
            return True

        for i in range(3):

            if (self.board[i][0] == self.board[i][1] ==
                    self.board[i][2]) and self.board[i][0] != BLANK:
                self.winner = self._EmojiToPlayer[self.board[i][0]]
                return True
            if (self.board[0][i] == self.board[1][i] ==
                    self.board[2][i]) and self.board[0][i] != BLANK:
                self.winner = self._EmojiToPlayer[self.board[0][i]]
                return True

        if (self.board[0][0] == self.board[1][1] ==
                self.board[2][2]) and self.board[0][0] != BLANK:
            self.winner = self._EmojiToPlayer[self.board[0][0]]
            return True

        if (self.board[0][2] == self.board[1][1] ==
                self.board[2][0]) and self.board[0][2] != BLANK:
            self.winner = self._EmojiToPlayer[self.board[0][2]]
            return True

        return False

    async def start(
        self,
        ctx: commands.Context,
        *,
        remove_reaction_after: bool = False,
        return_after_block: int = None,
        **kwargs,
    ):
        embed = await self.make_embed()
        self.message = await ctx.send(self.BoardString(),
                                      embed=embed,
                                      **kwargs)

        for button in self._controls:
            await self.message.add_reaction(button)

        while True:

            def check(reaction, user):
                return (str(reaction.emoji) in self._controls
                        and user == self.turn
                        and reaction.message == self.message)

            reaction, user = await ctx.bot.wait_for("reaction_add",
                                                    check=check)

            if await self.GameOver():
                break

            emoji = str(reaction.emoji)
            await self.MakeMove(emoji, user)
            embed = await self.make_embed()

            if remove_reaction_after:
                await self.message.remove_reaction(emoji, user)

            await self.message.edit(content=self.BoardString(), embed=embed)

        embed = await self.make_embed()
        return await self.message.edit(content=self.BoardString(), embed=embed)
