import math
import time
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
import tkinter as tk
import webbrowser

# Establecer apariencia CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ------------------ FUNCIONES BÁSICAS ------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def fresnel_radius(d1, d2, f_ghz, n=1):
    C = 3e8
    if d1 == 0 or d2 == 0:
        return 0
    lambda_m = C / (f_ghz * 1e9)
    return math.sqrt(n * lambda_m * d1 * d2 / (d1 + d2))

def obtener_perfil_elevacion(lat1, lon1, lat2, lon2, n_puntos=100, dataset="mapzen"):
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
            elevaciones.extend([0] * len(batch_lats))  # Fallback to 0
        time.sleep(1)
    return list(zip(lats, lons, elevaciones))

def calcular_distancias_acumuladas(perfil):
    distancias = [0.0]
    for i in range(1, len(perfil)):
        lat1, lon1 = perfil[i - 1][:2]
        lat2, lon2 = perfil[i][:2]
        d = haversine(lat1, lon1, lat2, lon2)
        distancias.append(distancias[-1] + d)
    return distancias

# ------------------ Funciones de cálculos ------------------
def calcular_los_line(elevaciones, tx_height, rx_height):
    return [
        elevaciones[0] + tx_height + i * (elevaciones[-1] + rx_height - (elevaciones[0] + tx_height)) / (len(elevaciones) - 1)
        for i in range(len(elevaciones))
    ]

def calcular_obstruccion_db(h, r):
    if r == 0:
        return 0
    v = math.sqrt(2) * h / r
    if v <= -0.78:
        return 0
    else:
        return 6.9 + 20 * math.log10(math.sqrt((v - 0.1)**2 + 1) + v - 0.1)

def detectar_peor_fresnel(elevaciones, los_line, distancias, freq_ghz):
    peores_puntos = []
    for i in range(1, len(elevaciones) - 1):
        d1 = distancias[i]
        d2 = distancias[-1] - d1
        r_fresnel = fresnel_radius(d1, d2, freq_ghz)
        centro_fresnel = los_line[i]
        borde_inferior = centro_fresnel - r_fresnel
        elevacion_terreno = elevaciones[i]
        if elevacion_terreno >= borde_inferior:
            penetracion = los_line[i] - elevacion_terreno
            pct_obstruccion = penetracion / r_fresnel
            h = elevacion_terreno - los_line[i]
            obstruccion_db = calcular_obstruccion_db(h, r_fresnel)
        else:
            pct_obstruccion = 1
            obstruccion_db = 0
        relacion_bordeinf_elevacion = borde_inferior - elevacion_terreno
        peores_puntos.append((i, pct_obstruccion, r_fresnel, centro_fresnel - elevacion_terreno, obstruccion_db, relacion_bordeinf_elevacion, d1, d2))
    peores_con_obstruccion = [p for p in peores_puntos if p[4] > 0]
    if peores_con_obstruccion:
        return max(peores_con_obstruccion, key=lambda x: x[4])
    else:
        return min(peores_puntos, key=lambda x: x[5])

def calcular_azimut(lat1, lon1, lat2, lon2):
    dlon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dlon)
    azimut_rad = math.atan2(x, y)
    azimut_deg = (math.degrees(azimut_rad) + 360) % 360
    return azimut_deg

def calcular_perdidas_espacio_libre(d_km, f_mhz):
    return 20 * math.log10(d_km) + 20 * math.log10(f_mhz) + 32.44

def calcular_angulo_elevacion(h_tx_total, h_rx_total, d_total_m):
    delta_altura = h_rx_total - h_tx_total
    angulo_rad = math.atan2(delta_altura, d_total_m)
    return math.degrees(angulo_rad)

def calcular_campo_e(power_watts, gain_dbi, distance_m):
    g_t = 10 ** (gain_dbi / 10)
    e = math.sqrt(30 * power_watts * g_t) / distance_m
    e_microvolts = e * 1e6
    e_dbuvm = 20 * math.log10(e_microvolts)
    return e_dbuvm

def calcular_nivel_rx_dbm(pot_transmisor, ganancia_tx, ganancia_rx, perdidas_linea, perdidas_totales, obstruccion_db=0):
    if pot_transmisor <= 0:
        return float('-inf')
    p_tx_dbm = 10 * math.log10(pot_transmisor) + 30
    return p_tx_dbm + ganancia_tx + ganancia_rx - perdidas_linea - perdidas_linea - perdidas_totales - obstruccion_db

