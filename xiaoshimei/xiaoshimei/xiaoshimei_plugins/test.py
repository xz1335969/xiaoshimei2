from PIL import Image, ImageDraw, ImageFont
from _globals import randomlist
from copy import deepcopy

img = Image.new("RGBA", (450, 450), "#FFFFFF")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("msyh.ttc", 18)
font2 = ImageFont.truetype("msyh.ttc", 28)

for x in range(11):
    draw.line([x * 42 + 28, 28, x * 42 + 28, 450], fill="black", width=2)
    draw.line([28, x * 42 + 28, 450, x * 42 + 28], fill="black", width=2)


for i in range(10):
    item = chr(i + 65)
    draw.text((41 + 43 * i, 2), text=item, font=font, fill="black")
    draw.text((7, 41 + 42 * i), text=str(i), font=font, fill="black")


for x in range(10):
    for y in range(10):
        if mine_map[10 * y + x] == 0:
            if around_mine_num[10 * y + x] == 0:
                draw.text((36 + 42 * x, 36 + 42 * y), str(around_mine_num[10 * y + x]), fill="black", font=font2)
            else:
                pass
        else:
            draw.rectangle((x * 42 + 30, y * 42 + 30,x * 42 + 69, y * 42 + 69), fill="#bbbbbb")

if __name__ == "__main__":
    img.show()
