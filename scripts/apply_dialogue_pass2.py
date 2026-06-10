#!/usr/bin/env python3
"""Second dialogue pass: British English, grammar, and stronger lines."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Exact replacements (longest keys first when applied)
REPLACEMENTS = [
    # Typos / choices
    ("Definately", "Definitely"),
    ("You drunk the whole thing", "You've drunk the whole thing"),
    ("Move with WSAD or the arrow keys", "Move with WASD or the arrow keys"),
    ("Acapella", "a cappella"),
    # Signs & objects
    ("Thats literally it", "That's literally it."),
    ("I dont know what else you want me to say", "I don't know what else you want me to say."),
    ("Right: More", "Right: More of town"),
    ("well well well. what do we have here", "Well, well, well. What have we got here?"),
    ("A gate blocks the way", "A sturdy gate blocks the path."),
    ("It seems like you have to talk to everyone first for the", "It looks like you need to speak to everyone in town before the"),
    ("gate to open?", "gate will open."),
    ("What kind of gate is this?", "What sort of gate needs a social battery to unlock?"),
    ("Its Mr Xadion", "It's Mr Xadion."),
    ("Are you here to grief me with your shocking", "Are you here to grief me with those shocking"),
    ("blitzcrank hooks", "Blitzcrank hooks again?"),
    ("Ribbit Ribbit", "Ribbit, ribbit!"),
    ("Very funny Liv", "Very funny, Liv."),
    ("Hey Froggy", "Hey, Froggy."),
    ("Wow, wont even say hi to lil ol me", "Wow. Won't even say hi to little old me?"),
    ("You hate me", "You hate me, don't you?"),
    ("\\}hi liv", "\\}Hi, Liv."),
    ("Dang. its sunny today", "Dang, it's sunny today."),
    ("It feels like a good day to catch up with", "Feels like the perfect day to catch up"),
    ("people", "with everyone in town."),
    ("Who do i see first?", "Who should I visit first?"),
    ("You are now free to explore the town, Talk and interact with", "You're free to explore Floroma Town. Talk to people and poke at"),
    ("lots of things. when you have spoken to everyone. you can", "everything you fancy. Once you've spoken to everyone, you can"),
    ("then go to the city via train to the right of town", "catch the train east to the city."),
    # TJ
    ("Hey TJ", "Hey, TJ!"),
    ("Beep Boop", "Beep boop."),
    ("Not much to say other than congrats on the 5", "Not much to report—congrats on five"),
    ("years and heres to another 5", "years on stream, and here's to five more."),
    ("Thank youuu!", "Thank you so much!"),
    ("haha will do", "Ha ha, will do."),
    ("Oh and one more thing", "Oh, and one more thing—"),
    ("10min ban on phan tommy plz <3", "ten-minute ban on Phan Tommy, please. <3"),
    ("be sure to remember to check the floor for any thumbtacks", "remember to check the floor for thumbtacks."),
    # Pig / test
    ("If you're able to talk to me and get over here", "If you can talk to me and reach me over here,"),
    ("Then something has gone horribly wrong", "then something has gone horribly wrong."),
    ("and Shane has messed up somewhere", "Shane has messed up somewhere."),
    # Conductor
    ("Want a ticket to the town?", "Fancy a ticket back to town?"),
    ("Great. the next train should be arriving soon", "Lovely. The next train should be along shortly."),
    ("Hello, Terribly sorry. it appears no trains are", "Hello there. Terribly sorry—it appears no trains are"),
    ("in service at the moment", "running at the moment."),
    ("You'll have to come back later", "You'll have to come back later."),
    ("Want a ticket to the city?", "Fancy a ticket to the city?"),
    # Angle
    ("Ay up liv", "Ay up, Liv."),
    ("How's it going mush", "How's it going, mush?"),
    ("Hey Angle, boy what did they do to you", "Hey, Angle, boy, what did they do to you?"),
    ("I know right, Shane did me dirty that rat", "I know, right? Shane did me dirty, the rat."),
    ("Apparently there are not enough hairstyles", "Apparently there aren't enough hairstyles"),
    ("that suit me, so this was the best they could", "that suit me, so this was the best they could"),
    ("Okay but like why are you in the kitchen?", "Okay, but why are you in the kitchen?"),
    ("Well liv, im glad you asked. because ive been", "Well, Liv, I'm glad you asked—I've been"),
    ("cooking up a storm", "cooking up a storm."),
    ("Big Ras Spinnah has been cooking with his", "Big Ras Spinnah has been cooking with his"),
    ("beats lately", "beats lately."),
    ("Yeah man, it was great", "Yeah, man, it was great."),
    ("\\}Except for the fact my usb drive broke", "\\}Except my USB drive died."),
    ("Nothing liv, dont you worry. i am in my prime", "Nothing, Liv—don't you worry. I'm in my prime."),
    ("I may have not been paid for my last set.", "I may not have been paid for my last set."),
    ("but when it comes to making music. im at the", "But when it comes to music, I'm at the"),
    ("Naw dont be saying none of this,", "Naw, don't go spreading any of this,"),
    ("In fact. i can prove it to ya.", "In fact, I can prove it to you."),
    ("I’m going to sing a cappella", "I'm going to sing a cappella."),
    ("Well guess im the first hater of DJ Angle", "Well, I suppose I'm DJ Angle's first hater."),
    # Gotti
    ("Hey Prize", "Hey, Prize."),
    ("Oh uh, Hey Liv", "Oh, uh—hey, Liv."),
    ("You got here just in time.", "You got here just in time."),
    ("Im currently building a bot that can...\\|", "I'm building a bot that can...\\|"),
    ("oh wait,\\| what does it do again", "oh wait—\\| what does it do again?"),
    ("Well anyway it will be sure to change the way", "Well, anyway—it'll change the way"),
    ("we livestream as we know it", "we livestream, mark my words."),
    ("Very nice", "Very nice."),
    ("Why are all these books so old", "Why are all these books so ancient?"),
    ("Oh no, are you sure, these are the most up", "Oh no—surely these are the most up-"),
    ("to date textbooks in the 90's", "to-date textbooks of the nineties?"),
    ("Prize, you realise that we are not in the 90's", "Prize, you do realise we're not in the nineties"),
    ("anymore right?", "any more, right?"),
    ("i am getting on a bit as you can see", "I am getting on a bit, as you can see."),
    ("Listen Liv, back in my day, we didn't have", "Listen, Liv—in my day we didn't have"),
    ("This new fangled Twitch livestreaming stuff.", "this new-fangled Twitch live-streaming lark."),
    ("Danngggg Shane. are you gonna take that?", "Danngggg, Shane—are you going to take that?"),
    # Liv house
    ("I really need some coffee before i head out", "I really need coffee before I head out."),
    ("Its Milo!", "It's Milo!"),
    ("Hey puppy", "Hey, puppy."),
    ("Its Liv's Diary", "It's Liv's diary."),
    ("Today i learned that i really shouldnt read", "Today I learned I really shouldn't read"),
    ("HA! i fooled you all!", "Ha! I fooled you all!"),
    ("Wait. did i just break the fourth wall?", "Wait—did I just break the fourth wall?"),
    ("Shame you didnt wake up in time to see her go", "Shame you didn't wake up in time to see her off."),
    ("Wow, really hits the spot", "Wow—that really hits the spot."),
    ("Its an empty cup", "It's an empty cup."),
    ("Drinking problem", "Bit of a drinking problem, that."),
    # Do's room
    ("its a picture of Obliviosa on the wall", "It's a picture of Obliviosa on the wall."),
    ("Damn i look good", "Damn, I look good."),
    ("Hi i am Do", "Hi, I am Do."),
    ("Hey Do, How ya doin", "Hey, Do—how are you doing?"),
    ("Im good, and i have good news", "I'm good, and I've got good news."),
    ("in creative writing for me.", "in creative writing—for me."),
    ("Isn't that ironic considering yall flame my", "Isn't that ironic, considering you lot flame my"),
    ("Thats great do. But you do confuse me sometimes", "That's great, Do. You do confuse me sometimes, though."),
    ("And now you have been confused yet again livvy", "And now I've confused you again, Livvy."),
    ("like im going a bit crazy", "like I'm going a bit mad."),
    ("Yeah i was gonna say, im surprised you havent", "Yeah, I was going to say—I'm surprised you haven't"),
    ("Anyway i gotta get back to this. Love you Liv!", "Anyway, I've got to get back to this. Love you, Liv!"),
    ("Do is now locked tf in", "Do is now locked in properly."),
    ("Its Angle's wardrobe", "It's Angle's wardrobe."),
    ("Its Gotti's wardrobe", "It's Gotti's wardrobe."),
    ("Hey, Dont go looking through my stuff", "Hey—don't go rummaging through my stuff."),
    # Cape / leave
    ("No turning back now", "No turning back now."),
    ("Once you leave, you wont be able to come back to this place.", "Once you leave, you won't be able to return here."),
    ("Its very peaceful up here, \\. Dont you think", "It's peaceful up here, \\. Don't you think?"),
    ("The wind howling, \\. Trees in the breeze", "The wind in the trees, \\. the light on the water"),
    ("You feel, \\. Relaxed", "You feel \\. calm."),
    ("This little game and this subathon might be coming to a", "The subathon is over, and this little game was part of"),
    # Clock / wake
    ("Its 10am, Yet Obliviosa is not awake", "It's 10 a.m., yet Obliviosa still isn't awake."),
    ("Its Noon, Yet Obliviosa is still not awake", "It's noon, and Obliviosa still isn't awake."),
    ("This girl...", "This girl…"),
    ("Yikes its 1pm. i overslept again", "Yikes—it's 1 p.m. I overslept again."),
    ("Hoo Boy. What time is it. ", "Hoo boy… what time is it?"),
    # Cam / KFC
    ("Cammy, We're not doing this again", "Cammy, we're not doing this again."),
    ("Its me the finger lickin good kernel saunders", "It's me—the finger-lickin' good Colonel Saunders."),
    ("What brings you down this way?", "What brings you down this way, fair missy?"),
    ("Deary me", "Dear me…"),
    ("Ya see that map on the wall there fair missy", "You see that map on the wall there, fair missy?"),
    ("What on earth did you just call me?", "What on earth did you just call me?"),
    ("I've been to every county in every state on", "I've been to every county in every state on"),
    ("that map. and ive been searchin for", "that map, and I've been searching for"),
    ("somethin", "something."),
    ("And what would that..\\^", "And that would be…?\\^"),
    ("On the search for some.", "On the hunt for some."),
    # Kotaro (partial — rest patched structurally)
    ("Hey Liv", "Hey, Liv!"),
    ("Hey Hey Kotaro. How are you", "Hey, hey, Kotaro! How are you?"),
    ("Well, i just wanted to say.", "Well, I just wanted to say—"),
    ("Thaaaank Youuuu", "Thank you so much!"),
    ("Awwww, You're so sweet", "Aww, you're so sweet."),
    # Junes — line fixed structurally
    ("Ohayo Liv", "Ohayo, Liv!"),
    # Nova
    ("Hey Nova, my queen", "Hey, Nova—my queen."),
    ("Omg Hi Liv", "OMG, hi, Liv!"),
    ("I didnt expect to see you. I just moved here", "I didn't expect to see you—I only just moved in."),
    ("Well i mean if you moved right next to me, of", "Well, if you moved in right next to me, of"),
    ("course im gonna come over.", "course I'm going to come over."),
    ("Yeah thats true i guess so.", "Yeah, that's fair, I suppose."),
    ("other stuff. Sorry for the lack of furniture.", "other bits. Sorry about the lack of furniture."),
    ("Yesterday i was sleeping on a floor mattress", "Yesterday I was on a floor mattress"),
    ("Aww im sorry girl", "Aww, I'm sorry, girl."),
    ("Its okay Liv, because you're here and you're", "It's okay, Liv—you're here, and you're"),
    ("Wow, i knew you wouldnt say no", "I knew you wouldn't say no."),
    ("Okay i gotta go and help alex to pretend to do", "Right, I've got to help Alex pretend to"),
    ("more moving stuff", "move more boxes."),
    ("Even though i'll secretly be doing my gacha", "Even though I'll secretly be doing my gacha"),
    ("Oh and before i go", "Oh—and before I go,"),
    ("Okay byee", "Okay, bye!"),
    # Bot
    ("I promise i will fix you up one day", "I promise I'll fix you up one day."),
    ("Im so sorry buddy.", "I'm so sorry, buddy."),
    ("Wait no... Dont say that. Thats not true!", "Wait, no—don't say that. That's not true!"),
    ("I never thought id feel so sad about a robot", "I never thought I'd feel this sad about a robot"),
    # Intro / tutorial
    ("Welcome to the Obliviosa Subathon game", "Welcome to the Obliviosa game!"),
    ("You will laugh (i hope)", "You will laugh (I hope)."),
    ("You will cry (maybe)", "You might cry (maybe)."),
    ("And you will have a good time (you better)", "And you will have a good time—you'd better."),
    ("This is you. Say Hello Obliviosa", "This is you. Say hello, Obliviosa."),
    ("No chat i will not do more pushups", "No, chat—I will not do more push-ups."),
    ("You are currently sleeping. (shock horror)", "You are currently asleep. (Shock horror.)"),
    ("Lets go over a few things while you're dreaming", "Let's go over a few things whilst you're dreaming."),
    ("Your in game appearance may not match your real life", "Your in-game appearance may not match real life"),
    ("appearance (sorry i tried)", "looks (sorry—I tried my best)."),
    ("And text like this where i am talking to the player", "And text like this is me talking to you, the player,"),
    ("I think that is all", "I think that's everything."),
    ("Are you ready to wake up bright and early", "Ready to wake up bright and early?"),
    ("Im Ready", "I'm ready"),
    ("Okay You're waking up now. We're not waiting around for", "Right—you're waking up now. We're not waiting for"),
    ("your lazy butt to wake up", "your lazy backside all day."),
    # Tree stump
    ("It's a tree stump.", "It's a tree stump."),
]

REPLACEMENTS.sort(key=lambda x: len(x[0]), reverse=True)


def fix_pronoun_i(text: str) -> str:
    """Capitalise standalone 'i' / 'i'm' style after other fixes."""
    text = re.sub(r"\bi'm\b", "I'm", text)
    text = re.sub(r"\bi've\b", "I've", text)
    text = re.sub(r"\bi'll\b", "I'll", text)
    text = re.sub(r"\bi'd\b", "I'd", text)
    # standalone i
    text = re.sub(r"(?<![A-Za-z])i(?![A-Za-z'])", "I", text)
    return text


