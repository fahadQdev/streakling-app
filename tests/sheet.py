"""Contact sheets: python3 sheet.py <prefix> [cols] [scale]"""
import sys, glob, os
from PIL import Image, ImageDraw
prefix = sys.argv[1]; cols = int(sys.argv[2]) if len(sys.argv) > 2 else 4; scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
files = sorted(glob.glob('shots/' + prefix + '__*.png'))
os.makedirs('sheets', exist_ok=True)
per = cols * 2
for page in range(0, len(files), per):
    chunk = files[page:page + per]
    ims = [Image.open(f) for f in chunk]
    w = max(i.width for i in ims); h = max(i.height for i in ims)
    tw, th = int(w * scale), int(h * scale) + 16
    out = Image.new('RGB', (tw * cols, th * ((len(ims) + cols - 1) // cols)), 'white')
    d = ImageDraw.Draw(out)
    for k, (f, im) in enumerate(zip(chunk, ims)):
        x, y = (k % cols) * tw, (k // cols) * th
        out.paste(im.resize((int(im.width * scale), int(im.height * scale))), (x, y + 16))
        d.text((x + 4, y + 2), os.path.basename(f).split('__')[1][:-4], fill='red')
    name = 'sheets/%s-%02d.png' % (prefix, page // per)
    out.save(name)
    print(name, len(chunk))
