"""Holiday push content: slide decks for the Holiday Cocktail Party Menu Kit
and the Mobile Bartending Profit + Booking OS.

Each deck -> TikTok photo carousel (1080x1920 slides), a reel/Short
(same slides as video with an original music loop) and a Pinterest pin
(1000x1500). Slide kinds: hook, list, steps, menu, big, cta.
"""

KIT = "https://boydsbusiness.gumroad.com/l/holiday-cocktail-party-menu-kit"
OS = "https://boydsbusiness.gumroad.com/l/mobile-bartending-profit-booking-os"
GUIDE = "https://boydsbusiness.gumroad.com/l/yknubt"

KIT_CTA = {
    "kind": "cta",
    "eyebrow": "THE HOLIDAY COCKTAIL PARTY MENU KIT",
    "title": "3 printable menus.\n12 recipes.\nThe batch math done.",
    "body": "Shopping lists for 20 guests, a 3-day prep timeline and an editable batch calculator.",
    "price": "$12 · instant download",
    "foot": "Link in bio",
    "cover": "kit",
}

OS_CTA = {
    "kind": "cta",
    "eyebrow": "MOBILE BARTENDING PROFIT + BOOKING OS",
    "title": "Price every event\nfrom real costs.",
    "body": "Quote calculator, liquor planner, bookings pipeline, event profit log and dashboard. Excel + Google Sheets.",
    "price": "$29 · instant download",
    "foot": "Link in bio",
    "cover": "os",
}

