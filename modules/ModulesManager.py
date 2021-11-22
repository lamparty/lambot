import os
from discord.ext import commands
import json

with open("settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

class ModulesManager(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.path = settings["bot"]["modules_path"]
    
    @commands.command()
    async def loadModule(self, ctx, *, extensionName):
        self.client.load_extension(f"{self.path}.{extensionName}")

    @commands.command()
    async def unloadModule(self, ctx, *, extensionName):
        self.client.unload_extension(f"{self.path}.{extensionName}")

    @commands.command()
    async def reloadModule(self, ctx, *, extensionName):
        self.client.unload_extension(f"{self.path}.{extensionName}")
        self.client.load_extension(f"{self.path}.{extensionName}")

def setup(client):
    client.add_cog(ModulesManager(client))

def teardown(client):
    client.remove_cog("ModulesManager")