import random
import requests
from PIL import Image
from io import BytesIO
import json


from xiaoshimei.xiaoshimei_plugins.goldsystem.cls import *

test = on_command("测试")


@test.handle()
async def _(event: PrivateMessageEvent):
    print(event.json())
    print(event.sender.group_id)

