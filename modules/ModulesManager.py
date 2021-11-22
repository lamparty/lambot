import os
from discord.ext import commands
from discord.utils import get
import json

with open("settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

async def isAdministrator(ctx):
    admin = get(ctx.guild.roles, name=settings["bot"]["admin_role_name"])
    return admin in ctx.author.roles

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

    @commands.command()
    async def showModules(self, ctx):
        await ctx.send(self.client.extensions.keys())

def setup(client):
    client.add_cog(ModulesManager(client))

def teardown(client):
    client.remove_cog("ModulesManager")