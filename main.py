from discord.ext import commands
import json
import os

with open("settings.json") as f:
    settings = json.load(f)
prefix = settings["bot"]["prefix"]
token = settings["bot"]["token"]

client = commands.Bot(command_prefix=prefix)

client.load_extension("modules.Manager")

client.run(token)