def fix_contractions(text: str) -> str:
    rules = [
        (r"\bdont\b", "don't"),
        (r"\bdidnt\b", "didn't"),
        (r"\bwont\b", "won't"),
        (r"\bwouldnt\b", "wouldn't"),
        (r"\bhavent\b", "haven't"),
        (r"\bshouldnt\b", "shouldn't"),
        (r"\bcant\b", "can't"),
        (r"\bDont\b", "Don't"),
        (r"\bThats\b", "That's"),
        (r"\bthats\b", "that's"),
        (r"\bIts\b", "It's"),
        (r"\bIm\b", "I'm"),
        (r"\bLets\b", "Let's"),
        (r"\bHAVENT\b", "HAVEN'T"),
    ]
    for pat, rep in rules:
        text = re.sub(pat, rep, text)
    return text


def transform_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text
    # Preserve RPG Maker codes — skip heavy transform on code-only lines
    if text.startswith("\\.") and " " not in text.strip("\\."):
        return text
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
    text = fix_contractions(text)
    text = fix_pronoun_i(text)
    # Never replace substrings inside words (e.g. "do" in "don't")
    return text


def transform_parameters(code: int, params: list) -> list:
    if code == 401 and params:
        params = list(params)
        params[0] = transform_text(params[0])
        return params
    if code == 102 and params:
        params = list(params)
        choices = params[0]
        if isinstance(choices, list):
            params[0] = [transform_text(c) if isinstance(c, str) else c for c in choices]
        return params
    if code == 101 and params:
        params = list(params)
        if len(params) > 4 and isinstance(params[4], str):
            params[4] = transform_text(params[4])
        return params
    return params


