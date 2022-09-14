import random
import requests
from PIL import Image
from io import BytesIO
import json
import configparser

from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *


def text_cmd(command_name: str, aliases: set[str, ...], text: str | Message | MessageSegment):
    text_command = on_command(command_name, aliases=aliases)

    @text_command.handle()
    async def _(args: Message = CommandArg()):
        plain_text = args.extract_plain_text()
        if plain_text:
            return
        await text_command.finish(text)

    return command_name


def image_cmd(command_name: str, aliases: set[str, ...]):
    image_command = on_command(command_name, aliases=aliases)

    @image_command.handle()
    async def _(args: Message = CommandArg()):
        plain_text = args.extract_plain_text()
        if plain_text:
            return
        url = __file__.strip("__init__.py") + f"img\\{command_name}.png"
        await image_command.finish(MessageSegment.image("file:///" + url))

    return command_name


customization = on_command("customization", aliases={"自定义回复", "自定义指令"})


@customization.handle()
async def _(bot:Bot,event: GroupMessageEvent, state: T_State, arg: Message = CommandArg()):
    if await GROUP_ADMIN(bot,event) or GROUP_OWNER(bot,event):
        args = arg.extract_plain_text().strip().split()
        if len(args) >= 1:
            state["question"] = args[0].strip()
            if len(args) >= 2:
                state["answer"] = args[1]
    else:
        await customization.finish("权限不足")
        return


@customization.got("question", prompt="请输入您的自定义指令名称")
async def _(event: GroupMessageEvent, state: T_State, arg: str = ArgPlainText("question")):
    with open(__file__.strip("__init__.py") + "customization.json", "r") as f:
        json_code = f.read()
        json_code = json.loads(json_code)
        questions = json_code["questions"]
        question = arg.strip()
        if question in questions:
            await customization.finish("添加失败，已存在这个自定义指令。")
            return
    state["question"] = arg


@customization.got("answer", prompt="请输入您的自定义指令回复")
async def _(event: GroupMessageEvent, state: T_State, arg: Message = Arg("answer")):
    arg_text = arg.extract_plain_text()
    if not arg_text:
        if arg[0].type == "image":
            url = arg[0].data["url"]
            response = requests.get(url)
            with open(__file__.strip("__init__.py") + "customization.json", "r") as f:
                json_code = f.read()
                json_code = json.loads(json_code)
                num = len(json_code["questions"])
            image = Image.open(BytesIO(response.content))
            image.save(f"{__file__.strip('__init__.py')}img\\custom_cmd{num}.png")
            state["answer"] = "img_reply"
        else:
            await customization.finish("不支持的回复类型")
            return
    else:
        state["answer"] = arg_text
    with open(__file__.strip("__init__.py") + "customization.json", "r") as f:
        json_code = f.read()
        json_code = json.loads(json_code)
        questions = json_code["questions"]
        question = state["question"]
        answers = json_code["answers"]
        answer = state["answer"]
        num = len(questions)
        questions.append(question)
        answers.append(answer)
        txt = json.dumps(json_code,ensure_ascii=False)
    with open(__file__.strip("__init__.py") + "customization.json", "w") as f:
        f.write(txt)
    if answer == "img_reply":
        image_cmd(f"custom_cmd{num}", {question,})
    else:
        text_cmd(f"custom_cmd{num}", {question,}, answer)
    await customization.finish("添加成功")


with open(__file__.strip("__init__.py") + "customization.json", "r") as f:
    json_code = f.read()
    json_code = json.loads(json_code)
    for i,(q, a) in enumerate(zip(json_code["questions"], json_code["answers"])):
        if a == "img_reply":
            image_cmd(f"custom_cmd{i}", {q,})
        else:
            text_cmd(f"custom_cmd{i}", {q,}, a)
