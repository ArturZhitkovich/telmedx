import textwrap

from PIL import ImageFont, Image, ImageDraw


def annotate_image(original_image, text):
    """
    :param original_image:
    :type original_image: Image.Image
    :param text:
    :type text: str
    :return:
    :rtype: Image.Image
    """
    font = ImageFont.truetype('fonts/DroidSans.ttf', 16)

    original = original_image
    (orig_w, orig_h) = original.size

    # New image with an expanded canvas
    expanded = Image.new('RGB', (orig_w, orig_h + 50), (255, 255, 255))

    # Paste original here, original is now "expanded"
    expanded.paste(original)

    # Get drawing context for text on top of expanded
    d = ImageDraw.Draw(expanded)

    margin = 5
    offset = orig_h + 2
    for line in textwrap.wrap(text, width=85):
        d.text((margin, offset), line, font=font, fill=(0, 0, 0, 255))
        offset += font.getsize(line)[1]

    return expanded
