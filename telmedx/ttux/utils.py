import textwrap

from PIL import ImageFont, Image, ImageDraw


def annotate_image(original_image, text=None, rotation=0, extend_by=50,
                   margin_top=2, margin_left=5):
    """
    :param original_image:
    :type original_image: Image.Image
    :param text:
    :type text: str
    :param rotation:
    :type rotation: int
    :param extend_by: Number of pixels to extend canvas by (bottom)
    :type extend_by: int
    :param margin_top:
    :type margin_top: int
    :param margin_left:
    :type margin_left: int
    :return:
    :rtype: Image.Image
    """
    font = ImageFont.truetype('fonts/DroidSans.ttf', 16)
    (orig_w, orig_h) = original_image.size
    rotated = original_image.rotate(rotation)

    # Only expand the canvas when we have text for it
    if text:
        # New image with an expanded canvas
        ret = Image.new('RGB', (orig_w, orig_h + extend_by), (255, 255, 255))

        # Paste original here, original is now "expanded"
        ret.paste(rotated)

        # Get drawing context for text on top of expanded
        d = ImageDraw.Draw(ret)

        margin = margin_left
        offset = orig_h + margin_top
        for line in textwrap.wrap(text, width=85):
            d.text((margin, offset), line, font=font, fill=(0, 0, 0, 255))
            offset += font.getsize(line)[1]
    else:
        ret = rotated

    return ret
