"""import customtkinter as ctk
import os
from PIL import Image

# Configuración general
ctk.set_appearance_mode("dark")  # Opciones: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"

# Crear ventana principal
app = ctk.CTk()
app.geometry("1000x600")
app.title("RadioLinkCalc")

# Crear widgets
punto1 = ctk.CTkEntry(master=app, placeholder_text="Digite los grados,minutos,seguntos del punto 1")
punto1.pack(pady=10)

punto2 = ctk.CTkEntry(master=app, placeholder_text="Digite los grados,minutos,seguntos del punto 2")
punto2.pack(pady=10)

def mostrar_texto():
    print("Texto ingresado:", punto1.get())

boton = ctk.CTkButton(master=app, text="Mostrar", command=mostrar_texto)
boton.pack(pady=10)

# Ejecutar
app.mainloop()"""

# import customtkinter as ctk
# from geopy.distance import geodesic

# def dms_a_decimal(g, m, s, dir):
#     decimal = g + m / 60 + s / 3600
#     return -decimal if dir in ['S', 'W'] else decimal

# def obtener_distancia():
#     try:
#         lat1 = dms_a_decimal(int(g1.get()), int(m1.get()), float(s1.get()), dir1.get())
#         lon1 = dms_a_decimal(int(g2.get()), int(m2.get()), float(s2.get()), dir2.get())
#         lat2 = dms_a_decimal(int(g3.get()), int(m3.get()), float(s3.get()), dir3.get())
#         lon2 = dms_a_decimal(int(g4.get()), int(m4.get()), float(s4.get()), dir4.get())
#         distancia = geodesic((lat1, lon1), (lat2, lon2)).kilometers
#         resultado.configure(text=f"Distancia: {distancia:.2f} km")
#     except Exception as e:
#         resultado.configure(text=f"Error: {e}")

# # Configuración
# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("blue")
# app = ctk.CTk()
# app.geometry("800x400")
# app.title("RadioLinkCalc")

# # ---- FRAME para disposición horizontal ----
# frame_a = ctk.CTkFrame(app)
# frame_a.pack(pady=20)

# # Punto A - Latitud
# ctk.CTkLabel(frame_a, text="Latitud Punto A").grid(row=0, column=0, columnspan=2, padx=5)
# g1 = ctk.CTkEntry(frame_a, placeholder_text="G"); g1.grid(row=1, column=0)
# m1 = ctk.CTkEntry(frame_a, placeholder_text="M"); m1.grid(row=2, column=0)
# s1 = ctk.CTkEntry(frame_a, placeholder_text="S"); s1.grid(row=3, column=0)
# dir1 = ctk.CTkComboBox(frame_a, values=["N", "S"]); dir1.grid(row=4, column=0)

# # Punto A - Longitud
# ctk.CTkLabel(frame_a, text="Longitud Punto A").grid(row=0, column=6, columnspan=4, padx=5)
# g2 = ctk.CTkEntry(frame_a, placeholder_text="G"); g2.grid(row=1, column=6)
# m2 = ctk.CTkEntry(frame_a, placeholder_text="M"); m2.grid(row=2, column=6)
# s2 = ctk.CTkEntry(frame_a, placeholder_text="S"); s2.grid(row=3, column=6)
# dir2 = ctk.CTkComboBox(frame_a, values=["E", "W"]); dir2.grid(row=4, column=6)

# # Punto B - Latitud
# ctk.CTkLabel(frame_a, text="Latitud Punto B").grid(row=0, column=12, columnspan=4, padx=5)
# g3 = ctk.CTkEntry(frame_a, placeholder_text="G"); g3.grid(row=1, column=12)
# m3 = ctk.CTkEntry(frame_a, placeholder_text="M"); m3.grid(row=2, column=12)
# s3 = ctk.CTkEntry(frame_a, placeholder_text="S"); s3.grid(row=3, column=12)
# dir3 = ctk.CTkComboBox(frame_a, values=["N", "S"]); dir3.grid(row=4, column=12)

# # Punto B - Longitud
# ctk.CTkLabel(frame_a, text="Longitud Punto B").grid(row=0, column=18, columnspan=4, padx=5)
# g4 = ctk.CTkEntry(frame_a, placeholder_text="G"); g4.grid(row=1, column=18)
# m4 = ctk.CTkEntry(frame_a, placeholder_text="M"); m4.grid(row=2, column=18)
# s4 = ctk.CTkEntry(frame_a, placeholder_text="S"); s4.grid(row=3, column=18)
# dir4 = ctk.CTkComboBox(frame_a, values=["E", "W"]); dir4.grid(row=4, column=18)

# # Botón y resultado
# ctk.CTkButton(app, text="Calcular Distancia", command=obtener_distancia).pack(pady=15)
# resultado = ctk.CTkLabel(app, text="Distancia: ")
# resultado.pack(pady=10)

# app.mainloop()

import customtkinter as ctk
import requests
import math
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def obtener_perfil_elevacion_batch(lat1, lon1, lat2, lon2, n_puntos=100, dataset="mapzen"):
    lats = [lat1 + i * (lat2 - lat1) / (n_puntos - 1) for i in range(n_puntos)]
    lons = [lon1 + i * (lon2 - lon1) / (n_puntos - 1) for i in range(n_puntos)]

    elevaciones = []
    batch_size = 100

    for i in range(0, n_puntos, batch_size):
        batch_lats = lats[i:i + batch_size]
        batch_lons = lons[i:i + batch_size]
        locations = "|".join([f"{lat},{lon}" for lat, lon in zip(batch_lats, batch_lons)])
        url = f"https://api.opentopodata.org/v1/{dataset}?locations={locations}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            elevaciones.extend([result["elevation"] for result in data["results"]])
        else:
            elevaciones.extend([None] * len(batch_lats))
        time.sleep(1)

    return list(zip(lats, lons, elevaciones))

