from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *


add_superuser = on_command("add_superuser", aliases={"添加管理员", },permission=SUPERUSER)
delete_superuser = on_command("delete_superuser", aliases={"移除管理员", },permission=SUPERUSER)


@add_superuser.handle()
async def _(event:GroupMessageEvent,arg : Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    group_id = event.group_id
    player_user_id = get_qq(arg)
    player = Person(player_user_id, group_id)
    player.is_superuser = 1
    player.refresh()
    await add_superuser.finish("添加成功")


@delete_superuser.handle()
async def _(event:GroupMessageEvent,arg:Message =CommandArg()):
    group_id = event.group_id
    player_user_id = get_qq(arg.extract_plain_text())
    player = Person(player_user_id, group_id)
    player.is_superuser = 0
    player.refresh()
    await add_superuser.finish("移除成功")