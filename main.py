import streamlit as st
import qrcode
from io import BytesIO
import random
import zipfile

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="STUDIO BLACK", page_icon="📸", layout="centered")

# --- DISEÑO PREMIUM (CSS INYECTADO) ---
def apply_custom_css():
    st.markdown("""
        <style>
        /* Títulos centrados y elegantes */
        .brand-title {
            text-align: center;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: 4px;
            margin-bottom: 0px;
        }
        .brand-subtitle {
            text-align: center;
            color: #888888;
            font-size: 1rem;
            letter-spacing: 2px;
            margin-bottom: 30px;
        }
        /* Botones estilo minimalista pro */
        .stButton>button {
            border: 1px solid #555555;
            border-radius: 5px;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            border-color: #FFFFFF;
            color: #FFFFFF;
            box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.1);
        }
        .stDownloadButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# --- BASE DE DATOS TEMPORAL (EN MEMORIA) ---
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

def create_zip(photos):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for photo in photos:
            zip_file.writestr(photo["name"], photo["bytes"])
    return zip_buffer.getvalue()

# --- ENRUTAMIENTO (Camaleón) ---
query_params = st.query_params
client_session_id = query_params.get("session")

# ==========================================
# VISTA DEL CLIENTE
# ==========================================
if client_session_id:
    st.markdown("<div class='brand-title'>STUDIO BLACK</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>ENTREGA DIGITAL</div>", unsafe_allow_html=True)
    
    if client_session_id == db["session_id"] and len(db["photos"]) > 0:
        
        # Tip para celulares
        st.info("💡 **Tip para el celular:** Para guardar una foto directo en tu galería, mantén presionada la imagen y selecciona 'Guardar imagen'.")
        
        # Botón mágico para descargar todo junto
        zip_bytes = create_zip(db["photos"])
        st.download_button(
            label="📦 DESCARGAR TODAS LAS FOTOS (.ZIP)",
            data=zip_bytes,
            file_name=f"Studio_Black_Galeria_{client_session_id}.zip",
            mime="application/zip",
            type="primary"
        )
        
        st.divider()
        
        # Mostrar fotos en cuadrícula
        cols = st.columns(2)
        for index, photo_data in enumerate(db["photos"]):
            with cols[index % 2]:
                st.image(photo_data["bytes"], use_container_width=True)
                st.download_button(
                    label="⬇️ Descargar",
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
    st.markdown("<div class='brand-title'>STUDIO BLACK</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>PANEL DE CONTROL</div>", unsafe_allow_html=True)
    
    # Contraseña de seguridad
    admin_pass = st.sidebar.text_input("🔑 Contraseña de Admin", type="password")
    
    try:
        SECRET_PASS = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        SECRET_PASS = "studio123"
    
    if admin_pass == SECRET_PASS:
        st.sidebar.success("Acceso concedido")
        
        # Botón de limpieza
        if st.sidebar.button("🚨 Nueva Sesión (Borrar Todo)"):
            clear_session()
            
        st.subheader("1. Subir Material")
        uploaded_files = st.file_uploader("Sube los archivos JPG", type=["jpg", "jpeg"], accept_multiple_files=True)
        
        base_url = st.text_input("URL oficial de tu App", value="https://studio-black-delivery.streamlit.app")
        
        if st.button("Generar Galería y QR") and uploaded_files:
            db["photos"] = [{"name": f.name, "bytes": f.getvalue()} for f in uploaded_files]
            db["session_id"] = str(random.randint(1000, 9999))
            
            st.success(f"¡Galería generada con éxito! ID: {db['session_id']}")
            
            final_url = f"{base_url}/?session={db['session_id']}"
            st.write(f"**Enlace del cliente:** [{final_url}]({final_url})")
            
            qr_bytes = generate_qr(final_url)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(qr_bytes, caption="Escanea para entregar", use_container_width=True)
            
    elif admin_pass != "":
        st.sidebar.error("Contraseña incorrecta")
    else:
        st.info("Introduce la contraseña en la barra lateral para acceder.")
