from discord.ext import commands, tasks
import requests, time

class StatsPost_StatusPage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page_id_1 = 'xnqtmjy63llr'
        self.metric_id_1 = 'trvwzt1bqc8l'

        self.page_id_2 = 'xnqtmjy63llr'
        self.metric_id_2 = 'qdh074y44rsz'

        self.api_base = 'api.statuspage.io'
        self.api_key = bot.api_key_statuspage
        self.headers = {"Content-Type": "application/json", "Authorization": "OAuth " + self.api_key}

        self.total_points = (60 / 5 * 24)
    
    @tasks.loop(seconds = 0, hours=0,minutes=5.0, count=int(60 / 5 * 24))
    async def server_count_post(self):
        ts = int(time.time())
        requests.post(
            'https://'+ self.api_base +"/v1/pages/" + self.page_id_1 + "/metrics/" + self.metric_id_1 + "/data.json", 
            headers=self.headers, 
            json={
                    "data": {
                        'timestamp': ts, 
                        'value': len(self.bot.guilds)
                    }
                }
            )
        print(len(self.bot.guilds))
    
    @tasks.loop(seconds = 0, hours=0,minutes=5.0, count=int(60 / 5 * 24))
    async def server_count_post(self):
        print(len(set(self.bot.get_all_members())))
        ts = int(time.time())
        requests.post(
            'https://'+ self.api_base +"/v1/pages/" + self.page_id_2 + "/metrics/" + self.metric_id_2 + "/data.json", 
            headers=self.headers, 
            json={
                    "data": {
                        'timestamp': ts, 
                        'value': len(set(self.bot.get_all_members()))
                    }
                }
        )

def setup(bot):
    bot.add_cog(StatsPost_StatusPage(bot))