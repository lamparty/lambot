import LambotCommand from "./LambotCommand";

export default class LambotClientCommand extends LambotCommand {
    public override register(): void {
        super.register(this.client.application?.commands!);
    }
    public override unregister(): void {
        super.unregister(this.client.application?.commands!);
    }
}