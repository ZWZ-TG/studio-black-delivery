import streamlit as st
import qrcode
from io import BytesIO
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BLACK-STUDIO", page_icon="📸", layout="centered")

# --- BASE DE DATOS TEMPORAL (EN MEMORIA) ---
# Esto permite que tu vista de Admin comparta datos con la vista del Cliente
@st.cache_resource
def get_shared_database():
    return {"session_id": None, "photos": []}

db = get_shared_database()

# --- FUNCIONES AUXILIARES ---
def generate_qr(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def clear_session():
    db["session_id"] = None
    db["photos"] = []
    st.success("🧹 Sesión anterior borrada. Sistema limpio.")

# --- ENRUTAMIENTO (Camaleón) ---
query_params = st.query_params
client_session_id = query_params.get("session")

# ==========================================
# VISTA DEL CLIENTE
# ==========================================
if client_session_id:
    st.title("🖤 BLACK-STUDIO")
    
    if client_session_id == db["session_id"] and len(db["photos"]) > 0:
        st.write("📷 **Tus fotos están listas. ¡Descárgalas ahora! Estarán disponibles por tiempo limitado.**")
        
        # Mostrar fotos en cuadrícula
        cols = st.columns(2)
        for index, photo_data in enumerate(db["photos"]):
            with cols[index % 2]:
                st.image(photo_data["bytes"], use_container_width=True)
                st.download_button(
                    label="⬇️ Descargar Original",
                    data=photo_data["bytes"],
                    file_name=photo_data["name"],
                    mime="image/jpeg",
                    key=f"dl_{index}"
                )
        
        st.divider()
        st.caption("Contacto: p43972892@gmail.com | Bogotá, Colombia")
    else:
        st.error("⚠️ Sesión expirada o ID incorrecto. Por favor, contacta al fotógrafo.")

# ==========================================
# VISTA DEL ADMIN (Tú)
# ==========================================
else:
    st.title("⚙️ Panel de Control | STUDIO BLACK")
    
    # Contraseña de seguridad
    admin_pass = st.sidebar.text_input("Contraseña de Admin", type="password")
    
    # --- SOLUCIÓN AL ERROR DE SECRETS ---
    try:
        # Intenta usar la contraseña segura de la nube
        SECRET_PASS = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        # Si falla (como en tu PC local), usa esta de prueba
        SECRET_PASS = "studio123"
    
    if admin_pass == SECRET_PASS:
        st.sidebar.success("Acceso concedido")
        
        # Botón de limpieza
        if st.sidebar.button("🚨 Nueva Sesión (Borrar Todo)"):
            clear_session()
            
        st.subheader("1. Subir Material")
        uploaded_files = st.file_uploader("Sube los archivos JPG (Ignora los .CR3)", type=["jpg", "jpeg"], accept_multiple_files=True)
        
        base_url = st.text_input("URL de la App (Cámbiala cuando despliegues en Streamlit)", value="http://localhost:8501")
        
        if st.button("Generar Galería y QR") and uploaded_files:
            # Guardar fotos en la memoria compartida
            db["photos"] = [{"name": f.name, "bytes": f.getvalue()} for f in uploaded_files]
            
            # Generar ID único
            db["session_id"] = str(random.randint(1000, 9999))
            st.success(f"¡Galería generada con ID: {db['session_id']}!")
            
            # Generar y mostrar QR
            final_url = f"{base_url}/?session={db['session_id']}"
            st.write(f"**Enlace del cliente:** {final_url}")
            
            qr_bytes = generate_qr(final_url)
            st.image(qr_bytes, caption="Escanea para descargar", width=300)
            
    elif admin_pass != "":
        st.sidebar.error("Contraseña incorrecta")
    else:
        st.info("Introduce la contraseña en la barra lateral para acceder.")