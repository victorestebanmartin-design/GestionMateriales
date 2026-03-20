"""
Genera los iconos PNG para la PWA (Gestión de Materiales).
Requiere Pillow: pip install pillow

Crea:
  static/icons/icon-192.png
  static/icons/icon-512.png

Puedes reemplazar estos archivos por el logo que prefieras
(deben ser PNG cuadrados de 192x192 y 512x512).
"""
import os

def generar_icono(ruta, size):
    try:
        from PIL import Image, ImageDraw, ImageFont
        usa_pillow = True
    except ImportError:
        usa_pillow = False

    if usa_pillow:
        # Icono con Pillow: fondo azul + letras GM blancas
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fondo con esquinas redondeadas
        radio = size // 8
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radio, fill=(26, 115, 232))

        # Texto "GM"
        text = "GM"
        font_size = int(size * 0.42)
        try:
            # Intentar fuente del sistema
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Centrar texto
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (size - tw) // 2 - bbox[0]
        y = (size - th) // 2 - bbox[1]
        draw.text((x, y), text, fill="white", font=font)

        img.save(ruta, "PNG")
        print(f"  ✓ Icono creado con Pillow: {ruta} ({size}x{size})")
    else:
        # Fallback: PNG mínimo de color sólido (azul) sin texto usando bytes raw
        import struct, zlib

        def make_png(size, color_rgb):
            w, h = size, size
            raw = []
            for y in range(h):
                row = b'\x00'  # filter type None
                for x in range(w):
                    row += bytes(color_rgb)
                raw.append(row)

            def chunk(name, data):
                c = name + data
                return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

            IHDR_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
            idat_data = zlib.compress(b''.join(raw))

            return (
                b'\x89PNG\r\n\x1a\n'
                + chunk(b'IHDR', IHDR_data)
                + chunk(b'IDAT', idat_data)
                + chunk(b'IEND', b'')
            )

        with open(ruta, 'wb') as f:
            f.write(make_png(size, [26, 115, 232]))  # azul
        print(f"  ✓ Icono creado (básico, sin Pillow): {ruta} ({size}x{size})")
        print("    Instala Pillow para un icono con texto: pip install pillow")


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(base, "static", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    print("Generando iconos para la PWA...")
    generar_icono(os.path.join(icons_dir, "icon-192.png"), 192)
    generar_icono(os.path.join(icons_dir, "icon-512.png"), 512)
    print("\nListo. Puedes reemplazar estos archivos por el logo de tu empresa.")
    print("Solo asegúrate de que sean PNG cuadrados de 192x192 y 512x512.")


if __name__ == "__main__":
    main()
