import random

# ASCII BANNERS
ASCII_BANNERS = [
    r"""
     /\_/\  
    ( o.o ) 
     > ^ <    AniList Backup & Restore
    """,
    r"""
     |\_/|                  
     (°.°)   < meow~        
     (   )    ANIME POWERS!         
     (___)                 
    """,
    r"""
      ／l、
    （ﾟ､ ｡７
      l、 ~ヽ
      じしf_,)ノ   List Saver
    """,
    r"""
     /\     /\
    {  `---'  }
    {  O   O  }
    ~~>  V  <~~
     \  \|/  /
      `-----'____
      /     \    \_
     {       }\  )_\_   AniList Tool
     |  \_/  |/ /  /
      \__/  /(_/  /
        (__/
    """,
]

QUOTES = [
    "“The world isn’t perfect. But it’s there for us, doing the best it can. That’s what makes it so damn beautiful.” – Roy Mustang",
    "“No one knows what the future holds. That’s why its potential is infinite.” – Rintarou Okabe",
    "“Whatever you lose, you’ll find it again. But what you throw away you’ll never get back.” – Kenshin Himura",
    "“To know sorrow is not terrifying. What is terrifying is to know you can't go back to happiness you could have.” – Matsumoto Rangiku",
    "“A lesson without pain is meaningless.” – Edward Elric",
    "“If you can’t find a reason to fight, then you shouldn’t be fighting.” – Akame",
    "“Do not fear death. Fear the unlived life.” – Nanny McPhee",
    "“No matter how deep the night, it always turns to day, eventually.” – Brook"
]

INTRO = (
    "Welcome, anime and manga lover!\n"
    "This tool helps you backup and restore your AniList lists (anime & manga), "
    "with friendly anime vibes and full color.\n"
    "Type -help at any prompt for extra info."
)

OUTRO = (
    "Thanks for using the AniList Backup Tool! 🌸\n"
    "Keep your anime dreams safe and keep exploring new worlds!"
)

def print_banner():
    print(random.choice(ASCII_BANNERS))

def print_random_quote():
    print("\n" + random.choice(QUOTES) + "\n")

def print_intro():
    print(INTRO)

def print_outro():
    print("\n" + OUTRO + "\n")
    print_random_quote()
