"""Render the five SVG concepts into a single shareable review sheet."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import fitz

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "design" / "favicon-concepts"
FILES = [
    ("01-v-orbit.svg", "V + 글로벌 궤도", "브랜드 · 해외 확장"),
    ("02-world-shield.svg", "글로벌 권리 보호", "세계 · 보호"),
    ("03-two-regions.svg", "국내 · 해외 연결", "두 영역 · 한 창구"),
    ("04-patent-route.svg", "특허 문서 + 세계", "출원 · 해외 절차"),
    ("05-global-compass.svg", "글로벌 방향 제시", "국가별 출원 경로"),
]


def font(size, bold=False):
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


canvas = Image.new("RGB", (1760, 630), "#edf3f5")
draw = ImageDraw.Draw(canvas)
draw.text((70, 40), "VON PATENT · FAVICON CONCEPTS", fill="#1686b8", font=font(21, True))
draw.text((70, 83), "국내에서 세계까지, 하나의 특허 상담 창구", fill="#102b34", font=font(39, True))
draw.text((70, 145), "브랜드 컬러를 살린 5가지 시안  |  크게 보기와 16px 브라우저 탭 크기 비교", fill="#617782", font=font(20))

for index, (filename, title, subtitle) in enumerate(FILES):
    x = 70 + index * 338
    y = 210
    draw.rounded_rectangle((x, y, x + 318, y + 360), radius=25, fill="white", outline="#1498d0" if index == 0 else "#d8e4e9", width=3 if index == 0 else 1)
    draw.text((x + 24, y + 20), f"0{index + 1}", fill="#7f9faa", font=font(18, True))
    if index == 0:
        draw.rounded_rectangle((x + 220, y + 17, x + 295, y + 47), radius=14, fill="#e6f5fb")
        draw.text((x + 231, y + 21), "적용 중", fill="#0874a6", font=font(14, True))
    document = fitz.open(stream=(DIR / filename).read_bytes(), filetype="svg")
    pixmap = document[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=True)
    icon = Image.frombytes("RGBA", (pixmap.width, pixmap.height), pixmap.samples)
    icon = icon.resize((152, 152), Image.Resampling.LANCZOS)
    canvas.paste(icon, (x + 83, y + 61), icon)
    draw.text((x + 24, y + 224), title, fill="#102b34", font=font(21, True))
    draw.text((x + 24, y + 263), subtitle, fill="#617782", font=font(16))
    draw.line((x + 24, y + 307, x + 294, y + 307), fill="#e3ebee", width=1)
    for size, dx in ((32, 28), (16, 136)):
        small = icon.resize((size, size), Image.Resampling.LANCZOS)
        canvas.paste(small, (x + dx, y + 319), small)
        draw.text((x + dx + size + 8, y + 321), f"{size}px", fill="#79909b", font=font(14))

canvas.save(DIR / "preview.png")

simple = [
    ("06-simple-globe.svg", "지구", "국내·해외를 하나로"),
    ("07-simple-route.svg", "연결 경로", "국경을 넘는 출원"),
    ("08-simple-shield.svg", "권리 보호", "특허 권리를 지키는 상징"),
]
canvas = Image.new("RGB", (1160, 590), "#edf3f5")
draw = ImageDraw.Draw(canvas)
draw.text((70, 40), "VON PATENT · SIMPLE FAVICON", fill="#1686b8", font=font(20, True))
draw.text((70, 83), "글자 없이, 더 단순하게", fill="#102b34", font=font(38, True))
draw.text((70, 145), "기존 로고의 진남색·파란색을 유지한 추가 시안 3종", fill="#617782", font=font(19))

for index, (filename, title, subtitle) in enumerate(simple):
    x = 70 + index * 350
    y = 210
    draw.rounded_rectangle((x, y, x + 326, y + 330), radius=24, fill="white", outline="#d8e4e9")
    draw.text((x + 25, y + 19), f"0{index + 6}", fill="#7f9faa", font=font(18, True))
    document = fitz.open(stream=(DIR / filename).read_bytes(), filetype="svg")
    pixmap = document[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=True)
    icon = Image.frombytes("RGBA", (pixmap.width, pixmap.height), pixmap.samples)
    icon = icon.resize((142, 142), Image.Resampling.LANCZOS)
    canvas.paste(icon, (x + 92, y + 48), icon)
    draw.text((x + 25, y + 204), title, fill="#102b34", font=font(23, True))
    draw.text((x + 25, y + 245), subtitle, fill="#617782", font=font(16))
    draw.line((x + 25, y + 283, x + 301, y + 283), fill="#e3ebee", width=1)
    for size, dx in ((32, 26), (16, 145)):
        small = icon.resize((size, size), Image.Resampling.LANCZOS)
        canvas.paste(small, (x + dx, y + 292), small)
        draw.text((x + dx + size + 8, y + 295), f"{size}px", fill="#79909b", font=font(14))

canvas.save(DIR / "preview-simple.png")
