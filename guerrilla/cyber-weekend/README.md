# Cyber Weekend decks

Renders 3 decks x 4 slides, as 1080x1920 (`tall/`) and 1080x1350 (`feed/`) PNGs.

    python3 guerrilla/cyber-weekend/render_cyber.py

Requires Pillow (with raqm) and the Inter font. Uses the vendored `fonts/Gelasio[wght].ttf`; the render fails if it is missing.
