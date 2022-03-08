import { Client, ClientOptions } from "discord.js";
import { dirname } from 'path';
import { executeCommand, ILambotCommandOptions } from "./types";
import { readdirSync } from 'fs';
import path from 'path';
import LambotGuildCommand from "./LambotGuildCommand";
import LambotClientCommand from "./LambotClientCommand";

export default class LambotClient extends Client {
    private static readonly runPath: string = dirname(process.argv[1]);

    public commands: Map<string, executeCommand> = new Map();
    public events = new Map();
    public buttons = new Map();

    constructor(options: ClientOptions) {
        super(options);

        this.on('ready', async () => {
            await this.fetchCommands();
            await this.registerCommands();
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
    private async registerCommands() {
        const commandsPath = path.join(LambotClient.runPath, 'commands');
        const commandFiles = readdirSync(commandsPath)
            .filter(commandFile => commandFile.endsWith('js'))
            // files starts with dot symbol is hidden for bot
            .filter(commandFile => !commandFile.startsWith('.'));

        for (const fileName of commandFiles) {
            const commandFilePath = path.join(commandsPath, fileName);
            const commandOptions: ILambotCommandOptions = (await import(commandFilePath)).default;

            const command = commandOptions.isGlobal ? 
                new LambotClientCommand(commandOptions, this) : 
                new LambotGuildCommand(commandOptions, this);
            command.register();
        }
    }
}