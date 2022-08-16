from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *


extra = on_command("extra",aliases={"附加功能",},permission=SUPERUSER)


@extra.handle()
async def _(event:GroupMessageEvent,arg:Message = CommandArg()):
    group_id = event.group_id
    arg = arg.extract_plain_text().strip()
    if not arg or arg == "状态":
        auth = authority(group_id)[1:-1]


#  未完待续


