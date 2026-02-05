from PIL import Image, ImageDraw

def create_app_icon():
    """Crée une icône pour l'application"""
    # Créer une image 256x256 (taille recommandée pour .ico)
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Cercle de fond vert
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(34, 139, 34, 255))  # ForestGreen
    
    # Cercle intérieur blanc (onde sonore)
    inner_margin = 60
    draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                 fill=(255, 255, 255, 255))
    
    # Petit cercle central vert
    center_margin = 100
    draw.ellipse([center_margin, center_margin, size-center_margin, size-center_margin], 
                 fill=(34, 139, 34, 255))
    
    # Sauvegarder en différentes tailles pour le .ico
    icon_sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    image.save('icon.ico', format='ICO', sizes=icon_sizes)
    print("✓ Icône créée : icon.ico")

if __name__ == "__main__":
    create_app_icon()
