import discord
import asyncio

from typing import List
import random
RED = "\U0001f534"
BLUE = "\U0001f535"
BLANK = "\U00002b1b"

class ConnectFourButton(discord.ui.Button["ConnectFour"]):
    def __init__(self, y: int, emoji):
        super().__init__(style=discord.ButtonStyle.primary,emoji=emoji,row=y)
    
    async def callback(self,interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError

        self.view.PlacePiece(self.emoji, interaction.user)
        embed = self.view.make_embed()
        await interaction.message.edit(embeds=[embed,self.view.BoardString()], view=self.view)
        if self.view.GameOver():
            embed = self.view.make_embed()
            for child in self.view.children:
                child.disabled = True
            await interaction.message.edit(embeds=[embed,self.view.BoardString()], view=self.view)
            self.view.stop()
            return
        
        await interaction.response.send_message('Now let me think! ......',ephemeral=True)
        await asyncio.sleep(2)
        
        #if bot
        if not self.view.auto:
            return
        if self.view.turn is not self.view.blue_player:
            return
        self.view.PlacePiece(random.choice(self.view._controls), self.view.turn)
        embed = self.view.make_embed()
        await interaction.message.edit(embeds=[embed,self.view.BoardString()], view=self.view)
        if self.view.GameOver():
            embed = self.view.make_embed()
            for child in self.view.children:
                child.disabled = True
            await interaction.message.edit(embeds=[embed,self.view.BoardString()], view=self)
            self.view.stop()


class Quit(discord.ui.Button["ConnectFour"]):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red,label='Quit',row=2)
    
    async def callback(self,interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError

        await interaction.response.defer()
        await interaction.delete_original_message()
        self.view.stop()

class ConnectFour(discord.ui.View):
    children: List[ConnectFourButton]

    def __init__(self, *, red: discord.Member, blue: discord.Member, auto: bool = False):
        super().__init__()
        self.red_player = red
        self.blue_player = blue
        self.auto = auto
        self.message : discord.Message = None
        self.board = [[BLANK for __ in range(7)] for __ in range(6)]
        self._controls = (
            discord.PartialEmoji(name="\N{DIGIT ONE}\U000020e3"),
            discord.PartialEmoji(name="\N{DIGIT TWO}\U000020e3"),
            discord.PartialEmoji(name="\N{DIGIT THREE}\U000020e3"),
            discord.PartialEmoji(name="\N{DIGIT FOUR}\U000020e3"),
            discord.PartialEmoji(name="\N{DIGIT FIVE}\U000020e3"),
            discord.PartialEmoji(name="\N{DIGIT SIX}\U000020e3"),
            discord.PartialEmoji(name="\N{DIGIT SEVEN}\U000020e3"),
        )
        self.turn = self.red_player
        self.message = None
        self.winner = None
        self._conversion = {
            discord.PartialEmoji(name="\N{DIGIT ONE}\U000020e3"): 0,
            discord.PartialEmoji(name="\N{DIGIT TWO}\U000020e3"): 1,
            discord.PartialEmoji(name="\N{DIGIT THREE}\U000020e3"): 2,
            discord.PartialEmoji(name="\N{DIGIT FOUR}\U000020e3"): 3,
            discord.PartialEmoji(name="\N{DIGIT FIVE}\U000020e3"): 4,
            discord.PartialEmoji(name="\N{DIGIT SIX}\U000020e3"): 5,
            discord.PartialEmoji(name="\N{DIGIT SEVEN}\U000020e3"): 6,
        }
        self._PlayerToEmoji = {
            self.red_player: RED,
            self.blue_player: BLUE,
        }
        self._EmojiToPlayer = {
            RED: self.red_player,
            BLUE: self.blue_player
        }
        self.embed = self.make_embed()
        for i in range(7):
            row = i//2 if i > 1 else 1
            self.add_item(ConnectFourButton(y=row if row <=2 else 2,emoji=self._controls[i]))
        self.add_item(Quit())

    def BoardString(self) -> str:
        board = "\N{DIGIT ONE}\U000020e3\N{DIGIT TWO}\U000020e3\N{DIGIT THREE}\U000020e3\N{DIGIT FOUR}\U000020e3\N{DIGIT FIVE}\U000020e3\N{DIGIT SIX}\U000020e3\N{DIGIT SEVEN}\U000020e3\n"
        for row in self.board:
            board += "".join(row) + "\n"
        return discord.Embed(description=board)

    def make_embed(self) -> discord.Embed:
        embed = discord.Embed()
        if not self.GameOver():
            embed.description = f"**Turn:** {self.turn.mention}\n**Piece:** `{self._PlayerToEmoji[self.turn]}`"
        else:
            status = f"{self.winner.mention} won!" if self.winner else "Tie"
            embed.description = f"**Game over**\n{status}"
            embed.color = discord.Color.green()
        return embed

    def PlacePiece(self, emoji: str, user) -> list:
        if emoji not in self._controls:
            raise KeyError("Provided emoji is not one of the valid controls")
        y = self._conversion[emoji]

        for x in range(5, -1, -1):
            if self.board[x][y] == BLANK:
                self.board[x][y] = self._PlayerToEmoji[user]
                break

        self.turn = self.red_player if user == self.blue_player else self.blue_player
        return self.board

    def GameOver(self) -> bool:
        if all(i != BLANK for i in self.board[0]):
            return True

        for x in range(6):
            for i in range(4):
                if (self.board[x][i] == self.board[x][i + 1] ==
                        self.board[x][i + 2] ==
                        self.board[x][i + 3]) and self.board[x][i] != BLANK:
                    self.winner = self._EmojiToPlayer[self.board[x][i]]
                    return True

        for x in range(3):
            for i in range(7):
                if (self.board[x][i] == self.board[x + 1][i] ==
                        self.board[x + 2][i] ==
                        self.board[x + 3][i]) and self.board[x][i] != BLANK:
                    self.winner = self._EmojiToPlayer[self.board[x][i]]
                    return True

        for x in range(3):
            for i in range(4):
                if (self.board[x][i] == self.board[x + 1][i + 1] ==
                        self.board[x + 2][i + 2] == self.board[x + 3][i + 3]
                    ) and self.board[x][i] != BLANK:
                    self.winner = self._EmojiToPlayer[self.board[x][i]]
                    return True

        for x in range(5, 2, -1):
            for i in range(4):
                if (self.board[x][i] == self.board[x - 1][i + 1] ==
                        self.board[x - 2][i + 2] == self.board[x - 3][i + 3]
                    ) and self.board[x][i] != BLANK:
                    self.winner = self._EmojiToPlayer[self.board[x][i]]
                    return True

        return False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.turn:
            return True
        else:
            await interaction.response.send_message("This Connect Four match is not for you or wait for your turn", ephemeral=True)
            return False
    
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(embeds=[self.embed, self.BoardString()],view=self)
