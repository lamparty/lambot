import { CommandInteraction } from "discord.js";

export type executeCommand = (interaction: CommandInteraction) => void;

export interface ILambotCommandOptions {
    execute: executeCommand;
    name: string,
    description: string,
    isGlobal: boolean,
}