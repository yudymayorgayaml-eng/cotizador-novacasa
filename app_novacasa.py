import streamlit as st
from fpdf import FPDF
from datetime import datetime, timedelta
import os
import json

class PDF(FPDF):
    def header(self):
        self.set_fill_color(218, 37, 29) 
        self.rect(0, 0, 210, 10, 'F')
        logo_path = 'logo_novacasa.png'
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 15, 55) 
        else:
            self.set_font('Arial', 'B', 22)
            self.set_text_color(40, 40, 40)
            self.set_xy(10, 15)
            self.cell(0, 10, 'NOVACASA', ln=True)
            self.set_font('Arial', '', 9)
            self.set_text_color(150, 0, 0)
            self.cell(0, -2, 'remodelación::reparaciones locativas', ln=True)
        self.ln(25)

    def footer_cierre(self):
        self.set_y(-65)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 7, ' OBSERVACIONES', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 8)
        self.set_draw_color(218, 37, 29)
        obs_texto = ("::: Para comenzar el trabajo es necesario aprobación expresa.\n"
                     "::: El valor incluye materiales, mano de obra e instalación.\n"
                     "::: Entrega del proyecto a convenir con el cliente.")
        self.multi_cell(0, 5, obs_texto, border='LRB')

def create_pdf(datos, items, desc_p):
    pdf = PDF()
    pdf.add_page()
    pdf.set_draw_color(218, 37, 29)
    pdf.set_line_width(0.4)
    # Bloque cliente
    pdf.set_fill_color(40, 40, 40); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(10, 45); pdf.cell(110, 7, "CLIENTE", 1, 1, 'L', True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 8); pdf.rect(10, 52, 110, 22)
    pdf.set_xy(12, 54); pdf.multi_cell(55, 4.5, f"NOMBRE: {datos['nombre']}\nATENCIÓN: {datos['atencion']}\nDIRECCIÓN: {datos['direccion']}")
    pdf.set_xy(67, 54); pdf.multi_cell(50, 4.5, f"NIT / CÉDULA: {datos['id_cliente']}\nCIUDAD: {datos['ciudad']}\nTEL: {datos['tel']}")
    # Bloque fechas
    pdf.set_text_color(255, 255, 255); pdf.set_xy(125, 45); pdf.cell(37, 7, "FECHA EMISIÓN", 1, 0, 'C', True); pdf.cell(37, 7, "FECHA VENCE", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(125, 52); pdf.cell(37, 12, datetime.strptime(datos['f_emision'], '%Y-%m-%d').strftime("%d/%m/%Y"), 1, 0, 'C'); pdf.cell(37, 12, datetime.strptime(datos['f_vence'], '%Y-%m-%d').strftime("%d/%m/%Y"), 1, 1, 'C')
    # Tabla
    pdf.ln(25)
    pdf.set_fill_color(40, 40, 40); pdf.set_text_color(255, 255, 255); pdf.cell(30, 8, "ZONA", 1, 0, 'C', True); pdf.cell(120, 8, "DESCRIPCIÓN DEL SERVICIO", 1, 0, 'C', True); pdf.cell(40, 8, "VALOR", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 9)
    subtotal = 0
    zona_completa = ", ".join(datos['zonas_lista'])
    for i, item in enumerate(items):
        z = zona_completa if i == 0 else ""
        pdf.cell(30, 9, z, 1, 0, 'C'); pdf.cell(120, 9, item['desc'], 1, 0, 'L'); pdf.cell(40, 9, f"$ {item['val']:,.2f}", 1, 1, 'R')
        subtotal += item['val']
    
    monto_desc = subtotal * (desc_p / 100)
    total_f = subtotal - monto_desc
    if desc_p > 0:
        pdf.cell(150, 8, f"DESCUENTO ({desc_p}%)", 1, 0, 'R'); pdf.cell(40, 8, f"- $ {monto_desc:,.2f}", 1, 1, 'R')
    pdf.set_fill_color(230, 230, 230); pdf.set_font('Arial', 'B', 10); pdf.cell(150, 10, "TOTAL A PAGAR", 1, 0, 'R', True); pdf.cell(40, 10, f"$ {total_f:,.2f}", 1, 1, 'R', True)
    pdf.footer_cierre()
    return pdf.output(dest='S').encode('latin-1')

# --- LÓGICA DE INTERFAZ ---
st.set_page_config(page_title="Novacasa Pro", page_icon="🏠")
st.title("🏠 Novacasa: Generador de Cotizaciones")

uploaded_file = st.file_uploader("📂 Cargar una cotización anterior (.json)", type=['json'])
saved_data = {}
if uploaded_file is not None:
    saved_data = json.load(uploaded_file)

with st.form("form_principal"):
    col1, col2 = st.columns(2)
    nombre = col1.text_input("Nombre Cliente", saved_data.get('nombre', ""))
    atencion = col2.text_input("Atención a", saved_data.get('atencion', ""))
    id_cliente = st.text_input("NIT / Cédula", saved_data.get('id_cliente', ""))
    
    col3, col4, col5 = st.columns(3)
    ciudad = col3.text_input("Ciudad", saved_data.get('ciudad', ""))
    tel = col4.text_input("Teléfono", saved_data.get('tel', ""))
    direccion = st.text_input("Dirección", saved_data.get('direccion', ""))
    
    # Fechas por defecto: hoy y +30 días si no hay datos cargados
    f_emision = st.date_input("Fecha Emisión", datetime.strptime(saved_data.get('f_emision', str(datetime.now().date())), '%Y-%m-%d'))
    f_vence = st.date_input("Fecha Vencimiento", datetime.strptime(saved_data.get('f_vence', str((datetime.now() + timedelta(days=30)).date())), '%Y-%m-%d'))
    pago = st.selectbox("Pago", ["A CONVENIR", "CONTADO", "50% ANTICIPO"])
    
    st.write("---")
    n_zonas = st.number_input("Número de zonas", 1, 10, len(saved_data.get('zonas_lista', [1])))
    zonas_lista = []
    cols_z = st.columns(2)
    for i in range(int(n_zonas)):
        val_z = saved_data.get('zonas_lista', [""])[i] if i < len(saved_data.get('zonas_lista', [])) else ""
        z_nom = cols_z[i % 2].text_input(f"Zona {i+1}", value=val_z, key=f"z_{i}")
        if z_nom: zonas_lista.append(z_nom)
    
    st.write("---")
    n_items = st.number_input("Número de ítems", 1, 15, len(saved_data.get('items', [1])))
    servicios_lista = []
    for i in range(int(n_items)):
        ca, cb = st.columns([3, 1])
        val_d = saved_data.get('items', [])[i]['desc'] if i < len(saved_data.get('items', [])) else ""
        val_v = saved_data.get('items', [])[i]['val'] if i < len(saved_data.get('items', [])) else 0.0
        d = ca.text_input(f"Descripción {i+1}", value=val_d, key=f"d_{i}")
        v = cb.number_input(f"Valor {i+1}", value=float(val_v), key=f"v_{i}")
        servicios_lista.append({'desc': d, 'val': v})
    
    desc_p = st.slider("Descuento %", 0, 100, saved_data.get('desc_p', 0))
    
    col_btn1, col_btn2 = st.columns(2)
    btn_pdf = col_btn1.form_submit_button("🚀 GENERAR PDF")
    btn_save = col_btn2.form_submit_button("💾 GUARDAR BORRADOR")

datos_finales = {
    'nombre': nombre, 'atencion': atencion, 'id_cliente': id_cliente,
    'ciudad': ciudad, 'tel': tel, 'direccion': direccion,
    'f_emision': str(f_emision), 'f_vence': str(f_vence), 
    'condiciones': pago, 'zonas_lista': zonas_lista, 
    'items': servicios_lista, 'desc_p': desc_p
}

if btn_pdf:
    pdf_bytes = create_pdf(datos_finales, servicios_lista, desc_p)
    st.download_button("📥 DESCARGAR PDF", pdf_bytes, f"Coti_{nombre}.pdf")

if btn_save:
    json_string = json.dumps(datos_finales)
    st.download_button("💾 DESCARGAR BORRADOR (.json)", json_string, f"Datos_{nombre}.json", "application/json")
