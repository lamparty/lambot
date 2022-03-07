import { CommandInteraction } from "discord.js";
import { ILambotCommandOptions } from "../struct/types";

// every command must have name, description, isGlobal flag and execute function

const command: ILambotCommandOptions = {
    name: "#", // name for command
    description: "#", // description for command 
    isGlobal: false, // true or false
    execute: function (interaction: CommandInteraction): void {
        // here your handler code for command
    }
}

export default command;