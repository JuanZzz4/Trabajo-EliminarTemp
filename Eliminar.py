import os
import time
from send2trash import send2trash
from pushbullet import Pushbullet

def verificar_tipo_archivo(ruta_archivo, tipo_archivo):
    if tipo_archivo == "Internet":
        extensiones_internet = [".html", ".htm", ".css", ".js", ".jpg", ".png", ".gif"]
        return any(ruta_archivo.lower().endswith(ext) for ext in extensiones_internet)
    elif tipo_archivo == "Sistema":
        extensiones_sistema = [".sys", ".dll", ".exe", ".ini", ".sys", ".log"]
        return any(ruta_archivo.lower().endswith(ext) for ext in extensiones_sistema)
    elif tipo_archivo == "Apps":
        extensiones_apps = [".app", ".exe", ".dll", ".dat"]
        return any(ruta_archivo.lower().endswith(ext) for ext in extensiones_apps)
    elif tipo_archivo == "Personalizado":
        extensiones_personalizadas = [".puff", ".txt" , ".tmp"]
        return any(ruta_archivo.lower().endswith(ext) for ext in extensiones_personalizadas)
    else:
        return True  # Eliminar cualquier tipo de archivo si no se especifica un tipo

def enviar_a_papelera(ruta_archivo):
    try:
        ruta_archivo_normalizada = os.path.normpath(ruta_archivo)
        send2trash(ruta_archivo_normalizada)
        return True
    except Exception as e:
        print(f"Error al enviar a la papelera el archivo {ruta_archivo}. Error: {e}")
        return False

def notificar_a_pushbullet(mensaje):
    try:
        pb = Pushbullet("o.DuiR6ZrC5o1V3fLQCIAiWIhO5eNlTFBf")  # Reemplaza con tu propia API Key
        push = pb.push_note("Notificación antes de eliminar archivos", mensaje)
        return True
    except Exception as e:
        print(f"Error al enviar la notificación a Pushbullet: {e}")
        return False

def esperar_respuesta_pushbullet():
    pb = Pushbullet("o.DuiR6ZrC5o1V3fLQCIAiWIhO5eNlTFBf")  # Reemplaza con tu propia API Key

    while True:
        pushes = pb.get_pushes()
        if pushes and 'body' in pushes[0] and pushes[0]['body'].lower() in ['si', 'no']:
            return pushes[0]['body'].lower() == 'si'
        time.sleep(5)  # Esperar 5 segundos antes de volver a verificar

def mostrar_resultados(archivos_eliminados, archivos_no_eliminados):
    print("\nArchivos movidos a la papelera:")
    for archivo in archivos_eliminados:
        print(archivo)

    print("\nArchivos no movidos a la papelera:")
    for archivo in archivos_no_eliminados:
        print(archivo)

    print(f"\nTotal de archivos movidos a la papelera: {len(archivos_eliminados)}")
    print(f"Total de archivos no movidos a la papelera: {len(archivos_no_eliminados)}")

def eliminar_archivos_por_tipo(ruta_temp, tamano_limite, tipo_archivo, paginacion=10, segmentacion=1024*1024*10):  # 10 MB
    archivos_eliminados = []
    archivos_no_eliminados = []

    try:
        notificacion_enviada = False
        archivos = os.listdir(ruta_temp)

        for archivo in archivos:
            ruta_archivo = os.path.join(ruta_temp, archivo)

            if os.path.isfile(ruta_archivo) and os.path.getsize(ruta_archivo) > tamano_limite:
                if verificar_tipo_archivo(ruta_archivo, tipo_archivo):
                    if not notificacion_enviada:
                        mensaje_notificacion = "Se han encontrado archivos para eliminar. ¿Deseas proceder? Responde 'Si' o 'No'."
                        notificacion_enviada = notificar_a_pushbullet(mensaje_notificacion)

                        if not notificacion_enviada or not esperar_respuesta_pushbullet():
                            print("No se eliminaron archivos según tu solicitud.")
                            return

                    if enviar_a_papelera(ruta_archivo):
                        print(f"Se movió a la papelera el archivo: {ruta_archivo}")
                        archivos_eliminados.append(archivo)
                    else:
                        print(f"No se pudo enviar a la papelera el archivo {ruta_archivo}")
                        archivos_no_eliminados.append(archivo)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    mostrar_resultados(archivos_eliminados, archivos_no_eliminados)

if __name__ == "__main__":
    carpeta_temp = input("Ingresa la ruta de tu carpeta temp (presiona Enter para usar la carpeta por defecto): ") or "C:/Users/juanm/AppData/Local/Temp"
    tamano_limite = int(input("Ingresa el tamaño límite para eliminar archivos (en bytes): ") or 1000)

    print("\nTipos de archivos disponibles:")
    print("1. Internet")
    print("2. Sistema")
    print("3. Apps")
    print("4. Personalizado (.puff, .txt)")
    print("5. Todos (ninguna selección)")

    opcion_tipo_archivo = input("Seleccione el tipo de archivo a eliminar (1-5): ")
    
    if opcion_tipo_archivo == "1":
        tipo_archivo = "Internet"
    elif opcion_tipo_archivo == "2":
        tipo_archivo = "Sistema"
    elif opcion_tipo_archivo == "3":
        tipo_archivo = "Apps"
    elif opcion_tipo_archivo == "4":
        tipo_archivo = "Personalizado"
    else:
        tipo_archivo = "Todos"

    eliminar_archivos_por_tipo(carpeta_temp, tamano_limite, tipo_archivo)
