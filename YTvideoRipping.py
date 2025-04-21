import yt_dlp
import os

# SETTINGS
URLS_FILE = "urls.txt"           # Text file with YouTube links (one per line)
AUDIO_ONLY = False               # Set to True to download audio as MP3
OUTPUT_DIR = os.path.expanduser("~/Documents/rips/Disrupt")  # Target download folder

def get_ydl_options(audio_only):
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    options = {
        'format': 'bestaudio/best' if audio_only else 'best',
        'outtmpl': os.path.join(OUTPUT_DIR, '%(title)s.%(ext)s'),
        'quiet': False,
        'postprocessors': []
    }

    if audio_only:
        options['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })

    return options

def download_from_list(file_path, audio_only=False):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("⚠️ No URLs found in file.")
        return

    print(f"📥 Starting download of {len(urls)} videos...")

    ydl_opts = get_ydl_options(audio_only)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                print(f"➡️ Downloading: {url}")
                ydl.download([url])
            except Exception as e:
                print(f"❌ Failed to download {url}: {e}")

if __name__ == "__main__":
    download_from_list(URLS_FILE, AUDIO_ONLY)

