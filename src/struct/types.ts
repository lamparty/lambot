import LambotClient from "./LambotClient";

export type assetType = 'commands' | 'events' | 'buttons';

export interface ISwitchable {
    load: (client: LambotClient) => void;
    reload: (client: LambotClient) => void;
    unload: (client: LambotClient) => void;
}