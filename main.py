import subprocess

print("🌀 Ejecutando generación de enlaces...")
subprocess.run(["python3", "SacaURLS California Other.py"], check=True)

print("\n🔎 Ejecutando scraping de proyectos...")
subprocess.run(["python3", "scrapear_proyectos.py"], check=True)

print("\n✅ Proceso completo.")