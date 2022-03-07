import { Client, ClientOptions } from "discord.js";
import { dirname } from 'path';

export default class LambotClient extends Client {
    private static runPath: string = dirname(process.argv[1]);

    public commands = new Map();
    public events = new Map();
    public buttons = new Map();

    constructor(options: ClientOptions) {
        super(options);

        this.on('ready', async () => {
            await this.fetchCommands();
        });
    }

    private async fetchCommands() {
        await this.application?.commands.fetch();
        this.guilds.cache.forEach(async guild => {
            await guild.commands.fetch();
        });
    }
}