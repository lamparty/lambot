from discord.ext import commands
import json
import os

with open("settings.json") as f:
    settings = json.load(f)
prefix = settings["bot"]["prefix"]
token = settings["bot"]["token"]
modules_path = settings["bot"]["modules_path"]

client = commands.Bot(command_prefix=prefix)

@client.event
async def on_ready():
    for module in os.listdir(modules_path):
        if (module.endswith(".py")):
            client.load_extension(f"{modules_path}.{module[:-3]}")

client.run(token)