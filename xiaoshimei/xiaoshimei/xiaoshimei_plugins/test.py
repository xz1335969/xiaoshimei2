import requests
from PIL import Image,ImageDraw
from io import BytesIO
import json

if __name__ == "__main__":
    resp = requests.get(url="https://api.lolicon.app/setu/v2?size=small")
    img_url = json.loads(resp.text)["data"][0]["urls"]["small"]
    img = requests.get(img_url)
    img2 = Image.open(BytesIO(img.content))
    img2.show()
    img2.save(".\\temp.jpg")