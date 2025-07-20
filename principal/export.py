import csv
import datetime
import os

def export_to_csv(data, filename=None):
    if not filename:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"archdaily_{today}.csv"

    fieldnames = [
        "Título", "Enlace", "Categoría", "Ciudad", "País",
        "Arquitecto", "Área", "Año", "Fotógrafo", "Web/Email"
    ]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            ubicacion = row.get("Ubicación", "")
            partes = [p.strip() for p in ubicacion.split(",")]
            ciudad = partes[0] if len(partes) > 0 else ""
            pais = partes[1] if len(partes) > 1 else ""

            writer.writerow({
                "Título": row.get("Título", ""),
                "Enlace": row.get("Enlace", ""),
                "Categoría": row.get("Categoría", ""),
                "Ciudad": ciudad,
                "País": pais,
                "Arquitecto": row.get("Arquitecto", ""),
                "Área": row.get("Área", ""),
                "Año": row.get("Año", ""),
                "Fotógrafo": row.get("Fotógrafo", ""),
                "Web/Email": row.get("Web/Email", "")
            })

    return filename