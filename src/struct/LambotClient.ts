import { Client, ClientOptions } from "discord.js";
import { dirname } from 'path';
import { executeCommand } from "./types";

export default class LambotClient extends Client {
    private static readonly runPath: string = dirname(process.argv[1]);

    public commands: Map<string, executeCommand> = new Map();
    public events = new Map();
    public buttons = new Map();

    constructor(options: ClientOptions) {
        super(options);

        this.on('ready', async () => {
            await this.fetchCommands();
        });

        this.on('interactionCreate', interaction => {
            if (!interaction.isCommand()) return;

            const command = this.commands.get(interaction.commandName);
            if (command) command(interaction);
        });
    }

    private async fetchCommands() {
        await this.application?.commands.fetch();
        this.guilds.cache.forEach(async guild => {
            await guild.commands.fetch();
        });
    }
}