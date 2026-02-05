from PIL import Image

def convert_png_to_ico(png_path, ico_path):
    """Convertit un PNG en ICO multi-tailles de qualité"""
    # Ouvrir l'image PNG
    img = Image.open(png_path)
    
    # Convertir en RGBA si nécessaire
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Créer les différentes tailles (important pour éviter la pixelisation)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256), (512, 512)]
    
    # Sauvegarder en .ico avec toutes les tailles
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"✓ Fichier .ico créé : {ico_path}")
    print(f"  Tailles incluses : {sizes}")

if __name__ == "__main__":
    # Modifiez le nom de votre fichier PNG ici
    png_file = "icon.png"  # Votre fichier PNG source
    ico_file = "icon.ico"  # Le fichier .ico de sortie
    
    try:
        convert_png_to_ico(png_file, ico_file)
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{png_file}' n'existe pas")
        print("   Placez votre PNG dans le dossier et modifiez le nom dans le script")
    except Exception as e:
        print(f"❌ Erreur : {e}")
