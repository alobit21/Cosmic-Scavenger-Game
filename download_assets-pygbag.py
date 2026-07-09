import os
import urllib.request

# Dictionary of assets to download (URL -> Local Filename)
assets = {
    # Images
    "player.png": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/img/playerShip1_orange.png",
    "enemy.png": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/img/enemyRed1.png",
    "enemy_zigzag.png": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/img/enemyBlack2.png",
    "laser.png": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/img/laserRed16.png",
    "background.png": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/img/starfield.png",
    
    # Sounds
    "shoot.ogg": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/pew.ogg",
    "explosion.ogg": "https://raw.githubusercontent.com/kidscancode/pygame_tutorials/master/shmup/snd/expl3.ogg"
}

# Create assets folder if it doesn't exist
os.makedirs("assets", exist_ok=True)

print("Downloading open-source assets for Cosmic Scavenger...")

for filename, url in assets.items():
    filepath = os.path.join("assets", filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"✅ Saved to {filepath}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    else:
        print(f"✅ {filename} already exists!")

print("\nAll assets downloaded successfully! We are ready to plug them in.")