def fresnel_radius(d1, d2, f_ghz, n=1):
    if d1 == 0 or d2 == 0:
        return 0
    lambda_m = C / (f_ghz * 1e9)
    return math.sqrt(n * lambda_m * d1 * d2 / (d1 + d2))

def calcular_distancias_acumuladas(perfil):
    distancias = [0.0]
    for i in range(1, len(perfil)):
        lat1, lon1 = perfil[i - 1][:2]
        lat2, lon2 = perfil[i][:2]
        d = haversine(lat1, lon1, lat2, lon2)
        distancias.append(distancias[-1] + d)
    return distancias

def plot_elevation_profile_embebido(profile, frame):
    elevations = [p[2] for p in profile]
    distances = calcular_distancias_acumuladas(profile)

    fig, ax = plt.subplots(figsize=(7, 3), dpi=100)
    ax.plot(distances, elevations, color='green')
    ax.set_title("Perfil de Elevación")
    ax.set_xlabel("Distancia acumulada (m)")
    ax.set_ylabel("Elevación (m)")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    plt.close(fig)  # Cerramos para evitar superposición

###################################################### GUI - Interfaz Gráfica ##########################################################

def procesar():
    try:
        lat1 = float(entry_lat1.get())
        lon1 = float(entry_lon1.get())
        lat2 = float(entry_lat2.get())
        lon2 = float(entry_lon2.get())

        distancia = haversine(lat1, lon1, lat2, lon2) / 1000
        resultado_label.configure(text=f"Distancia Haversine: {distancia:.2f} km")

        # Limpiar gráficos anteriores
        for widget in graph_frame.winfo_children():
            widget.destroy()

        def obtener_y_mostrar():
            perfil = obtener_perfil_elevacion_batch(lat1, lon1, lat2, lon2, n_puntos=500)
            plot_elevation_profile_embebido(perfil, graph_frame)

        threading.Thread(target=obtener_y_mostrar).start()

    except Exception as e:
        resultado_label.configure(text=f"Error: {e}")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.geometry("900x600")
app.title("RadioLinkCalc")

frame_inputs = ctk.CTkFrame(app)
frame_inputs.pack(pady=10)

# Inputs Coordenadas
#------------------------------------------------------------------------------------------------------------------------------
ctk.CTkLabel(frame_inputs, text="Latitud y Longitud en Decimales").grid(row=0, column=0, columnspan=4, pady=5)

entry_lat1 = ctk.CTkEntry(frame_inputs, placeholder_text="Latitud A"); entry_lat1.grid(row=1, column=0, padx=5)
entry_lon1 = ctk.CTkEntry(frame_inputs, placeholder_text="Longitud A"); entry_lon1.grid(row=1, column=1, padx=5)
entry_lat2 = ctk.CTkEntry(frame_inputs, placeholder_text="Latitud B"); entry_lat2.grid(row=1, column=2, padx=5)
entry_lon2 = ctk.CTkEntry(frame_inputs, placeholder_text="Longitud B"); entry_lon2.grid(row=1, column=3, padx=5)

#Inputs Datos adicionales
#------------------------------------------------------------------------------------------------------------------------------
ctk.CTkLabel(frame_inputs, text="Datos adicionales").grid(row=2, column=0, columnspan=4, pady=5)

entry_fmax = ctk.CTkEntry(frame_inputs, placeholder_text="Frecuencia Máxima"); entry_fmax.grid(row=3, column=0, padx=5)
entry_fmin = ctk.CTkEntry(frame_inputs, placeholder_text="Frecuencia Minimma"); entry_fmin.grid(row=3, column=1, padx=5)
entry_potenciatx = ctk.CTkEntry(frame_inputs, placeholder_text="Potencia del TX (watt)"); entry_potenciatx.grid(row=3, column=2, padx=5)
entry_umbralrx = ctk.CTkEntry(frame_inputs, placeholder_text="Umbral del RX (uV)"); entry_umbralrx.grid(row=3, column=3, padx=5)
entry_perdidalinea = ctk.CTkEntry(frame_inputs, placeholder_text="Perdida de la linea (dB)"); entry_perdidalinea.grid(row=4, column=0, padx=5)
entry_ganancia = ctk.CTkEntry(frame_inputs, placeholder_text="Ganancia antena(dBi)"); entry_ganancia.grid(row=4, column=1, padx=5)
entry_perdidacable = ctk.CTkEntry(frame_inputs, placeholder_text="Perdida adicional del cable (db/m)"); entry_perdidacable.grid(row=4, column=2, padx=5)
entry_alturatx = ctk.CTkEntry(frame_inputs, placeholder_text="Altura de la antena TX (m)"); entry_alturatx.grid(row=4, column=3, padx=5)
entry_alturarx = ctk.CTkEntry(frame_inputs, placeholder_text="Altura de la antena RX (m)"); entry_alturarx.grid(row=5, column=1, padx=5)
entry_sensibilidadrx = ctk.CTkEntry(frame_inputs, placeholder_text="Sensibilidad RX (dbm)"); entry_sensibilidadrx.grid(row=5, column=2, padx=5)

# Botón y resultado
#------------------------------------------------------------------------------------------------------------------------------
ctk.CTkButton(app, text="Calcular y Mostrar Perfil", command=procesar).pack(pady=10)
resultado_label = ctk.CTkLabel(app, text="Distancia:")
resultado_label.pack()

# Frame para la gráfica
#------------------------------------------------------------------------------------------------------------------------------
graph_frame = ctk.CTkFrame(app)
graph_frame.pack(pady=5, fill="both", expand=True)

app.mainloop()

