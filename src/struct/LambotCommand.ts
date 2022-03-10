import { SlashCommandBuilder } from "@discordjs/builders";
import { ApplicationCommandManager, GuildApplicationCommandManager } from "discord.js";
import { slashCommandOption, executeCommand } from "./types";
import LambotClient from "./LambotClient";

export default abstract class LambotCommand extends SlashCommandBuilder {
    protected constructor(
        protected readonly client: LambotClient, 
        public readonly execute: executeCommand,
        name: string,
        description: string,
        slashCommandOptions?: Array<slashCommandOption>,
    ) {
        super();

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