DECKS = [
    # ---------------- Holiday Cocktail Party Menu Kit ----------------
    {
        "id": "k01", "product": "kit", "theme": "green",
        "slides": [
            {"kind": "hook", "eyebrow": "15 YEARS BEHIND THE BAR", "title": "Host like a bartender.\nStill enjoy your\nown party.", "sub": "The setup pros use at home  ↓"},
            {"kind": "steps", "title": "The bartender's\nholiday party setup", "items": [
                ("Pick 3 drinks + 1 zero-proof", "A short menu moves fast and wastes nothing."),
                ("Batch before the doorbell", "Spirits, syrup and bitters go in a bottle the day before."),
                ("Print the menu", "Guests order by name. Nobody asks what you've got."),
                ("Ice: 1–2 lb per guest", "You will run out of ice before you run out of booze."),
            ]},
            {"kind": "menu", "title": "Classic Holiday", "items": ["Holiday Old Fashioned", "Cranberry Moscow Mule", "Hugo Spritz", "Cranberry Rosemary Fizz"], "note": "ZERO PROOF: last drink", "color": "green"},
            KIT_CTA,
        ],
        "tiktok": "Host like a bartender and still enjoy your own party 🎄 The 4-step setup I use at home after 15 years behind the bar. Save this for your holiday party. Full kit: 3 printable menus, 12 recipes, batch math. Link in bio. #holidayparty #christmascocktails #hostingtips #bartender #cocktails",
        "ig": "Host like a bartender. Still enjoy your own party 🎄\n\n1. Pick 3 drinks + 1 zero-proof\n2. Batch before the doorbell\n3. Print the menu\n4. Ice: 1–2 lb per guest\n\nThe Holiday Cocktail Party Menu Kit has 3 printable menus, 12 bartender-tested recipes, shopping lists and the batch math done for you. $12, link in bio.\n\n#holidayparty #christmascocktails #hostingtips #cocktailrecipes #homebar #bartenderlife",
        "yt_title": "Host Like a Bartender This Holiday Season 🎄 #shorts",
        "pin_title": "Holiday Party Cocktail Menu: Host Like a Bartender",
        "pin_desc": "A bartender's holiday party setup: 3 drinks plus 1 zero-proof, batch before guests arrive, print the menu, and buy 1–2 lb of ice per guest. Get 3 printable holiday cocktail menus, 12 recipes and batch math in the Holiday Cocktail Party Menu Kit.",
    },
    {
        "id": "k02", "product": "kit", "theme": "burgundy",
        "slides": [
            {"kind": "hook", "eyebrow": "BARTENDER MATH", "title": "How much alcohol\nfor a 20-person\nholiday party?", "sub": "The rule I use for every event  ↓"},
            {"kind": "big", "eyebrow": "THE RULE", "big": "2 + 1", "title": "2 drinks per guest the first hour.\n1 per hour after that.", "body": "20 guests for 4 hours = 100 drinks."},
            {"kind": "list", "title": "What 100 drinks\nlooks like", "items": [
                "750 ml bottle ≈ 16 cocktails (1½ oz pours)",
                "750 ml wine ≈ 5 glasses",
                "Split it: about ⅓ cocktails, ⅓ wine, ⅓ beer or bubbles",
                "Plus a zero-proof option for drivers",
                "Ice: 20–40 lb. Yes, really.",
            ]},
            {"kind": "steps", "title": "Skip the math", "items": [
                ("Enter guests + hours", "The kit's calculator does the rest."),
                ("Get your shopping list", "Bottles, mixers, citrus and ice to buy."),
                ("Pour", "And actually enjoy the party."),
            ]},
            KIT_CTA,
        ],
        "tiktok": "How much alcohol do you need for a 20-person holiday party? 🎄 The bartender rule: 2 drinks per guest the first hour, 1 per hour after. Save this before you shop. The batch + shopping calculator is in my Holiday Cocktail Party Menu Kit, link in bio. #partyplanning #holidayparty #bartendertips #christmasparty #hostingtips",
        "ig": "How much alcohol for a 20-person holiday party? 🎄\n\nThe bartender rule: 2 drinks per guest the first hour, 1 per hour after that.\n20 guests × 4 hours = 100 drinks.\n\n• 750 ml bottle ≈ 16 cocktails\n• 750 ml wine ≈ 5 glasses\n• Ice: 20–40 lb\n\nThe Holiday Cocktail Party Menu Kit has a batch + shopping calculator that does this for you. Link in bio.\n\n#partyplanning #holidayparty #christmasparty #hostingtips #cocktails",
        "yt_title": "How Much Alcohol for a 20-Person Party? Bartender Math #shorts",
        "pin_title": "How Much Alcohol for a Holiday Party? Bartender Math",
        "pin_desc": "The bartender rule for party drinks: 2 per guest the first hour, 1 per hour after. 20 guests for 4 hours is about 100 drinks. A 750 ml bottle makes about 16 cocktails. Includes a batch and shopping calculator in the Holiday Cocktail Party Menu Kit.",
    },
    {
        "id": "k03", "product": "kit", "theme": "green",
        "slides": [
            {"kind": "hook", "eyebrow": "BATCHING 101", "title": "Make the cocktails\nbefore anyone\nshows up.", "sub": "How bars prep for a rush  ↓"},
            {"kind": "steps", "title": "Batch it like a bar", "items": [
                ("Day before", "Spirits, syrup and bitters go in a bottle in the fridge."),
                ("Stirred drinks", "Add about 20% water so it pours already diluted."),
                ("Day of", "Squeeze citrus the morning of. It fades fast."),
                ("At the pour", "Bubbles and garnish go in the glass, never the batch."),
            ]},
            {"kind": "menu", "title": "Cozy Winter\nWarmers", "items": ["Chai Spice Espresso Martini", "Hot Toddy", "Mulled Wine", "Spiced Apple Cider"], "note": "ZERO PROOF: last drink", "color": "burgundy"},
            KIT_CTA,
        ],
        "tiktok": "Make the cocktails BEFORE anyone shows up 🍸 How bars batch for a rush, and how you can at home. Every recipe in my Holiday Cocktail Party Menu Kit has single and 10-serving amounts. Link in bio. #batchcocktails #holidayparty #cocktailtips #bartender #partyideas",
        "ig": "Make the cocktails before anyone shows up 🍸\n\n• Day before: spirits, syrup and bitters in a bottle\n• Stirred drinks: add ~20% water\n• Day of: fresh citrus\n• At the pour: bubbles and garnish in the glass\n\nEvery recipe in the Holiday Cocktail Party Menu Kit comes in single and 10-serving amounts. Link in bio.\n\n#batchcocktails #holidayparty #cocktailtips #hostingtips #homebar",
        "yt_title": "Batch Your Holiday Cocktails Like a Bartender #shorts",
        "pin_title": "How to Batch Cocktails for a Holiday Party",
        "pin_desc": "Batch cocktails like a bar: spirits, syrup and bitters the day before, about 20% water for stirred drinks, fresh citrus the day of, bubbles and garnish at the pour. 12 holiday recipes with 10-serving amounts in the Holiday Cocktail Party Menu Kit.",
    },
    {
        "id": "k04", "product": "kit", "theme": "midnight",
        "slides": [
            {"kind": "hook", "eyebrow": "NEW YEAR'S EVE", "title": "Your NYE bar\nmenu is done.", "sub": "3 drinks + 1 zero-proof"},
            {"kind": "menu", "title": "New Year's Eve\nSparkle", "items": ["French 75", "Negroni Sbagliato", "Classic Champagne Cocktail", "Sparkling Pomegranate"], "note": "ZERO PROOF: last drink", "color": "midnight"},
            {"kind": "list", "title": "Why this menu works", "items": [
                "One case of bubbles covers all four drinks",
                "Three of them are built right in the glass",
                "The zero-proof one looks just as festive",
                "Batch the French 75 base ahead of time",
            ]},
            KIT_CTA,
        ],
        "tiktok": "Your New Year's Eve bar menu is done 🥂 French 75, Negroni Sbagliato, Champagne Cocktail and a zero-proof Sparkling Pomegranate. One case of bubbles covers all four. Printable menu in my Holiday Cocktail Party Menu Kit, link in bio. #newyearseve #nyeparty #champagnecocktails #cocktails #partyideas",
        "ig": "Your New Year's Eve bar menu is done 🥂\n\n• French 75\n• Negroni Sbagliato\n• Classic Champagne Cocktail\n• Sparkling Pomegranate (zero proof)\n\nOne case of bubbles covers all four. Printable + editable menu in the Holiday Cocktail Party Menu Kit. Link in bio.\n\n#newyearseve #nyeparty #champagnecocktails #cocktailmenu #hostingtips",
        "yt_title": "The Easiest New Year's Eve Cocktail Menu 🥂 #shorts",
        "pin_title": "New Year's Eve Cocktail Menu: 3 Drinks + Zero-Proof",
        "pin_desc": "An easy NYE bar menu: French 75, Negroni Sbagliato, Classic Champagne Cocktail and a zero-proof Sparkling Pomegranate. One case of sparkling wine covers all four. Printable and editable menu in the Holiday Cocktail Party Menu Kit.",
    },
    {
        "id": "k05", "product": "kit", "theme": "burgundy",
        "slides": [
            {"kind": "hook", "eyebrow": "ZERO PROOF", "title": "Non-drinkers\ndeserve better\nthan soda.", "sub": "3 that look like the real thing  ↓"},
            {"kind": "list", "title": "Zero-proof drinks\nthat don't feel like\nan afterthought", "items": [
                "Cranberry Rosemary Fizz",
                "Spiced Apple Cider",
                "Sparkling Pomegranate",
                "Same glass, same garnish as the cocktails",
                "Put it ON the menu, not behind the counter",
            ]},
            {"kind": "big", "eyebrow": "BARTENDER TIP", "big": "Same glass.", "title": "Serve it exactly like\nthe cocktails.", "body": "Nobody should have to explain why they're not drinking."},
            KIT_CTA,
        ],
        "tiktok": "Non-drinkers deserve better than a can of soda 🍹 Three zero-proof holiday drinks that look just like the cocktails. All three are on the menus in my Holiday Cocktail Party Menu Kit. Link in bio. #mocktails #zeroproof #holidaydrinks #sobercurious #holidayparty",
        "ig": "Non-drinkers deserve better than soda 🍹\n\n• Cranberry Rosemary Fizz\n• Spiced Apple Cider\n• Sparkling Pomegranate\n\nSame glass, same garnish, right on the menu. All three are in the Holiday Cocktail Party Menu Kit. Link in bio.\n\n#mocktails #zeroproof #holidaydrinks #sobercurious #hostingtips",
        "yt_title": "3 Holiday Mocktails That Look Like Cocktails #shorts",
        "pin_title": "3 Holiday Mocktails for Your Party Menu",
        "pin_desc": "Zero-proof holiday drinks that don't feel like an afterthought: Cranberry Rosemary Fizz, Spiced Apple Cider and Sparkling Pomegranate. Serve them in the same glass with the same garnish. Recipes and printable menus in the Holiday Cocktail Party Menu Kit.",
    },
    {
        "id": "k06", "product": "kit", "theme": "green",
        "slides": [
            {"kind": "hook", "eyebrow": "PREP TIMELINE", "title": "Hosting this\nweekend? Start\n3 days out.", "sub": "The countdown I use  ↓"},
            {"kind": "steps", "title": "Party countdown", "items": [
                ("3 days out", "Shop bottles, mixers and garnish. Print menus."),
                ("2 days out", "Make syrups. They keep for weeks."),
                ("1 day out", "Batch the base. Chill glassware if you have room."),
                ("Day of", "Citrus, ice, garnish. Set the bar 1 hour early."),
            ]},
            {"kind": "big", "eyebrow": "THE ONE MISTAKE", "big": "Ice.", "title": "Buy double what\nyou think you need.", "body": "1–2 lb per guest. It's the first thing every party runs out of."},
            KIT_CTA,
        ],
        "tiktok": "Hosting this weekend? Start 3 days out 🗓️ The countdown I use so I'm not stuck behind my own bar all night. Full prep timeline + shopping lists in my Holiday Cocktail Party Menu Kit, link in bio. #partyprep #holidayhosting #christmasparty #hostingtips #cocktails",
        "ig": "Hosting this weekend? Start 3 days out 🗓️\n\n3 days: shop + print menus\n2 days: make syrups\n1 day: batch the base\nDay of: citrus, ice, garnish\n\nAnd buy double the ice you think you need. Full timeline + shopping lists in the Holiday Cocktail Party Menu Kit. Link in bio.\n\n#partyprep #holidayhosting #christmasparty #hostingtips #homebar",
        "yt_title": "Holiday Party Prep Timeline From a Bartender #shorts",
        "pin_title": "Holiday Party Prep Timeline (Bartender's Countdown)",
        "pin_desc": "A 3-day holiday party countdown: shop and print menus 3 days out, make syrups 2 days out, batch the base the day before, then citrus, ice and garnish the day of. Buy 1–2 lb of ice per guest. Full timeline in the Holiday Cocktail Party Menu Kit.",
    },
    {
        "id": "k07", "product": "kit", "theme": "midnight",
        "slides": [
            {"kind": "hook", "eyebrow": "LAST-MINUTE GIFT", "title": "Gift for the\nfriend who always\nhosts.", "sub": "Arrives in their inbox in seconds"},
            {"kind": "list", "title": "What they get", "items": [
                "3 ready-to-print bar menus",
                "12 bartender-tested recipes",
                "Single + 10-serving amounts",
                "Shopping lists for 20 guests",
                "Editable menus + batch calculator",
            ]},
            {"kind": "big", "eyebrow": "PRO MOVE", "big": "+ 1 bottle", "title": "Pair it with a bottle\nfrom the menu.", "body": "Now it's a party in a bag."},
            KIT_CTA,
        ],
        "tiktok": "Last-minute gift for the friend who always hosts 🎁 3 printable bar menus, 12 recipes and the batch math, delivered instantly. Pair it with a bottle from the menu. Link in bio. #giftideas #lastminutegifts #hostessgift #holidayparty #cocktails",
        "ig": "Last-minute gift for the friend who always hosts 🎁\n\n3 printable bar menus, 12 bartender-tested recipes, shopping lists and a batch calculator, delivered to their inbox instantly. Pair it with a bottle from the menu and it's a party in a bag.\n\nHoliday Cocktail Party Menu Kit, $12. Link in bio.\n\n#giftideas #hostessgift #lastminutegifts #holidayparty #cocktaillover",
        "yt_title": "Last-Minute Gift for the Friend Who Always Hosts 🎁 #shorts",
        "pin_title": "Last-Minute Hostess Gift: Printable Cocktail Party Kit",
        "pin_desc": "A last-minute gift for the friend who always hosts: 3 printable holiday bar menus, 12 bartender-tested recipes, shopping lists and a batch calculator, delivered instantly. Pair it with a bottle from the menu.",
    },
    {
        "id": "k08", "product": "kit", "theme": "burgundy",
        "slides": [
            {"kind": "hook", "eyebrow": "POV", "title": "You spent your\nwhole party\nmaking drinks.", "sub": "Here's how bartenders avoid that  ↓"},
            {"kind": "steps", "title": "Get out from\nbehind the bar", "items": [
                ("Batch 2 of the 3 drinks", "Guests pour their own from a pitcher."),
                ("Make 1 drink built in the glass", "Spritz or mule: pour, top, garnish, done."),
                ("Set a self-serve garnish tray", "Citrus wheels, rosemary, cranberries."),
                ("Put the menu where the line forms", "Nobody asks you what to make."),
            ]},
            KIT_CTA,
        ],
        "tiktok": "POV: you spent your whole party making drinks 😩 How bartenders get out from behind the bar at their own parties. Menus, recipes and batch amounts in my Holiday Cocktail Party Menu Kit, link in bio. #hostingtips #holidayparty #bartenderlife #partyhacks #cocktails",
        "ig": "POV: you spent your whole party making drinks 😩\n\n• Batch 2 of the 3 drinks\n• Make 1 built right in the glass\n• Self-serve garnish tray\n• Menu where the line forms\n\nMenus, recipes and batch amounts in the Holiday Cocktail Party Menu Kit. Link in bio.\n\n#hostingtips #holidayparty #partyhacks #homebar #cocktails",
        "yt_title": "Stop Spending Your Whole Party Making Drinks #shorts",
        "pin_title": "Self-Serve Holiday Bar Setup: Party Hosting Tips",
        "pin_desc": "How to host without being stuck behind the bar: batch 2 of your 3 drinks, make 1 built in the glass, set up a self-serve garnish tray and put the printed menu where the line forms. Menus and recipes in the Holiday Cocktail Party Menu Kit.",
    },
    # ---------------- Mobile Bartending Profit + Booking OS ----------------
    {
        "id": "b01", "product": "os", "theme": "cream",
        "slides": [
            {"kind": "hook", "eyebrow": "FOR MOBILE BARTENDERS", "title": "5 costs missing\nfrom your\nquote.", "sub": "And why your 'good month' paid less than it should have  ↓"},
            {"kind": "list", "title": "Price these in,\nevery time", "items": [
                "Setup and breakdown hours, not just service hours",
                "Ice, cups, napkins, garnish",
                "Drive time and mileage",
                "Card processing fees (about 3%)",
                "Your minimum. Never quote below it.",
            ]},
            {"kind": "big", "eyebrow": "THE CHECK", "big": "$ / hour", "title": "Divide profit by\nevery hour you worked.", "body": "Including the drive and the cleanup. That's your real rate."},
            OS_CTA,
        ],
        "tiktok": "Mobile bartenders: 5 costs you forgot to put in your quote 🍸 Setup hours, ice and supplies, drive time, card fees and your minimum. I built a workbook that prices every event from real costs. Link in bio. #mobilebartending #bartenderbusiness #mobilebar #eventbartender #smallbusinesstips",
        "ig": "Mobile bartenders: 5 costs you forgot to put in your quote 🍸\n\n1. Setup + breakdown hours\n2. Ice, cups, napkins, garnish\n3. Drive time and mileage\n4. Card fees (~3%)\n5. Your minimum\n\nThe Mobile Bartending Profit + Booking OS prices every event from real costs and never quotes below your minimum. Link in bio.\n\n#mobilebartending #mobilebar #bartenderbusiness #eventbartender #bartending",
        "yt_title": "Mobile Bartenders: 5 Costs Missing From Your Quote #shorts",
        "pin_title": "Mobile Bartending Pricing: 5 Costs to Include in Every Quote",
        "pin_desc": "Price mobile bartending events from real costs: setup and breakdown hours, ice and supplies, drive time, card fees and your minimum. The Mobile Bartending Profit + Booking OS is an Excel and Google Sheets workbook with a quote calculator, liquor planner and bookings pipeline.",
    },
    {
        "id": "b02", "product": "os", "theme": "cream",
        "slides": [
            {"kind": "hook", "eyebrow": "MOBILE BAR STAFFING", "title": "How many\nbartenders for\n100 guests?", "sub": "The ratio I've used for years  ↓"},
            {"kind": "big", "eyebrow": "THE RATIO", "big": "1 : 50", "title": "One bartender for\nevery 50 guests.", "body": "Full bar, cocktails on the menu. Beer and wine only can stretch further."},
            {"kind": "big", "eyebrow": "THE DRINK ESTIMATE", "big": "2 + 1", "title": "2 drinks per guest the first\nhour, 1 per hour after.", "body": "That number drives your liquor list, your ice and your staffing."},
            OS_CTA,
        ],
        "tiktok": "How many bartenders for 100 guests? 🍸 1 per 50 for a full bar. And the drink estimate every event planner should know. My workbook auto-staffs from your guest count. Link in bio. #mobilebartending #eventplanning #bartendertips #weddingbar #mobilebar",
        "ig": "How many bartenders for 100 guests? 🍸\n\nThe ratio: 1 bartender per 50 guests for a full bar.\nThe drink estimate: 2 per guest the first hour, 1 per hour after.\n\nThe Mobile Bartending Profit + Booking OS auto-staffs from your guest count and estimates drinks for you. Link in bio.\n\n#mobilebartending #mobilebar #eventbartender #weddingbar #bartending",
        "yt_title": "How Many Bartenders for 100 Guests? #shorts",
        "pin_title": "How Many Bartenders Per Guest? Event Staffing Ratio",
        "pin_desc": "Event bar staffing: one bartender per 50 guests for a full bar, and estimate 2 drinks per guest the first hour and 1 per hour after. The Mobile Bartending Profit + Booking OS staffs and prices events automatically.",
    },
    {
        "id": "b03", "product": "os", "theme": "cream",
        "slides": [
            {"kind": "hook", "eyebrow": "MOBILE BAR OWNERS", "title": "No deposit?\nThat's not a\nbooking.", "sub": "3 rules that keep my calendar honest  ↓"},
            {"kind": "steps", "title": "Booking rules\nthat protect you", "items": [
                ("Non-refundable retainer", "No payment, no date on the calendar."),
                ("Balance due before the event", "Two weeks out is standard. Never on the night."),
                ("Written cancellation terms", "Decide them once. Send them with every quote."),
            ]},
            {"kind": "list", "title": "Track it all\nin one place", "items": [
                "Inquiry → Quoted → Booked → Completed",
                "Deposit, balance and balance-due date",
                "Follow-up date on every quote",
                "Close rate on the dashboard",
            ]},
            OS_CTA,
        ],
        "tiktok": "No deposit? That's not a booking 🙅 3 rules that keep a mobile bar's calendar honest. My workbook tracks deposits, balances and follow-ups for every event. Link in bio. #mobilebartending #smallbusiness #bartenderbusiness #eventbusiness #mobilebar",
        "ig": "No deposit? That's not a booking 🙅\n\n1. Non-refundable retainer\n2. Balance due before the event\n3. Written cancellation terms\n\nThe Mobile Bartending Profit + Booking OS tracks every inquiry, deposit, balance and follow-up date in one place. Link in bio.\n\n#mobilebartending #mobilebar #smallbusinesstips #eventbusiness #bartending",
        "yt_title": "Mobile Bartenders: No Deposit = No Booking #shorts",
        "pin_title": "Mobile Bartending Booking Rules: Deposits and Balances",
        "pin_desc": "Protect your mobile bar business: take a non-refundable retainer, collect the balance before the event and send written cancellation terms with every quote. Track inquiries, deposits and follow-ups in the Mobile Bartending Profit + Booking OS.",
    },
]
