import io
import random
import string
from html.parser import HTMLParser

import bleach
from django.conf import settings

ALLOWED_TAGS = set(settings.ALLOWED_HTML_TAGS)
ALLOWED_ATTRS = settings.ALLOWED_HTML_ATTRS
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


class HTMLTagValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []
        self.void_elements = {'br', 'hr', 'img', 'input', 'meta', 'link'}

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self.errors.append(f'Tag <{tag}> is not allowed.')
            return
        if tag not in self.void_elements:
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
    return bleach.clean(
        text,
        tags=settings.ALLOWED_HTML_TAGS,
        attributes=settings.ALLOWED_HTML_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def normalize_uploaded_image(image_file):
    from PIL import Image, ImageOps, UnidentifiedImageError
    from django.core.files.uploadedfile import InMemoryUploadedFile

    allowed_formats = {
        'JPEG': ('jpg', 'image/jpeg'),
        'PNG': ('png', 'image/png'),
        'GIF': ('gif', 'image/gif'),
    }

    ext = image_file.name.rsplit('.', 1)[-1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError('Allowed image formats: JPG, GIF, PNG.')

    try:
        image_file.seek(0)
        img = Image.open(image_file)
        img.verify()
        image_file.seek(0)
        img = Image.open(image_file)
        fmt = img.format
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError('Upload a valid JPG, GIF, or PNG image.')

    if fmt not in allowed_formats:
        raise ValueError('Allowed image formats: JPG, GIF, PNG.')

    max_size = (settings.MAX_IMAGE_WIDTH, settings.MAX_IMAGE_HEIGHT)
    should_resize = img.width > max_size[0] or img.height > max_size[1]

    if not should_resize:
        image_file.seek(0)
        return image_file

    if fmt == 'GIF':
        img.seek(0)
        img = ImageOps.contain(img.copy(), max_size, Image.LANCZOS)
    else:
        img = ImageOps.contain(img, max_size, Image.LANCZOS)

    if fmt == 'JPEG' and img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    extension, content_type = allowed_formats[fmt]
    stem = image_file.name.rsplit('.', 1)[0]
    filename = f'{stem}.{extension}'

    buffer = io.BytesIO()
    save_kwargs = {}
    if fmt == 'JPEG':
        save_kwargs.update({'quality': 88, 'optimize': True})
    img.save(buffer, format=fmt, **save_kwargs)
    buffer.seek(0)

    return InMemoryUploadedFile(
        buffer,
        'image',
        filename,
        content_type,
        buffer.getbuffer().nbytes,
        None,
    )


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
