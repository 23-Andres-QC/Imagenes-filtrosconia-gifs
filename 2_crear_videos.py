import os
import math
try:
    from PIL import Image
except ImportError:
    print("Error: Falta la librería 'Pillow'. Ejecuta: pip install Pillow")
    exit(1)

def crear_videos_animados():
    carpeta_entrada = "imagenes_sin_fondo"
    carpeta_salida = "output_videos_animados"
    
    if not os.path.exists(carpeta_entrada):
        print(f"Error: No existe la carpeta {carpeta_entrada}")
        return
        
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        
    archivos = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.png')]
    
    if not archivos:
        print(f"No se encontraron imágenes en '{carpeta_entrada}'.")
        return

    print("Generando animación 2D (Efecto de Vida / Respiración)...")
    print("Esta es una técnica local 100% libre de límites que no usa internet ni consume GPU.")

    for archivo in archivos:
        ruta_entrada = os.path.join(carpeta_entrada, archivo)
        nombre_sin_ext = os.path.splitext(archivo)[0]
        ruta_salida = os.path.join(carpeta_salida, f"{nombre_sin_ext}_animado.gif")
        
        print(f"Animando: {archivo} ...")
        
        try:
            img = Image.open(ruta_entrada).convert("RGBA")
            width, height = img.size
            
            frames = []
            fps = 15
            duracion = 3
            total_frames = fps * duracion
            
            # Compatibilidad con diferentes versiones de Pillow
            resampling_module = getattr(Image, 'Resampling', Image)
            filtro_lanczos = getattr(resampling_module, 'LANCZOS', 1)
            filtro_bicubic = getattr(resampling_module, 'BICUBIC', 3)
            
            for i in range(total_frames):
                # Fase de 0 a 2*PI para hacer un bucle perfecto (el video se repetirá sin cortes)
                fase = (i / total_frames) * 2 * math.pi
                
                # 1. Efecto de respiración: el personaje "respira", se estira en altura y se encoge en ancho
                scale_y = 1.0 + 0.02 * math.sin(fase) # 2% más alto en la inhalación
                scale_x = 1.0 - 0.01 * math.sin(fase) # 1% más delgado
                
                new_w = int(width * scale_x)
                new_h = int(height * scale_y)
                
                img_resized = img.resize((new_w, new_h), filtro_lanczos)
                
                canvas = Image.new("RGBA", (width, height), (0,0,0,0))
                
                # Anclar la imagen en la parte inferior para que parezca que los pies/base están fijos
                offset_x = (width - new_w) // 2
                offset_y = height - new_h
                
                canvas.paste(img_resized, (offset_x, offset_y), img_resized)
                
                # 2. Efecto de balanceo (Sway): Rotación ligera desfasada
                rot_angle = 1.5 * math.cos(fase) # Oscila entre -1.5 y 1.5 grados
                
                # Rotar tomando como centro la parte inferior (base)
                centro_rotacion = (width // 2, height)
                frame_final = canvas.rotate(rot_angle, resample=filtro_bicubic, center=centro_rotacion)
                
                frames.append(frame_final)
                
            # Guardar como GIF animado de alta fluidez
            frames[0].save(
                ruta_salida,
                save_all=True,
                append_images=frames[1:],
                duration=int(1000/fps),
                loop=0,
                disposal=2 # Vital para que la transparencia no deje "fantasma" en el frame anterior
            )
            
            print(f"¡Éxito! Personaje con vida guardado en {ruta_salida}")
            
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

if __name__ == "__main__":
    crear_videos_animados()

