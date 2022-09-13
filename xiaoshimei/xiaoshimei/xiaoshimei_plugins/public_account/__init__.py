import datetime, time

from nonebot import on_command, get_bot
from nonebot.adapters import Event, Message, MessageTemplate
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, PrivateMessageEvent, GroupMessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.params import State, Depends, CommandArg, Arg, ArgPlainText
from xiaoshimei.xiaoshimei_plugins._globals import sqlquery, get_qq

public_account = on_command("pub_account", aliases={"公用号", "借用公用号"})


@public_account.handle()
async def _(event: GroupMessageEvent):
    await public_account.finish("为保护隐私，请私聊机器人使用此功能")


@public_account.handle()
async def _(event: PrivateMessageEvent, bot: Bot, state: T_State):
    if event.sub_type == "group":
        group_id = event.sender.group_id
        await bot.call_api("send_private_msg", user_id=event.user_id, group_id=event.sender.group_id, message="测试1")
    else:
        await public_account.finish("请在群聊中使用")
    if 8 < datetime.datetime.now().hour <= 23:
        result = sqlquery(0, "public_account", {"group_id": group_id},
                          "nickname", "limit_time", "user_id", "id")
        await bot.call_api("send_private_msg", user_id=event.user_id, group_id=event.sender.group_id, message="测试1")
        if not len(result):
            report = "本群目前没有可供使用的公用号"
            await bot.call_api("send_private_msg", user_id=event.user_id, group_id=event.sender.group_id, message="测试1")
            await public_account.finish(report)
        else:
            report = "公用号列表：\n=========================\n"
            for accounts in result:
                if accounts[1] <= datetime.datetime.now():
                    current_user = "40分钟内无使用者"
                else:
                    current_user = accounts[2]
                report = report + "账号编号：{}\n昵称：{}\n目前使用情况：{}\n=========================\n".format(accounts[3],
                                                                                                  accounts[0],
                                                                                                  current_user)
            state["report"] = report + "请选择您要使用的账号ID，输入其他内容取消"
    else:
        report = "目前不在可使用时间范围内"
        await public_account.finish(report)


@public_account.got("id", prompt=MessageTemplate("{report}"))
async def _(event: PrivateMessageEvent, bot: Bot, state: T_State):
    user_id = event.user_id
    group_id = event.sender.group_id
    try:
        account_id = int(state["id"])
    except ValueError:
        await public_account.finish("已取消")
    else:
        result = sqlquery(0, "public_account", {"id": account_id}, "account", "password", "limit_time", fetchone=True)
        if result[3] > datetime.datetime.now():
            await public_account.finish("此账号40分钟内有人使用，为避免顶号，请选择其他号或联系使用者QQ归还。")
        report = f"您要使用的账号如下：\n账号：{result[0]}\n密码：{result[1]}"
        msg_id = await public_account.send(report)
        sqlquery(2, "public_account_usage", None, ("id", "user_id", "group_id", "end_time"), (
        account_id, user_id, group_id,
        f"\'{(datetime.datetime.now() + datetime.timedelta(minutes=40)).strftime('%Y-%m-%d %H:%M:%S')}\'"))
        sqlquery(1, "public_account", {"id": account_id}, ("user_id", user_id), ("limit_time",
                                                                                 f"\'{(datetime.datetime.now() + datetime.timedelta(minutes=40)).strftime('%Y-%m-%d %H:%M:%S')}\'"))
        time.sleep(35)
        await bot.delete_msg(message_id=msg_id)
        await public_account.finish("已记录，请使用后及时输入“\\归还”来归还账号，或者40分钟后自动归还账号")


return_account = on_command("return_account", aliases={"归还", "归还账号"})


@return_account.handle()
async def _(event: PrivateMessageEvent):
    user_id = event.user_id
    group_id = event.sender.group_id
    result = sqlquery(0, "public_account", {"user_id": user_id, "group_id": group_id}, "limit_time", "id",
                      fetchone=True, others="ORDERED BY usage_id LIMIT 1")
    if result[0] <= datetime.datetime.now():
        await return_account.finish("您目前没有需要归还的账号，或者距离您上次借用公共号已超过40分钟")
    else:
        account_id = result[1]
        sqlquery(1, "public_account", {"id": account_id},
                 ("limit_time", f"\'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\'"))
        sqlquery(1, "public_account_usage", {"id": account_id},
                 ("end_time", f"\'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\'"))
        await return_account.finish("归还成功")


add_public_account = on_command("add_pub_account", aliases={"添加公共号", })


@add_public_account.handle()
async def _(event: PrivateMessageEvent, state: T_State, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip().split(" ")
    """添加公共号 testacc testpswd 测试昵称"""
    if len(args):
        state["account"] = args[0]
        if len(args) >= 1:
            state["password"] = args[1]
            if len(args) >= 2:
                state["nickname"] = args[2]


@add_public_account.got("account", prompt="请输入账号")
@add_public_account.got("password", prompt="请输入密码")
@add_public_account.got("nickname", prompt="请输入昵称")
async def _(event: PrivateMessageEvent, state: T_State):
    account = state["account"]
    password = state["password"]
    nickname = state["nickname"]
    group_id = event.sender.group_id
    sqlquery(2, "public_account", None, ("account", "password", "nickname", "group_id"),
             (f"\'{account}\'", f"\'{password}\'", f"\'{nickname}\'", group_id))
    await add_public_account.finish("添加成功")
