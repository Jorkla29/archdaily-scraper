import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os
from scraper import listar_proyectos, scrapear_detalles
from config import FILTER_CATEGORIES, FILTER_COUNTRIES
from export import export_to_csv

datos_guardados = []

def ejecutar_scraping():
    categorias = [FILTER_CATEGORIES[nombre] for nombre in categoria_var if categoria_var[nombre].get()]
    paises = [FILTER_COUNTRIES[nombre] for nombre in pais_var if pais_var[nombre].get()]

    if not categorias and not paises:
        messagebox.showwarning("Atención", "Selecciona al menos una categoría o país.")
        return

    boton_scrap.config(state="disabled")
    root.update_idletasks()
    estado_var.set("⏳ Scraping en progreso...")
    progress.start()
    try:
        def actualizar_estado(index, total, titulo):
            estado_var.set(f"🛠️ {index}/{total} — {titulo}")
            progress_bar["maximum"] = total
            progress_bar["value"] = index
            root.update_idletasks()
            print(f"[{index}/{total}] {titulo}")

        global datos_guardados
        if datos_guardados and "Categoría" in datos_guardados[0]:
            print("✅ Usando datos ya detallados.")
            resultados = datos_guardados
        else:
            if not datos_guardados:
                print("📥 Listando proyectos...")
                datos_guardados = listar_proyectos(categorias, paises)
            print("🔍 Iniciando scraping detallado...")
            resultados = scrapear_detalles(datos_guardados, actualizar_estado)
            datos_guardados = resultados
        estado_var.set(f"✅ {len(resultados)} proyectos encontrados.")
        # Selección de nombre de archivo personalizado y carpeta
        categoria_nombre = "_".join([k for k, v in categoria_var.items() if v.get()])
        pais_nombre = "_".join([k for k, v in pais_var.items() if v.get()])
        nombre_final = f"archdaily_{categoria_nombre}_{pais_nombre}.csv".replace(" ", "_")

        ruta = filedialog.askdirectory()
        if not ruta:
            estado_var.set("⚠️ Exportación cancelada.")
            return
        filename = os.path.join(ruta, nombre_final)
        filename = export_to_csv(resultados, filename)
        # Imprimir resumen detallado antes del messagebox
        print("\n📦 Scraping completado. Proyectos exportados:")
        for i, row in enumerate(resultados, 1):
            print(f"{i}. {row.get('Título', 'Sin título')} — {row.get('Arquitecto', 'Sin arquitecto')} — {row.get('Ubicación', '')}")
        messagebox.showinfo("Scraping finalizado", f"Datos exportados a: {filename}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        progress.stop()
        progress_bar["value"] = 0
        boton_scrap.config(state="normal")

def contar_proyectos():
    categorias = [FILTER_CATEGORIES[nombre] for nombre in categoria_var if categoria_var[nombre].get()]
    paises = [FILTER_COUNTRIES[nombre] for nombre in pais_var if pais_var[nombre].get()]

    if not categorias and not paises:
        messagebox.showwarning("Atención", "Selecciona al menos una categoría o país.")
        return

    boton_contar.config(state="disabled")
    root.update_idletasks()
    try:
        resultados = listar_proyectos(categorias, paises)
        global datos_guardados
        datos_guardados = resultados
        etiqueta_resultado.config(text=f"Se encontraron {len(resultados)} proyectos.")
        estado_var.set(f"✅ {len(resultados)} proyectos encontrados.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        boton_contar.config(state="normal")

root = tk.Tk()
root.title("Scraper ArchDaily")

# --- ttk style for green buttons ---
style = ttk.Style()
style.theme_use("clam")
style.configure("Green.TButton", foreground="white", background="#28a745")
style.map("Green.TButton",
          background=[("active", "#218838")],
          foreground=[("disabled", "gray")])

ttk.Label(root, text="Scraper de proyectos ArchDaily", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))

def crear_scrollable_frame(contenedor):
    canvas = tk.Canvas(contenedor, width=250, height=300)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scroll_frame

frame_superior = tk.Frame(root)
frame_superior.pack(pady=10)

frame_categorias = ttk.LabelFrame(frame_superior, text="Categorías", padding=10)
frame_categorias.grid(row=0, column=0, padx=10)
frame_scroll_categorias = crear_scrollable_frame(frame_categorias)

frame_paises = ttk.LabelFrame(frame_superior, text="Países", padding=10)
frame_paises.grid(row=0, column=1, padx=10)
frame_scroll_paises = crear_scrollable_frame(frame_paises)

categoria_var = {}
for nombre in FILTER_CATEGORIES:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(frame_scroll_categorias, text=nombre, variable=var)
    chk.pack(anchor="w")
    categoria_var[nombre] = var

pais_var = {}
for nombre in FILTER_COUNTRIES:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(frame_scroll_paises, text=nombre, variable=var)
    chk.pack(anchor="w")
    pais_var[nombre] = var

boton_scrap = ttk.Button(root, text="Iniciar Scraping", command=ejecutar_scraping, style="Green.TButton")
boton_scrap.pack(pady=10)

boton_contar = ttk.Button(root, text="Listar cantidad", command=contar_proyectos, style="Green.TButton")
boton_contar.pack()

etiqueta_resultado = tk.Label(root, text="", font=("Arial", 11))
etiqueta_resultado.pack(pady=10)

estado_var = tk.StringVar()
estado_label = ttk.Label(root, textvariable=estado_var, font=("Arial", 10))
estado_label.pack(pady=(5, 10))

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(pady=(0, 10))

progress_bar = ttk.Progressbar(root, orient="horizontal", mode="determinate", length=300)
progress_bar.pack(pady=(0, 10))

# --- Reiniciar selección ---
def reiniciar_seleccion():
    global datos_guardados
    datos_guardados = []
    etiqueta_resultado.config(text="")
    estado_var.set("🔄 Reiniciado. Puedes volver a listar o scrapear.")

boton_reiniciar = ttk.Button(
    root,
    text="Reiniciar selección",
    command=reiniciar_seleccion,
    style="Green.TButton"
)
boton_reiniciar.pack(pady=(0, 10))

root.mainloop()