def patch_kotaro_event(events: list) -> None:
    for ev in events:
        if not ev or ev.get("id") != 7 or ev.get("name") != "EV007":
            continue
        lst = ev["pages"][0]["list"]
        new_list = []
        skip_until = None
        for i, cmd in enumerate(lst):
            if skip_until is not None:
                if i <= skip_until:
                    continue
                skip_until = None
            if cmd.get("code") == 401:
                t = cmd["parameters"][0]
                if t == "5 years is actually long fucking time and im":
                    # Replace Kotaro's garbled block with clean lines
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "Five years is a bloody long time, and I'm"
                            ],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "really proud of everything you've pulled off."
                            ],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "I'm not in every stream lately, but the time"
                            ],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "I've spent here with you and chat has been"
                            ],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": ["amazing."],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "It's always dead chill with you. No wonder"
                            ],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "people stick around—you're talented,"
                            ],
                        }
                    )
                    new_list.append(
                        {
                            "code": 401,
                            "indent": cmd["indent"],
                            "parameters": [
                                "artistic, and properly charismatic."
                            ],
                        }
                    )
                    # skip until after old block (through "and charismatic you are. ")
                    for j in range(i + 1, len(lst)):
                        if lst[j].get("code") == 401:
                            tj = lst[j]["parameters"][0]
                            if tj.startswith("I'm very glad"):
                                skip_until = j - 1
                                break
                    continue
            new_list.append(cmd)
        ev["pages"][0]["list"] = new_list


