import { ILambotCommandOptions } from "./types";
import LambotClient from "./LambotClient";
import LambotCommand from "./LambotCommand";

export default class LambotClientCommand extends LambotCommand {
    constructor(options: ILambotCommandOptions, client: LambotClient) {
        const { execute, name, description, SlashCommandOptions } = options;

        super(client, execute, name, description, SlashCommandOptions);
    }

    public override register(): void {
        super.register(this.client.application?.commands!);
    }
    public override unregister(): void {
        super.unregister(this.client.application?.commands!);
    }
}