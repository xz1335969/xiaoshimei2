import random,os,re

from nonebot import on_command, get_bot
from nonebot.adapters import Event, Message, MessageTemplate
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, PrivateMessageEvent, GroupMessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.params import State, Depends, CommandArg, Arg, ArgPlainText
from .._globals import image_reply,text_reply
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO




def image_cmd(command_name: str, aliases: set[str, ...]):
    image_command = on_command(command_name, aliases=aliases)

    @image_command.handle()
    async def _(args: Message = CommandArg()):
        plain_text = args.extract_plain_text()
        if plain_text:
            return
        url = __file__.strip("__init__.py") + f"resources\\{command_name}.png"
        await image_command.finish(MessageSegment.image("file:///" + url))

    return command_name


def text_cmd(command_name: str, aliases: set[str, ...], text: str):
    text_command = on_command(command_name, aliases=aliases)

    @text_command.handle()
    async def _(args: Message = CommandArg()):
        plain_text = args.extract_plain_text()
        if plain_text:
            return
        await text_command.finish(text)

    return command_name


for items in image_reply.keys():
    image_cmd(command_name=items, aliases=image_reply[items])

for items in text_reply:
    aliases = text_reply[items][0]
    text = text_reply[items][1]
    text_cmd(command_name=items, aliases=aliases, text=text)

petgrow = on_command("petgrow", aliases={"宠物成长", })


@petgrow.handle()
async def _(
        args: Message = CommandArg()
):
    plain_text = args.extract_plain_text()
    if plain_text:
        return
    report = MessageSegment.image(__file__.strip("__init__.py") + "resources\\petgrow.png") + MessageSegment.image(
        __file__.strip("__init__.py") + "resources\\petstatus2.png")
    await petgrow.finish("file:///" + report)


async def get_random_nums(state: T_State, arg: Message = Arg("range")):
    value = arg.extract_plain_text().split("-")
    try:
        _max = value[1]
        _min = value[0]
    except IndexError:
        _max = value[0]
        _min = 1
    except Exception:
        print(str(Exception))
        return
    finally:
        try:
            _max = int(_max)
            _min = int(_min)
        except ValueError:
            await dice.reject(
                prompt="您的输入有误！\n方法1：输入一个正整数x，从1到x之间随机选取一个整数\n方法2：输入两个正整数x-y（中间是减号），从x到y之间随机选取一个正整数\n请重新输入范围：")
        return {**state, "min": _min, "max": _max}


dice = on_command("dice", aliases={"掷骰", "随机数", "random", "Dice", })


@dice.handle()
async def _(matcher:Matcher, state: T_State, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        state["range"] = plain_text
        dice.set_arg(matcher,key ="range",message=args)


@dice.got("range", prompt="随机数说明：\n方法1：输入一个正整数x，从1到x之间随机选取一个整数\n方法2：输入两个正整数x-y（中间是减号），从x到y之间随机选取一个正整数\n请输入范围：")
async def _(event: GroupMessageEvent, state: T_State = Depends(get_random_nums)):
    _min = state["min"]
    _max = state["max"]
    randomint = random.randint(_min, _max)
    report = f"随机数的结果是:{randomint}"
    await dice.finish(report)

version = on_command("version", aliases={"版本号"})
command_list = on_command("cmd_list", aliases={"指令表", "指令列表"})

@version.handle()
async def _(matcher:Matcher):
    await version.finish("小师妹ver0.0.1")


def initImage(txt):
    rows = len(txt.split("\n"))
    img = Image.new("RGBA",(700,rows*26+10),(255,255,255))
    dr = ImageDraw.Draw(img)
    font = ImageFont.truetype("msyh.ttc",20)
    dr.text((10,5),txt,font=font,fill = "#000000")
    return img

def get_command_list():
    path = __file__.strip("\\__init__.py")
    path = path[:path.rfind("\\")]
    initfiles = []
    report = "全部指令列表如下，每行的几个指令代表同一种指令\n指令之前加上“!”或者“/，如：/武器”\n"
    for root,dirs,files in os.walk(path):
        if "__init__.py" in files:
            initfiles.append(root+"\\__init__.py")
    for item in initfiles:
        with open(item, "r",encoding="utf8") as f:
            txt = f.read()
            cmd = re.findall(r"on_command\(\"(\S+)\", ?aliases ?= ?\{(.+)}\)", txt)
            for items in cmd:
                cmd_name = items[0]
                cmd_aliases = items[1].split(",")
                report = report + "\n" + cmd_name + "," + ",".join(cmd_aliases)
    for items in image_reply.keys():
        report = report + "\n" + items + "," + " , ".join(image_reply[items])
    img = initImage(report)
    return img



@command_list.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text():
        return
    bio = BytesIO()
    get_command_list().save(bio,format="PNG")
    await command_list.finish(MessageSegment.image(bio))


