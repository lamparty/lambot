import { Client, ClientOptions } from "discord.js";
import { dirname } from 'path';

export default class LambotClient extends Client {
    private static runPath: string = dirname(process.argv[1]);

    public commands = new Map();
    public events = new Map();
    public buttons = new Map();

    constructor(options: ClientOptions) {
        super(options);
    }
}