import {
    SlashCommandMentionableOption, 
    SlashCommandBooleanOption, 
    SlashCommandChannelOption, 
    SlashCommandIntegerOption, 
    SlashCommandNumberOption, 
    SlashCommandStringOption, 
    SlashCommandRoleOption, 
    SlashCommandUserOption 
} from "@discordjs/builders";
import { CommandInteraction } from "discord.js";

export type executeCommand = (interaction: CommandInteraction) => void;

export type slashCommandOption = 
    SlashCommandMentionableOption |
    SlashCommandBooleanOption | 
    SlashCommandChannelOption | 
    SlashCommandIntegerOption | 
    SlashCommandStringOption |
    SlashCommandNumberOption |
    SlashCommandRoleOption |
    SlashCommandUserOption;

export interface ILambotCommandOptions {
    execute: executeCommand;
    name: string,
    description: string,
    isGlobal: boolean,
    SlashCommandOptions?: Array<slashCommandOption>
}