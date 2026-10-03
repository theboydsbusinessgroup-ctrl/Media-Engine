"""Finite editorial fallback library; published variants are not reused."""
import json
from pathlib import Path

LESSONS = [
 ('dilution', 'Water belongs in your cocktail', 'Water is an ingredient in a cocktail, even when it comes from ice. Stirring or shaking chills the drink and adds dilution. That water changes the texture and softens concentrated flavors. Taste the same drink before and after stirring and notice the difference. The goal is balance, not simply making the glass cold. Start with plenty of solid ice, then pay attention to taste as well as temperature.', ['ice in cocktail glass','bartender stirring cocktail','cocktail pouring close up','cocktail glass bar','bartender working']),
 ('shake-stir', 'Shake or stir? Start with the ingredients', 'Shaking and stirring do different jobs. Citrus and other thick ingredients usually benefit from shaking because it mixes them quickly and adds air. A spirit-forward drink usually benefits from stirring for a smooth texture. Neither technique is automatically better. Look at what is in the drink and the texture you want. Keep the glass cold, measure the ingredients, and compare the result. A good technique serves the recipe.', ['bartender shaking cocktail','bartender stirring cocktail','fresh citrus','cocktail pouring','cocktail glass']),
 ('measure', 'Your jigger is a consistency tool', 'A jigger is not just for beginners. Measuring makes a cocktail easier to repeat and easier to improve. If a drink tastes too sweet or too sharp, change one measured ingredient and taste again. Guessing every pour changes several variables at once. Start with a reliable recipe, measure each ingredient, and write down the adjustment you liked. That is how a single good drink becomes something you can make again.', ['cocktail measuring jigger','bartender pouring','cocktail glass','citrus cocktail','bartender making cocktail']),
 ('fresh-citrus', 'Taste your citrus before you pour', 'Lemons and limes are not identical from one batch to the next. Their flavor and acidity affect the balance of a sour. Measure the juice, taste the finished drink, and make small adjustments rather than adding a large extra pour. Fresh juice is a useful starting point, but tasting still matters. Keep your recipe as the baseline and let the ingredients in front of you guide the final balance.', ['fresh lemon','lime cocktail','bartender shaking','cocktail pouring','citrus garnish']),
 ('chill-glass', 'A cold drink deserves a cold glass', 'A cocktail can warm up quickly in a room-temperature glass. Chilling the glass before serving helps preserve the temperature you worked to create. Put the glass in a suitable chilled space or fill it with ice while you make the drink, then discard that ice before pouring. Use glassware safely and avoid sudden extreme temperature changes. Small preparation steps can make a finished cocktail feel more deliberate.', ['cocktail glass ice','bartender pouring cocktail','cold glass','bartender stirring','cocktail garnish']),
]


def evergreen_plan(root: Path) -> dict:
    used=set()
    for path in (root/'data/publications').glob('*.json'):
        receipt=json.loads(path.read_text())
        if str(receipt.get('model','')).startswith('editorial:'):
            used.add(receipt['model'])
    for slug,title,script,queries in LESSONS:
        model='editorial:v1:'+slug
        if model not in used:
            return {'title':title,'script':script,'description':title+' #Shorts #Bartending #Hospitality',
                'tags':['bartending','cocktails','home bar'],'hook_text':title,'broll_queries':queries,
                'topic':slug,'model':model}
    raise RuntimeError('Editorial fallback library exhausted; review new lessons before publishing')
