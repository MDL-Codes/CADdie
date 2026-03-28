import urllib.request
import urllib.parse
import json
import time

GIPHY_KEY = "key-here"
OUTPUT_FILE = "qotw/qotw_gifs.txt"

questions = [
    ("What are your plans for summer 2026?", "summer vacation excited"),
    ("What's the weirdest food combination you actually enjoy?", "weird food gross delicious"),
    ("If you were a professional wrestler, what would your entrance theme be?", "wrestling entrance epic"),
    ("Is a hotdog a sandwich?", "hotdog confused debate"),
    ("What's the most useless talent you have?", "useless skill funny"),
    ("If you could swap lives with any fictional character for a day, who would it be?", "character swap transform"),
    ("What's a superpower that sounds cool but would actually be super inconvenient?", "superpower backfire awkward"),
    ("If your life was a movie, what would the title be?", "dramatic movie trailer"),
    ("The item to your left is your only weapon in a zombie apocalypse. How screwed are you?", "zombie apocalypse scared"),
    ("Would you rather travel 100 years into the past or 100 years into the future?", "time travel"),
    ("If you could make one animal species talk, which one would it be?", "talking animal funny"),
    ("Does the cereal go in the bowl before or after the milk?", "cereal milk debate"),
    ("If you were on death row, what would your last meal be?", "last meal food"),
    ("Which emoji best describes your personality right now?", "emoji reaction funny"),
    ("Do you have a hidden talent that is actually just weird?", "weird talent surprised"),
    ("What is the absolute worst fashion trend of all time?", "bad fashion cringe"),
    ("Do you think aliens have visited Earth and are just hiding in plain sight?", "aliens hiding earth"),
    ("What is the ultimate pizza topping and why is it or isn't it pineapple?", "pineapple pizza disgusted"),
    ("If you went to Hogwarts, which house would you realistically be sorted into?", "sorting hat hogwarts"),
    ("What was your dream job when you were five years old?", "childhood dream job"),
    ("What was the first concert you ever attended?", "concert crowd excited"),
    ("What is the one meme that will never not be funny to you?", "meme laughing"),
    ("You can only eat one cuisine for the rest of your life. What is it?", "food choice impossible"),
    ("What is your go-to bad dance move?", "bad dancing awkward"),
    ("If you had to be on a reality TV show, which one would it be?", "reality tv show dramatic"),
    ("If you could have dinner with any celebrity (dead or alive), who is it?", "celebrity dinner fancy"),
    ("Who was your first cartoon character crush?", "cartoon crush animated"),
    ("You're stranded on a desert island and can only bring one physical object. What is it?", "desert island stranded"),
    ("What do you think your spirit animal is?", "spirit animal wild"),
    ("What's the worst haircut you've ever had?", "bad haircut regret"),
    ("What is your ultimate comfort food?", "comfort food cozy"),
    ("Are you a morning person or a night owl?", "morning sleepy tired"),
    ("What's the scariest movie you've ever seen?", "scary movie terrified"),
    ("If you could go on a vacation anywhere in the world right now, where would it be?", "vacation travel dream"),
    ("What is your go-to karaoke song?", "karaoke singing microphone"),
    ("What is your biggest, most irrational pet peeve?", "pet peeve annoyed"),
    ("What is something you collect that other people might find strange?", "weird collection hoarding"),
    ("On a scale of 1 to 10, how much of an introvert or extrovert are you?", "introvert extrovert personality"),
    ("Which board game are you most likely to start an argument over?", "board game argument"),
    ("If you could have any superpower, but only while you're asleep, what would it be?", "sleeping dream power"),
    ("What is your favorite season of the year and why?", "favorite season nature"),
    ("Coffee, tea, or neither?", "coffee tea morning"),
    ("What is the most-used app on your phone?", "phone addicted scrolling"),
    ("What was your favorite subject in school (besides lunch)?", "school subject learning"),
    ("What is the best holiday and why?", "holiday celebration festive"),
    ("If you had 5 minutes of fame, what would you want it to be for?", "five minutes fame spotlight"),
    ("What is the best prank you've ever pulled?", "prank funny gotcha"),
    ("If you could only read one book for the rest of your life, what would it be?", "reading books favorite"),
    ("What is an invention that doesn't exist yet but really should?", "invention idea lightbulb"),
    ("If you were a color, which color would you be?", "colorful rainbow personality"),
    ("What's the best piece of advice you'd give to your younger self?", "advice wisdom reflection"),
]

def fetch_gif(search):
    params = urllib.parse.urlencode({
        "api_key": GIPHY_KEY,
        "q": search,
        "limit": 1,
        "rating": "g",
        "lang": "en"
    })
    url = f"https://api.giphy.com/v1/gifs/search?{params}"
    with urllib.request.urlopen(url, timeout=10) as res:
        data = json.loads(res.read())
    if data["data"]:
        gif_id = data["data"][0]["id"]
        return f"https://media.giphy.com/media/{gif_id}/giphy.gif"
    return None

def main():
    links = []
    for i, (question, search) in enumerate(questions):
        print(f"[{i+1}/51] {question[:60]}...")
        try:
            link = fetch_gif(search)
            if link:
                links.append(link)
                print(f"       {link}")
            else:
                links.append("NOT_FOUND")
                print(f"       (no result)")
        except Exception as e:
            links.append("ERROR")
            print(f"       (error: {e})")
        time.sleep(0.1)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(links))

    found = len([l for l in links if l.startswith("http")])
    print(f"\nDone! {found}/51 GIFs written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()