def calcular_nivel_rx_uv(nivel_rx_dbm):
    return 10 ** ((nivel_rx_dbm + 107) / 20)

def rx_relative_db(sensibilidad_rx, nivel_rx_dbm):
    return nivel_rx_dbm - sensibilidad_rx

def calcular_estadisticas(d_total_km):
    return 6.3 + 0.9*math.log10(d_total_km)

def calcular_perdidas(perdidas_espacio_libre, estadisticas, obstruccion_db):
    return perdidas_espacio_libre + estadisticas + obstruccion_db

# ------------------ GUI CLASS ------------------
class RadioLinkCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RadioLinkCalc")
        self.resizable(True, True)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.input_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.input_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)

        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Sección de entradas
        self.create_coordinates_section()
        self.create_equipment_section()
        self.create_simulation_section()
        self.create_calculate_button()

        # Sección de salidas
        self.create_results_section()
        self.create_plot_section()

    def create_coordinates_section(self):
        self.coord_frame = ctk.CTkFrame(self.input_frame)
        self.coord_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(self.coord_frame, text="Coordenadas", font=("Arial", 14, "bold")).pack(anchor="w")

        # Coordenadas del transmisor
        ctk.CTkLabel(self.coord_frame, text="Transmisor").pack(anchor="w")
        self.tx_lat = ctk.CTkEntry(self.coord_frame, placeholder_text="Latitud (e.g., 7.357130556)")
        self.tx_lat.pack(fill="x", pady=2)
        self.tx_lon = ctk.CTkEntry(self.coord_frame, placeholder_text="Longitud (e.g., -72.65921111)")
        self.tx_lon.pack(fill="x", pady=2)

        # Coordenadas del Receptor
        ctk.CTkLabel(self.coord_frame, text="Receptor").pack(anchor="w")
        self.rx_lat = ctk.CTkEntry(self.coord_frame, placeholder_text="Latitud (e.g., 7.380841667)")
        self.rx_lat.pack(fill="x", pady=2)
        self.rx_lon = ctk.CTkEntry(self.coord_frame, placeholder_text="Longitud (e.g., -72.65215833)")
        self.rx_lon.pack(fill="x", pady=2)

    def create_equipment_section(self):
        self.equip_frame = ctk.CTkFrame(self.input_frame)
        self.equip_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(self.equip_frame, text="Parámetros de los Equipos", font=("Arial", 14, "bold")).pack(anchor="w")

        # Frequencia
        ctk.CTkLabel(self.equip_frame, text="Frequencia (GHz)").pack(anchor="w")
        self.freq_min = ctk.CTkEntry(self.equip_frame, placeholder_text="Min (e.g., 5.700)")
        self.freq_min.pack(fill="x", pady=2)
        self.freq_max = ctk.CTkEntry(self.equip_frame, placeholder_text="Max (e.g., 5.720)")
        self.freq_max.pack(fill="x", pady=2)

        # Alturas
        ctk.CTkLabel(self.equip_frame, text="Alturas de las antenas (m)").pack(anchor="w")
        self.tx_height = ctk.CTkEntry(self.equip_frame, placeholder_text="Tx Altura (e.g., 3)")
        self.tx_height.pack(fill="x", pady=2)
        self.rx_height = ctk.CTkEntry(self.equip_frame, placeholder_text="Rx Altura (e.g., 5)")
        self.rx_height.pack(fill="x", pady=2)

        # Parámetros de los Equipos
        ctk.CTkLabel(self.equip_frame, text="Parámetros del Transmisor").pack(anchor="w")
        self.pot_transmisor = ctk.CTkEntry(self.equip_frame, placeholder_text="Potencia (W, e.g., 1)")
        self.pot_transmisor.pack(fill="x", pady=2)
        self.perdidas_linea = ctk.CTkEntry(self.equip_frame, placeholder_text="Pérdida de Linea (dB, e.g., 0.1)")
        self.perdidas_linea.pack(fill="x", pady=2)
        self.ganancia_tx = ctk.CTkEntry(self.equip_frame, placeholder_text="Tx Ganancia (dBi, e.g., 12)")
        self.ganancia_tx.pack(fill="x", pady=2)
        self.ganancia_rx = ctk.CTkEntry(self.equip_frame, placeholder_text="Rx Ganancia (dBi, e.g., 12)")
        self.ganancia_rx.pack(fill="x", pady=2)
        self.sensibilidad_rx = ctk.CTkEntry(self.equip_frame, placeholder_text="Rx Sensibilidad (dBm, e.g., -107)")
        self.sensibilidad_rx.pack(fill="x", pady=2)
        
    def create_simulation_section(self):
        self.sim_frame = ctk.CTkFrame(self.input_frame)
        self.sim_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(self.sim_frame, text="Parámetros de Simulación", font=("Arial", 14, "bold")).pack(anchor="w")

        # Parámetros de Simulación
        self.n_puntos = ctk.CTkEntry(self.sim_frame, placeholder_text="Puntos/muestras (e.g., 100)")
        self.n_puntos.pack(fill="x", pady=2)
        dataset_options = ["mapzen", "nzdem8m", "ned10m", "eudem25m", "aster30m", "srtm30m", "srtm90m", "bkg200m", "etopo1", "gebco2020", "emod2018"]
        self.dataset = ctk.CTkComboBox(self.sim_frame, values=dataset_options, state="readonly")
        self.dataset.set("mapzen")  # Set default value
        self.dataset.pack(fill="x", pady=2)

    def create_calculate_button(self):
        self.calculate_button = ctk.CTkButton(self.input_frame, text="Calcular", command=self.calculate_link)
        self.calculate_button.pack(pady=6)

    def create_results_section(self):
        ctk.CTkLabel(self.output_frame, text="Desarrollado por: Cristian Castro, Andrés Delgado, Universidad de Pamplona", font=("Arial", 12)).pack(anchor="ne", padx=5, pady=5)
        
        self.results_frame = ctk.CTkFrame(self.output_frame)
        self.results_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(self.results_frame, text="Resultados", font=("Arial", 14, "bold")).pack(anchor="w")
        self.results_text = ctk.CTkTextbox(self.results_frame, height=200, width=400)
        self.results_text.pack(fill="x", pady=5)
        self.results_text.insert("end", "Los resultados aparecerán aquí después del cálculo.")

    def create_plot_section(self):
        self.plot_frame = ctk.CTkFrame(self.output_frame)
        self.plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(self.plot_frame, text="Perfil de elevación", font=("Arial", 14, "bold")).pack(anchor="w")
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        # Establecer el fondo para que coincida con el marco CustomTkinter
        frame_bg = self.plot_frame.cget("fg_color")
        print(f"Frame background color: {frame_bg}")
        # Maneja el caso donde frame_bg es una tupla (tema claro/oscuro) o un solo color
        canvas_bg = frame_bg[0] if isinstance(frame_bg, tuple) else frame_bg
        # Volver a un color conocido si canvas_bg sigue siendo inválido
        try:
            canvas_widget.configure(bg=canvas_bg)
        except tk.TclError:
            print(f"Invalid color {canvas_bg}, using fallback 'gray'")
            canvas_widget.configure(bg="gray")
        self.ax.set_axis_off()  # Ocultar los ejes hasta que se dibuje el gráfico
        self.canvas.draw()
        
        # Agregar link de acceso "Documentación"
        doc_label = ctk.CTkLabel(self.plot_frame, text="Documentación: https://radiolinkcal.vercel.app/", font=("Arial", 12), text_color="white", cursor="hand2")
        doc_label.pack(anchor="se", padx=5, pady=5)
        doc_label.bind("<Button-1>", lambda e: webbrowser.open("https://radiolinkcal.vercel.app/"))
        
    def calculate_link(self):
        try:
            # Recuperar y validar entradas
            lat1 = float(self.tx_lat.get())
            lon1 = float(self.tx_lon.get())
            lat2 = float(self.rx_lat.get())
            lon2 = float(self.rx_lon.get())
            freq_min_ghz = float(self.freq_min.get())
            freq_max_ghz = float(self.freq_max.get())
            tx_height = float(self.tx_height.get())
            rx_height = float(self.rx_height.get())
            pot_transmisor = float(self.pot_transmisor.get())
            perdidas_linea = float(self.perdidas_linea.get())
            ganancia_tx = float(self.ganancia_tx.get())
            ganancia_rx = float(self.ganancia_rx.get())
            sensibilidad_rx = float(self.sensibilidad_rx.get())
            n_puntos = int(self.n_puntos.get())
            dataset = str(self.dataset.get())

            # Ejecución de Calculos
            freq_ghz = (freq_max_ghz + freq_min_ghz) / 2
            perfil = obtener_perfil_elevacion(lat1, lon1, lat2, lon2, n_puntos, dataset)
            elevaciones = [p[2] for p in perfil]
            d_total = haversine(lat1, lon1, lat2, lon2)
            distancias = calcular_distancias_acumuladas(perfil)
            los_line = calcular_los_line(elevaciones, tx_height, rx_height)
            peor_index, peor_pct_obst, peor_fresnel, peor_clearance, obstruccion_db, relacion_bordeinf_elevacion, d1, d2 = detectar_peor_fresnel(elevaciones, los_line, distancias, freq_ghz)
            azimut = calcular_azimut(lat1, lon1, lat2, lon2)
            perdidas_espacio_libre = calcular_perdidas_espacio_libre(d_total/1000, freq_ghz*1000)
            h_tx_total = elevaciones[0] + tx_height
            h_rx_total = elevaciones[-1] + rx_height
            angulo_elevacion = calcular_angulo_elevacion(h_tx_total, h_rx_total, d_total)
            campo_e = calcular_campo_e(pot_transmisor, ganancia_tx, d_total)
            estadisticas = calcular_estadisticas(d_total/1000)
            perdidas_totales = calcular_perdidas(perdidas_espacio_libre, estadisticas, obstruccion_db)
            nivel_rx_dbm = calcular_nivel_rx_dbm(pot_transmisor, ganancia_tx, ganancia_rx, perdidas_linea, perdidas_totales, obstruccion_db)
            nivel_rx_uv = calcular_nivel_rx_uv(nivel_rx_dbm)
            rx_relative = rx_relative_db(sensibilidad_rx, nivel_rx_dbm)

            # Actualización de resultados
            self.results_text.delete("1.0", "end")
            results = (
                f"Index Peor Fresnel = {peor_index}\n"
                f"Radio de Fresnel = {peor_fresnel:.3f} m\n"
                f"Espacio Libre Fresnel = {peor_clearance:.3f} m\n"
                f"{'-'*135}\n"
                f"Frecuencia Promedio = {freq_ghz:.3f} GHz    |   Distancia Tx - Obstáculo = {d1:.3f} m\n"
                f"Distancia Total = {d_total/1000:.3f} km                |   Distancia Rx - Obstaculo = {d2:.3f} m\n"
                f"Azimut = {azimut:.2f}°                                    |   Espacio Libre = {perdidas_espacio_libre:.3f} dB\n"
                f"Pérdidas Totales = {perdidas_totales:.2f} dB            |   Ángulo de Elevación = {angulo_elevacion:.3f}°\n"
                f"Obstrucción = {obstruccion_db:.3f} dB                     |   Campo E = {campo_e:.3f} dBμV/m\n"
                f"Despeje a = {d1/1000:.3f} Km                          |   Nivel Rx = {nivel_rx_dbm:.3f} dBm\n"
                f"Nivel Rx = {nivel_rx_uv:.3f} μV                              |   Rx Relativo = {rx_relative:.3f} dB\n"
                f"Estadísticas = {estadisticas:.2f} dB                         |    Peor Fresnel = {peor_pct_obst:.2f}F1\n"
            )
            self.results_text.insert("end", results)

            # Actualización de gráfico
            self.ax.clear()
            self.ax.set_axis_on()  # Mostrar ejes al dibujar el gráfico
            self.ax.plot(distancias, elevaciones, label='Perfil de Elevación', color='green')
            self.ax.plot(distancias, los_line, label='Línea de Vista (LOS)', linestyle='--', color='blue')
            zona_fresnel_inf = [los_line[i] - fresnel_radius(distancias[i], distancias[-1] - distancias[i], freq_ghz) for i in range(len(distancias))]
            zona_fresnel_sup = [los_line[i] + fresnel_radius(distancias[i], distancias[-1] - distancias[i], freq_ghz) for i in range(len(distancias))]
            self.ax.fill_between(distancias, zona_fresnel_inf, zona_fresnel_sup, color='orange', alpha=0.3, label='Zona de Fresnel')
            self.ax.scatter(distancias[peor_index], elevaciones[peor_index], color='red', label='Peor Punto')
            self.ax.set_title("Perfil de Elevación")
            self.ax.set_xlabel("Distancia (m)")
            self.ax.set_ylabel("Altura (m)")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()

        except ValueError as e:
            self.results_text.delete("1.0", "end")
            self.results_text.insert("end", f"Error: Please check input values.\n{e}")
        except Exception as e:
            self.results_text.delete("1.0", "end")
            self.results_text.insert("end", f"Unexpected error: {e}")

if __name__ == "__main__":
    app = RadioLinkCalculator()
    app.mainloop()