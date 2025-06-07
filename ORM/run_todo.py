import subprocess
import sys

scripts = [
    "contraseña.py",
    "models.py",
    "inserts.py",
    "triggers.py",
    "views.py",
    "app.py"
]

print("🚀 Iniciando ejecución secuencial de scripts...\n")

for script in scripts:
    print(f"🔄 Ejecutando: {script}")
    try:
        subprocess.run([sys.executable, script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar {script}: {e}")
        break
    print(f"✅ Finalizado: {script}\n")

print("✅ Proceso completo.")
