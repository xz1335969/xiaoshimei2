from PIL import Image, ImageFont, ImageDraw

FONT_SIZE = 12  # 字号
FONT_FAMILY = 'msyh.ttc'  # 字体: 微软雅黑


def init_empty_bag(item_num=8):
	"""
	初始化空背包

	:return: Image: 空背包底图
	"""
	j = (item_num + 6) // 7  # 行数
	img = Image.new('RGBA', (326, j*46+4), (228, 222, 186))  # Size: 46 * 7 + 4
	block = Image.open(f'{__file__.strip("createImage.py")}img/block.png').convert('RGBA')  # 单物品格
	for row in range(7):
		for column in range(j):
			img.paste(block, (row * 46 + 2, column * 46 + 2))  # 覆盖绘制
	return img


def draw_border_text(drawable: ImageDraw, x: int, y: int, text, border, fill) -> None:
	"""
	画一个边框文字
	:param drawable: 可绘画对象
	:param x: 坐标
	:param y: 坐标
	:param text: 要绘画的内容
	:param border: 边框色
	:param fill: 填充色
	"""
	font = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)
	# 边框
	offsets = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]  # exclude: [0, 0]
	for ox, oy in offsets:
		drawable.text((x + ox, y + oy), text, font=font, fill=border)
	# 实际文字
	drawable.text((x, y), text, font=font, fill=fill)


def draw_item_by_list(image, array):
	"""
	根据数据列表绘制物品
	:param image: 空背包底图
	:param array: 物品列表 [{'name': '', 'count': 0}...]
	"""
	def_row = def_column = 7
	def_shape = (42, 42)  # 46 - 2 * 2
	drawable = ImageDraw.Draw(image)  # 需要转换才能写字
	f = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)

	for i, item in enumerate(array):
		r, c = i // def_row, i % def_column
		name = item.get('name', None)
		count = item.get('count', 1)

		if not name or i > 49:
			break
		img_item = Image.open(f'{__file__.strip("createImage.py")}img/{name}.png').convert('RGBA').resize(def_shape, Image.ANTIALIAS)
		x, y = 2 + c * 46, 2 + r * 46
		fw, fh = f.getsize(f'{count}')
		image.alpha_composite(img_item, (x + 2, y + 2))  # 叠加绘制

		if count != 1:  # 是否绘制数量
			fx = 46 * (c + 1) - 4 - fw
			fy = 46 * (r + 1) - 2 - fh
			draw_border_text(drawable, fx, fy, f'{count}', 'white', 'black')


if __name__ == '__main__':
	equips = [
		'pike', 'ghostaxe', 'boomerang', 'slingshot', 'keris', 'maya', 'sickle',
		'wand', 'snowman', 'Soffice', 'Sboomerang', None, None, None
	]
	test_array = [
		{'name': name, 'count': count}
		for name, count in zip(['0','1','4','5','8'], [3] * 5)
	]
	bag = init_empty_bag()
	draw_item_by_list(bag, test_array)
	# bag.convert('RGB').save('out.jpg', quality=95)  # jpeg
	bag.save('out.png')
