import os

# Get the home directory to make paths portable
HOME_DIR = os.path.expanduser("~")

# --- Gemini Model Names ---
PLANNER_MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation"
TTS_MODEL = "gemini-2.5-flash-preview-tts"
MUSIC_MODEL = 'models/lyria-realtime-exp'

# --- TTS Settings ---
# List of 24 languages supported by the Gemini TTS API. The planner will check against this list.
TTS_SUPPORTED_LANGUAGES = {
    'arabic', 'german', 'english', 'spanish', 'french', 'hindi', 'indonesian', 
    'italian', 'japanese', 'korean', 'portuguese', 'russian', 'dutch', 'polish', 
    'thai', 'turkish', 'vietnamese', 'romanian', 'ukrainian', 'bengali', 
    'marathi', 'tamil', 'telugu'
}

# List of 30 prebuilt voices available in the TTS API.
TTS_VOICES = [
    'Zephyr', 'Puck', 'Charon', 'Kore', 'Fenrir', 'Leda', 'Orus', 'Aoede', 'Callirrhoe', 
    'Autonoe', 'Enceladus', 'Iapetus', 'Umbriel', 'Algieba', 'Despina', 'Erinome', 
    'Algenib', 'Rasalgethi', 'Laomedeia', 'Achernar', 'Alnilam', 'Schedar', 'Gacrux', 
    'Pulcherrima', 'Achird', 'Zubenelgenubi', 'Vindemiatrix', 'Sadachbia', 'Sadaltager', 'Sulafat'
]

# Set to True to randomly select a voice from TTS_VOICES for each audio clip.
# Set to False to use the TTS_DEFAULT_VOICE for all clips.
TTS_RANDOM_VOICE = True
TTS_DEFAULT_VOICE = 'Kore' # Used if TTS_RANDOM_VOICE is False.

# --- File Paths ---
OUTPUT_DIR = "output"
DB_FILE = os.path.join(OUTPUT_DIR, "projects.sqlite")

# --- Rate Limiting (Free Tier) ---
# Add a small buffer to be safe
TTS_DELAY_S = 21       # 3 RPM -> 20s delay
IMAGE_DELAY_S = 7      # 10 RPM -> 6s delay
PLANNER_DELAY_S = 7    # 10 RPM -> 6s delay

# --- Video Composition ---
VIDEO_DIMENSIONS = (1080, 1920) # 9:16 aspect ratio
CHALLENGE_DURATION_S = 5
REVEAL_DURATION_S = 2
SCENE_PAUSE_S = 1.0
MUSIC_VOLUME = 0.15 # 15% of original volume
BACKGROUND_DARKEN_OPACITY = 0.4 # 40% dark overlay
COUNTDOWN_ANIMATION_DURATION = 1.0 # seconds for blur pulse effect

# --- FONT SETTINGS ---
# User must install these fonts on their system.
# cd ~/Library/Fonts/
# git clone https://github.com/google/fonts.git google-fonts
FONT_MAPPINGS = {
    "default": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "arabic": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosansarabic/NotoSansArabic[wdth,wght].ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosansarabic/NotoSansArabic[wdth,wght].ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosansarabic/NotoSansArabic[wdth,wght].ttf')
    },
    "bengali": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindsiliguri/HindSiliguri-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindsiliguri/HindSiliguri-Bold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindsiliguri/HindSiliguri-SemiBold.ttf')
    },
    "english": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/lobster/Lobster-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/lilitaone/LilitaOne-Regular.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/rowdies/Rowdies-Bold.ttf')
    },
    "hindi": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/rajdhani/Rajdhani-Bold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hind/Hind-SemiBold.ttf')
    },
    "japanese": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosansjp/NotoSansJP[wght].ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosansjp/NotoSansJP[wght].ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosansjp/NotoSansJP[wght].ttf')
    },
    "korean": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosanskr/NotoSansKR[wght].ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosanskr/NotoSansKR[wght].ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/notosanskr/NotoSansKR[wght].ttf')
    },
    "marathi": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/rajdhani/Rajdhani-Bold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hind/Hind-SemiBold.ttf')
    },
    "russian": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/montserratalternates/MontserratAlternates-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/montserratalternates/MontserratAlternates-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/montserratalternates/MontserratAlternates-Bold.ttf')
    },
    "tamil": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindmadurai/HindMadurai-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindmadurai/HindMadurai-Bold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindmadurai/HindMadurai-SemiBold.ttf')
    },
    "telugu": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/timmana/Timmana-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindguntur/HindGuntur-Bold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/hindguntur/HindGuntur-SemiBold.ttf')
    },
    "thai": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/kanit/Kanit-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/kanit/Kanit-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/kanit/Kanit-Bold.ttf')
    },
    "ukrainian": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/montserratalternates/MontserratAlternates-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/montserratalternates/MontserratAlternates-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/montserratalternates/MontserratAlternates-Bold.ttf')
    },
    # Latin-based languages can share a high-quality, comprehensive font set.
    "dutch": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "french": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "german": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "indonesian": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "italian": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "polish": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "portuguese": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "romanian": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "spanish": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "turkish": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Regular.ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-ExtraBold.ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/poppins/Poppins-Bold.ttf')
    },
    "vietnamese": {
        "intro": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf'),
        "challenge": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf'),
        "reveal": os.path.join(HOME_DIR, 'Library/Fonts/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf')
    }
}