import LambotCommand from "./LambotCommand";

export default class LambotGuildCommand extends LambotCommand {
    public override register(): void {
        this.client.guilds.cache.forEach(guild => {
            super.register(guild.commands);
        });
    }
    public override unregister(): void {
        this.client.guilds.cache.forEach(guild => {
            super.unregister(guild.commands);
        })
    }
}