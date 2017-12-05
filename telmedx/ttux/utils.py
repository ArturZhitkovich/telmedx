import textwrap

from PIL import ImageFont, Image, ImageDraw


def annotate_image(original_image, text=None, rotation=0):
    """
    :param original_image:
    :type original_image: Image.Image
    :param text:
    :type text: str
    :return:
    :rtype: Image.Image
    """
    font = ImageFont.truetype('fonts/DroidSans.ttf', 16)
    (orig_w, orig_h) = original_image.size
    rotated = original_image.rotate(rotation)

    # Only expand the canvas when we have text for it
    if text:
        # New image with an expanded canvas
        # COLOR, HEIGHT, RBG VALUES 
        ret = Image.new('RGB', (orig_w, orig_h + 65), (255, 255, 255))

        # Paste original here, original is now "expanded"
        ret.paste(rotated)

        # Get drawing context for text on top of expanded
        d = ImageDraw.Draw(ret)

        margin = 8
        offset = orig_h + 4
        for line in textwrap.wrap(text, width=72):
            d.text((margin, offset), line, font=font, fill=(0, 0, 0, 255))
            offset += font.getsize(line)[1]
    else:
        ret = rotated

    return ret
