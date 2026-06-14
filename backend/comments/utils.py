import html
import io
import random
import re
import string
from html.parser import HTMLParser

from django.conf import settings

ALLOWED_TAGS = set(settings.ALLOWED_HTML_TAGS)
ALLOWED_ATTRS = settings.ALLOWED_HTML_ATTRS


class HTMLTagValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self.errors.append(f'Tag <{tag}> is not allowed.')
            return
        self.tag_stack.append(tag)
        allowed = ALLOWED_ATTRS.get(tag, [])
        for attr_name, _ in attrs:
            if attr_name not in allowed:
                self.errors.append(f'Attribute "{attr_name}" is not allowed for tag <{tag}>.')

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS:
            return
        if not self.tag_stack or self.tag_stack[-1] != tag:
            self.errors.append(f'Tag </{tag}> does not match the opened tag.')
        else:
            self.tag_stack.pop()

    def get_errors(self):
        errors = list(self.errors)
        for tag in self.tag_stack:
            errors.append(f'Tag <{tag}> is not closed.')
        return errors


def validate_html_tags(text: str) -> bool:
    validator = HTMLTagValidator()
    validator.feed(text)
    return len(validator.get_errors()) == 0


def sanitize_html(text: str) -> str:
    escaped = html.escape(text)
    for tag in settings.ALLOWED_HTML_TAGS:
        escaped = escaped.replace(f'&lt;{tag}&gt;', f'<{tag}>')
        escaped = escaped.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    escaped = re.sub(
        r'&lt;a href=&quot;([^&]+)&quot;( title=&quot;([^&]*)&quot;)?&gt;',
        lambda match: f'<a href="{match.group(1)}"{f" title=\"{match.group(3)}\"" if match.group(3) else ""}>',
        escaped,
    )
    escaped = escaped.replace('&lt;/a&gt;', '</a>')
    return escaped


def resize_image_if_needed(image_file):
    try:
        from PIL import Image
        from django.core.files.uploadedfile import InMemoryUploadedFile

        max_w = settings.MAX_IMAGE_WIDTH
        max_h = settings.MAX_IMAGE_HEIGHT

        img = Image.open(image_file)
        w, h = img.size

        if w <= max_w and h <= max_h:
            image_file.seek(0)
            return image_file

        ratio = min(max_w / w, max_h / h)
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)

        fmt = img.format or 'JPEG'
        content_type_map = {
            'JPEG': 'image/jpeg',
            'PNG': 'image/png',
            'GIF': 'image/gif',
        }
        content_type = content_type_map.get(fmt, 'image/jpeg')

        buffer = io.BytesIO()
        img.save(buffer, format=fmt)
        buffer.seek(0)

        return InMemoryUploadedFile(
            buffer,
            'ImageField',
            image_file.name,
            content_type,
            buffer.getbuffer().nbytes,
            None,
        )
    except Exception:
        image_file.seek(0)
        return image_file


def generate_captcha_text(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_captcha_image(text: str) -> bytes:
    from PIL import Image, ImageDraw, ImageFont
    import random

    width, height = 200, 60
    img = Image.new('RGB', (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    for _ in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(180, 180, 180), width=1)

    for _ in range(100):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        draw.point((x, y), fill=(random.randint(100, 200),) * 3)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    except Exception:
        font = ImageFont.load_default()

    char_x = 15
    for char in text:
        color = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 150),
        )
        y_offset = random.randint(-5, 5)
        draw.text((char_x, 12 + y_offset), char, font=font, fill=color)
        char_x += 28

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
