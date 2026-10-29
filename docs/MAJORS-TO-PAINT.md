# Majors to paint

All 22 Major Arcana are painted. Each card's object is listed in `MAJOR_OBJECT` in `tarot/cards.py`, and the files live in `tarot/objects/`.

If an object file is ever missing, its card falls back to its pixel sticker, and the tests check that fallback.

To repaint one, use the Pocket Coven shell map as the style reference, in the merwitch register: cyberpunk whimsy, Y2K, witchcore, painted and hyper-detailed, no text. Ask for a 4:5 image and cut the object out onto a transparent background. A scene that won't cut out cleanly can stay a soft-edged vignette: add its file name to `FRAMED` in `tarot/cards.py` so it gets the drop shadow without the white outline. The Quiet Room's door is one of these.
