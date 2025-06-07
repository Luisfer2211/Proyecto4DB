# contraseña.py
import getpass

def guardar_contraseña():
    contraseña = getpass.getpass("🔒 Ingresa tu contraseña de PostgreSQL (no te preocupes si no ves lo que escribes, sí lo está leyendo el programa): ")
    with open("contraseña.txt", "w", encoding="utf-8") as f:
        f.write(contraseña)
    print("✅ Contraseña guardada en 'contraseña.txt'.")

if __name__ == "__main__":
    guardar_contraseña()
