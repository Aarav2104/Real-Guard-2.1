"""Synthetic content catalog for the Instagram-style prototype (all names and content are fictional)."""
CATS = ["Photography", "AI", "Tech", "Travel", "Food", "Fitness", "Music", "Art", "Fashion"]
CREATORS = {"Photography": ["lens.stories", "frame.by.arun", "the.film.lane"], "AI": ["neural.notes", "promptcraft", "ml.daily"],
            "Tech": ["devdesk.co", "byte.sized", "gadget.lab"], "Travel": ["wander.south", "trail.diaries", "passport.pages"],
            "Food": ["street.bites", "tastekitchen", "noodle.notes"], "Fitness": ["move.daily", "fit.with.mira", "ironroutine"],
            "Music": ["loop.sessions", "strings.and.things", "studio.nights"], "Art": ["ink.and.light", "canvas.club", "sketch.hour"],
            "Fashion": ["thread.theory", "thrift.studio", "street.style.in"]}
CAPS = {"Photography": ["Golden hour on a 35mm prime", "Street frames from the morning commute", "Shooting film again, no regrets"],
        "AI": ["Training a tiny model in 60 seconds", "Prompt patterns that actually work", "What a transformer sees in an image"],
        "Tech": ["Dev desk setup tour 2026", "Mechanical keyboards, explained", "Five gadgets worth the money"],
        "Travel": ["Hidden trail, golden hour", "Three days along the coast", "Packing light for a month"],
        "Food": ["Five-minute street-style noodles", "Sunday kitchen reset", "The soup that fixes everything"],
        "Fitness": ["Full-body routine, no equipment", "Mobility before the lift", "Twelve-minute morning flow"],
        "Music": ["Lo-fi guitar loop", "Studio night, take three", "Learning a song by ear"],
        "Art": ["Digital painting timelapse", "Ink and light study", "Sketchbook tour"],
        "Fashion": ["Thrift outfit remix", "Capsule wardrobe, week two", "Monsoon layers"]}

def _post(i):
    cat, k = CATS[i % 9], i // 9
    return {"id": f"p{i}", "cat": cat, "by": CREATORS[cat][k], "cap": f"{CAPS[cat][k]} #{cat.lower()}", "likes": 420 + (i * 1373) % 9800,
            "ncom": 3 + (i * 17) % 88, "age": ["2h", "5h", "1d", "2d", "3d", "6d"][i % 6], "kind": "reel" if i % 2 else "photo",
            "hue": (i % 9) * 40 + 15, "comments": [{"by": "mira.codes", "text": "Love the framing"}, {"by": "canvas.club", "text": "This is great"}]}

POSTS = [_post(i) for i in range(27)]
AD = {"id": "ad1", "ad": True, "cat": "Tech", "by": "nimbus_labs", "cap": "Apply for Software Engineering Internship", "name": "Software Engineering Internship (Nimbus Labs)", "likes": 0, "ncom": 0, "hue": 230}
