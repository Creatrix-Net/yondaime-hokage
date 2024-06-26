from __future__ import annotations

import asyncio
import random
from typing import List
from typing import Optional
from typing import Tuple

import discord

# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.
class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y
        self.button_id = x

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.player1:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.player2
            view.member_board[self.y][self.x] = view.player1
            content = f"It is now O's ({view.player2.mention}) turn"

            await interaction.message.edit(content=content, view=view)
            if view.auto:
                await interaction.response.defer()
        else:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.member_board[self.y][self.x] = view.player2
            view.current_player = view.player1
            content = f"It is now X's {view.player1.mention} turn"

        winner = view.check_board_winner()
        if view.auto and winner is None or winner == view.Tie:
            await interaction.message.edit(
                content="Now let me think! ......",
                view=view,
            )
            await asyncio.sleep(2)

            left_board_space: list[tuple] = []  # [(x,y)]
            for count, i in enumerate(view.member_board):
                for count_1, j in enumerate(i):
                    if isinstance(j, int):
                        left_board_space.append((count_1, count))
            select_space = random.choice(left_board_space)
            x = select_space[0]
            y = select_space[-1]

            child = discord.utils.get(view.children, button_id=x, row=y)
            child.style = discord.ButtonStyle.success
            child.label = "O"
            child.disabled = True
            view.board[y][x] = view.O
            view.member_board[y][x] = view.player2
            view.current_player = view.player1
            content = f"It is now X's {view.player1.mention} turn"
            await interaction.message.edit(content=content, view=view)

        if winner is not None:
            if winner == view.player1:
                content = f"{view.player1.mention} won!"
            elif winner == view.player2:
                content = f"{view.player2.mention} won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()
            await interaction.message.edit(content=content, view=view)


# This is our actual board View
class TicTacToe(discord.ui.View):
    children: list[TicTacToeButton]
    Tie = 2
    X = -1
    O = 1

    def __init__(self, player1, player2, auto: bool = False):
        super().__init__()
        # X is player 1 and O is player2
        self.current_player: discord.Member | None = player1
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.member_board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.player1: discord.Member = player1
        self.player2: discord.Member = player2
        self.auto = auto
        self.message: discord.Message | None = None

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.current_player.id:
            return True
        else:
            await interaction.response.send_message(
                "This TicTacToe match is not for you or wait for your turn",
                ephemeral=True,
            )
            return False

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.player2
            elif value == -3:
                return self.player1

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.player2
            elif value == -3:
                return self.player1

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.player2
        elif diag == -3:
            return self.player1

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.player2
        elif diag == -3:
            return self.player1

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
