"""Finite editorial fallback library; published variants are not reused."""
import json
from pathlib import Path

LESSONS = [
 ('one-bottle', 'Start your home bar with one bottle, not a shopping spree', 'A home bar does not have to start with a cabinet full of spirits. Start with one bottle you enjoy and learn a few drinks that use it. Measure your pours, practice the method, and only add another bottle when it unlocks something you actually want to make. This keeps the learning manageable and the shopping intentional. A bottle-by-bottle plan gives each purchase a purpose, instead of leaving you with ingredients you never use.', ['bourbon bottle bar','cocktail measuring jigger','bartender pouring','cocktail glass','home bar']),
 ('six-bottles', 'Six bottles can be a plan, not a collection', 'Buying more bottles does not automatically make you better at cocktails. Think about combinations before you shop. A spirit, a vermouth, or a bitter ingredient can each unlock different styles when paired thoughtfully. Learn what each bottle contributes and keep a small list of drinks you want to practice. The useful question is not how many bottles fit on the shelf. It is which next bottle helps you make a drink you will enjoy.', ['home bar bottles','bartender measuring','cocktail stirring','cocktail glass','bartender pouring']),
 ('recipe-plan', 'Stop collecting recipes you cannot make', 'Saving a cocktail recipe is easy. Making it is harder when every new recipe needs a different shopping list. Choose a small group of drinks that share ingredients, then practice them with measured pours. Notice which ingredients overlap and which techniques you repeat. That turns a scattered list of saved recipes into a practical learning plan. Start small, use the bottles you have, and add ingredients deliberately instead of buying everything at once.', ['cocktail ingredients','cocktail jigger','bartender stirring','cocktail pouring','home bar']),
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
