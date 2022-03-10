import { SlashCommandBuilder } from "@discordjs/builders";
import { ApplicationCommandManager, GuildApplicationCommandManager } from "discord.js";
import { executeCommand, ILambotCommandOptions } from "./types";
import LambotClient from "./LambotClient";

export default abstract class LambotCommand extends SlashCommandBuilder {
    protected readonly client: LambotClient;
    public readonly execute: executeCommand;

    public constructor(options: ILambotCommandOptions, client: LambotClient) {
        const { execute, name, description, slashCommandOptions } = options;
        super();

        this.client = client;
        this.execute = execute;
        this.setName(name);
        this.setDescription(description);

        if (!slashCommandOptions) return;
        slashCommandOptions.forEach(option => {
            this.options.push(option);
        });
    }

    protected register(target: GuildApplicationCommandManager | ApplicationCommandManager) {
        target.create(this.toJSON());
        this.client.commands.set(this.name, this.execute);
    }
    protected unregister(target: GuildApplicationCommandManager | ApplicationCommandManager) {
        target.cache
            .filter(command => command.client.user?.id === this.client.user?.id)
            .forEach(command => command.delete());
        this.client.commands.delete(this.name);
    }
}