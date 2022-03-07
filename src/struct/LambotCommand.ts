import { SlashCommandBuilder } from "@discordjs/builders";
import { ApplicationCommandManager, GuildApplicationCommandManager } from "discord.js";
import { executeCommand } from "./types";
import LambotClient from "./LambotClient";

export default abstract class LambotCommand extends SlashCommandBuilder {
    protected constructor(
        protected readonly client: LambotClient, 
        protected readonly execute: executeCommand,
    ) {
        super();
    }

    protected register(target: GuildApplicationCommandManager | ApplicationCommandManager) {
        if (this.name !== undefined)
        try {
            target.create(this.toJSON());
        } catch (error) {
            console.error(error);
        }
    }
    protected unregister(target: GuildApplicationCommandManager | ApplicationCommandManager) {
        target.cache.forEach(command => {
            if (command.name !== this.name) return;

            try {
                command.delete();
            } catch (error) {
                console.error(error);
            }
        })
    }
}