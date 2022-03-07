import LambotClient from "./LambotClient";

export type executeCommand = (interaction: CommandInteraction) => void;

export interface ISwitchable {
    load: (client: LambotClient) => void;
    reload: (client: LambotClient) => void;
    unload: (client: LambotClient) => void;
}