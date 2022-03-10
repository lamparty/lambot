import { ILambotCommandOptions } from "./types";
import LambotCommand from "./LambotCommand";
import LambotClient from "./LambotClient";

export default class LambotGuildCommand extends LambotCommand {
    constructor(options: ILambotCommandOptions, client: LambotClient) {
        const { execute, name, description, SlashCommandOptions } = options;

        super(client, execute, name, description, SlashCommandOptions);
    }

    public override register(): void {
        this.client.guilds.cache.forEach(guild => {
            super.register(guild.commands);
        });
    }
    public override unregister(): void {
        this.client.guilds.cache.forEach(guild => {
            super.unregister(guild.commands);
        })
    }
}