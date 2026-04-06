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
            self.set_font('Arial', 'B', 22); self.set_text_color(40, 40, 40)
            self.set_xy(10, 15); self.cell(0, 10, 'NOVACASA', ln=True)
        self.ln(25)

    def footer_cierre(self):
        self.set_y(-60)
        self.set_fill_color(40, 40, 40); self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10); self.cell(0, 7, ' OBSERVACIONES', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 8); self.set_draw_color(218, 37, 29)
        obs = ("::: Para comenzar el trabajo es necesario aprobación expresa.\n"
               "::: El valor incluye materiales, mano de obra e instalación.\n"
               "::: Entrega del proyecto a convenir con el cliente.")
        self.multi_cell(0, 5, obs, border='LRB')

def create_pdf(datos, zonas_data, desc_p):
    pdf = PDF()
    pdf.add_page()
    pdf.set_draw_color(218, 37, 29); pdf.set_line_width(0.4)

    # Bloque Cliente
    pdf.set_fill_color(40, 40, 40); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(10, 45); pdf.cell(110, 7, "CLIENTE", 1, 1, 'L', True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 8); pdf.rect(10, 52, 110, 22)
    pdf.set_xy(12, 54); pdf.multi_cell(55, 4.5, f"NOMBRE: {datos['nombre']}\nATENCIÓN: {datos['atencion']}\nDIRECCIÓN: {datos['direccion']}")
    pdf.set_xy(67, 54); pdf.multi_cell(50, 4.5, f"NIT / CÉDULA: {datos['id_cliente']}\nCIUDAD: {datos['ciudad']}\nTEL: {datos['tel']}")

    # Bloque Fechas y PAGO (Corregido)
    pdf.set_text_color(255, 255, 255); pdf.set_xy(125, 45)
    pdf.cell(37, 7, "FECHA EMISIÓN", 1, 0, 'C', True); pdf.cell(37, 7, "FECHA VENCE", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(125, 52)
    pdf.cell(37, 12, datetime.strptime(datos['f_emision'], '%Y-%m-%d').strftime("%d/%m/%Y"), 1, 0, 'C')
    pdf.cell(37, 12, datetime.strptime(datos['f_vence'], '%Y-%m-%d').strftime("%d/%m/%Y"), 1, 1, 'C')
    
    pdf.set_xy(125, 66)
    pdf.set_fill_color(40, 40, 40); pdf.set_text_color(255, 255, 255)
    pdf.cell(74, 5, "CONDICIONES DE PAGO", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(125, 71)
    pdf.cell(74, 6, datos['condiciones'].upper(), 1, 1, 'C') # Aquí se imprime el pago

    pdf.ln(15)
    
    # Tabla de Contenido por Zonas
    subtotal_general = 0
    for zona_nombre, items in zonas_data.items():
        if not items: continue
        # Encabezado de Zona
        pdf.set_fill_color(230, 230, 230); pdf.set_font('Arial', 'B', 9)
        pdf.cell(150, 7, f" ZONA: {zona_nombre.upper()}", 1, 0, 'L', True)
        pdf.cell(40, 7, "VALOR", 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 9)
        for item in items:
            pdf.cell(150, 8, f"   - {item['desc']}", 1, 0, 'L')
            pdf.cell(40, 8, f"$ {item['val']:,.2f}", 1, 1, 'R')
            subtotal_general += item['val']
        pdf.ln(2)

    # Totales
    monto_desc = subtotal_general * (desc_p / 100)
    total_f = subtotal_general - monto_desc
    
    pdf.ln(5)
    if desc_p > 0:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(150, 8, f"DESCUENTO ({desc_p}%)", 1, 0, 'R')
        pdf.cell(40, 8, f"- $ {monto_desc:,.2f}", 1, 1, 'R')
    
    pdf.set_fill_color(40, 40, 40); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 10)
    pdf.cell(150, 10, "TOTAL A PAGAR", 1, 0, 'R', True)
    pdf.cell(40, 10, f"$ {total_f:,.2f}", 1, 1, 'R', True)

    pdf.footer_cierre()
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.set_page_config(page_title="Novacasa Pro", layout="centered")
st.title("🏠 Novacasa: Cotizador por Zonas")

uploaded_file = st.file_uploader("📂 Cargar borrador (.json)", type=['json'])
saved_data = json.load(uploaded_file) if uploaded_file else {}

with st.form("form_pro"):
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Cliente", saved_data.get('nombre', ""))
    atencion = c2.text_input("Atención a", saved_data.get('atencion', ""))
    id_cliente = st.text_input("NIT / Cédula", saved_data.get('id_cliente', ""))
    
    c3, c4, c5 = st.columns(3)
    ciudad = c3.text_input("Ciudad", saved_data.get('ciudad', ""))
    tel = c4.text_input("Teléfono", saved_data.get('tel', ""))
    direccion = st.text_input("Dirección", saved_data.get('direccion', ""))
    
    f_e = st.date_input("Emisión", datetime.strptime(saved_data.get('f_emision', str(datetime.now().date())), '%Y-%m-%d'))
    f_v = st.date_input("Vencimiento", datetime.strptime(saved_data.get('f_vence', str((datetime.now() + timedelta(days=30)).date())), '%Y-%m-%d'))
    
    # Campo PAGO
    pago_opciones = ["A CONVENIR", "CONTADO", "50% ANTICIPO"]
    pago_idx = pago_opciones.index(saved_data.get('condiciones', "A CONVENIR")) if saved_data.get('condiciones') in pago_opciones else 0
    pago = st.selectbox("Pago", pago_opciones, index=pago_idx)
    
    st.write("---")
    n_zonas = st.number_input("¿Cuántas zonas tiene el proyecto?", 1, 10, 1)
    
    zonas_finales = {}
    for i in range(int(n_zonas)):
        z_nom = st.text_input(f"Nombre de Zona {i+1} (ej: Baño)", key=f"zn_{i}").strip()
        if z_nom:
            n_its = st.number_input(f"¿Cuántos items en {z_nom}?", 1, 10, 1, key=f"ni_{i}")
            items_zona = []
            for j in range(int(n_its)):
                ca, cb = st.columns([3, 1])
                d = ca.text_input(f"Descripción {j+1}", key=f"d_{i}_{j}")
                v = cb.number_input(f"Valor", key=f"v_{i}_{j}", format="%.2f")
                items_zona.append({'desc': d, 'val': v})
            zonas_finales[z_nom] = items_zona
            st.write("---")

    desc_p = st.slider("Descuento %", 0, 100, saved_data.get('desc_p', 0))
    
    c_b1, c_b2 = st.columns(2)
    btn_pdf = c_b1.form_submit_button("🚀 GENERAR PDF")
    btn_save = c_b2.form_submit_button("💾 GUARDAR BORRADOR")

datos_finales = {
    'nombre': nombre, 'atencion': atencion, 'id_cliente': id_cliente,
    'ciudad': ciudad, 'tel': tel, 'direccion': direccion,
    'f_emision': str(f_e), 'f_vence': str(f_v), 'condiciones': pago, 'desc_p': desc_p
}

if btn_pdf:
    pdf_b = create_pdf(datos_finales, zonas_finales, desc_p)
    st.download_button("📥 DESCARGAR PDF", pdf_b, f"Novacasa_{nombre}.pdf")

if btn_save:
    datos_finales['zonas_data'] = zonas_finales # Guardar estructura completa
    st.download_button("💾 GUARDAR JSON", json.dumps(datos_finales), f"Borrador_{nombre}.json")
