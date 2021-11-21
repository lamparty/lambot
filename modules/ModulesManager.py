import os
from discord.ext import commands
import json

with open("settings.json") as f:
    settings = json.load(f)

class ModulesManager(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.path = settings["bot"]["modules_path"]

def setup(client):
    client.add_cog(ModulesManager(client))

def teardown(client):
    client.remove_cog("ModulesManager")