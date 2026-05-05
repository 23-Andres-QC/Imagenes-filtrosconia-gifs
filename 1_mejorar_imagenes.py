import os
import io

try:
    from PIL import Image, ImageEnhance
except ImportError:
    print("Error: No se encontró 'Pillow'. Ejecuta: pip install Pillow")
    exit(1)

try:
    from rembg import remove, new_session
except ImportError:
    print("Error: No se encontró 'rembg'. Ejecuta: pip install rembg")
    exit(1)

def mejorar_imagen(ruta_imagen):
    # Asegurar que la imagen soporte canales RGBA para transparencia
    img = Image.open(ruta_imagen).convert("RGBA")
    
    # 1. Aumentar resolución (Filtro LANCZOS)
    filtro_lanczos = getattr(Image, 'Resampling', Image).LANCZOS
    nuevo_tamano = (img.width * 2, img.height * 2)
    img_grande = img.resize(nuevo_tamano, filtro_lanczos)
    
    # 2. Mejorar Nitidez (Sharpness)
    realzador_nitidez = ImageEnhance.Sharpness(img_grande)
    img_nitida = realzador_nitidez.enhance(1.5)
    
    # 3. Mejorar Color y Contraste
    realzador_color = ImageEnhance.Color(img_nitida)
    img_color = realzador_color.enhance(1.2)
    
    realzador_contraste = ImageEnhance.Contrast(img_color)
    img_final = realzador_contraste.enhance(1.1)
    
    # Convertir a bytes para rembg
    buffer = io.BytesIO()
    img_final.save(buffer, format="PNG")
    return buffer.getvalue()

def procesar_imagenes():
    carpeta_entrada = "imagenes_entrada"
    carpeta_salida = "imagenes_sin_fondo"
        
    archivos = os.listdir(carpeta_entrada)
    imagenes = [f for f in archivos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]
    
    if not imagenes:
        print(f"No se encontraron imágenes en '{carpeta_entrada}'.")
        return

    print("Cargando el mejor modelo de IA para recorte (BiRefNet)...")
    print("Nota: La primera vez puede tardar en descargar el modelo (aprox 900MB).")
    session = new_session("birefnet-general")

    for archivo in imagenes:
        ruta_entrada = os.path.join(carpeta_entrada, archivo)
        nombre_sin_ext = os.path.splitext(archivo)[0]
        # Guardaremos el resultado siempre como .png porque tiene transparencia
        ruta_salida = os.path.join(carpeta_salida, f"{nombre_sin_ext}.png")
        
        print(f"\nProcesando: {archivo} ...")
        
        try:
            print("   -> 1/2 Mejorando resolución, nitidez y colores...")
            imagen_mejorada_bytes = mejorar_imagen(ruta_entrada)
                
            print("   -> 2/2 Quitando fondo con IA...")
            output_data = remove(imagen_mejorada_bytes, session=session)
            
            # Guardar la imagen final sin fondo en la nueva carpeta
            with open(ruta_salida, 'wb') as o:
                o.write(output_data)
            
            print(f"¡Éxito! Guardado en: {ruta_salida}")
            
        except Exception as e:
            print(f"Error con {archivo}: {e}")

if __name__ == "__main__":
    print("Iniciando Paso 1: Mejoras de Calidad y Eliminación de Fondo...")
    procesar_imagenes()
    print("\n¡Paso 1 completado!")
