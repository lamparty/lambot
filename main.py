from discord.ext import commands
import json

with open("settings.json") as f:
    settings = json.load(f)
prefix = settings["bot"]["prefix"]
token = settings["bot"]["token"]

client = commands.Bot(command_prefix=prefix)
client.load_extension(f"{settings['bot']['modules_path']}.ModulesManager")
client.run(token)