def patch_junes_event(events: list) -> None:
    for ev in events:
        if not ev or ev.get("id") != 8:
            continue
        lst = ev["pages"][0]["list"]
        for i, cmd in enumerate(lst):
            if cmd.get("code") == 401 and cmd["parameters"][0] == "Hey Junes":
                # Liv should greet Junes
                prev = lst[i - 1] if i else None
                if prev and prev.get("code") == 101:
                    prev["parameters"] = list(prev["parameters"])
                    prev["parameters"][4] = "Liv"
                    prev["parameters"][0] = "LivFaceV2"
                cmd["parameters"] = ["Hey, Junes!"]
                break
            if cmd.get("code") == 401 and cmd["parameters"][0].startswith("AHH ARE"):
                cmd["parameters"] = ["AHH—ARE YOU FUCKING KIDDING ME?!"]
            if cmd.get("code") == 401 and cmd["parameters"][0].startswith("MY ADC"):
                cmd["parameters"] = [
                    "MY ADC LEFT ME TO DIE AGAIN!"
                ]


def process_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    if path.name.startswith("Map") and path.name != "MapInfos.json":
        if isinstance(data, dict) and "events" in data:
            patch_kotaro_event(data["events"])
            patch_junes_event(data["events"])
            changed = True

    def walk(obj):
        nonlocal changed
        if isinstance(obj, dict):
            if "code" in obj and "parameters" in obj:
                code = obj["code"]
                new_params = transform_parameters(code, obj["parameters"])
                if new_params != obj["parameters"]:
                    obj["parameters"] = new_params
                    changed = True
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)
    if changed:
        path.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
    return changed


def main():
    files = sorted(DATA.glob("*.json"))
    n = sum(1 for f in files if process_file(f))
    print(f"Updated {n} data files.")


if __name__ == "__main__":
    main()
