import streamlit as st
from fpdf import FPDF
from datetime import datetime, timedelta
import os

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
        self.ln(25)

    def footer_cierre(self):
        self.set_y(-60)
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

    # Bloque Cliente y Fechas
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(10, 45)
    pdf.cell(110, 7, "CLIENTE", 1, 1, 'L', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.rect(10, 52, 110, 22)
    pdf.set_xy(12, 54)
    pdf.multi_cell(55, 4.5, f"NOMBRE: {datos['nombre']}\nATENCIÓN: {datos['atencion']}\nDIRECCIÓN: {datos['direccion']}")
    pdf.set_xy(67, 54)
    pdf.multi_cell(50, 4.5, f"NIT / CC: {datos['id_cliente']}\nCIUDAD: {datos['ciudad']}\nTEL: {datos['tel']}")

    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(125, 45)
    pdf.cell(37, 7, "FECHA EMISIÓN", 1, 0, 'C', True)
    pdf.cell(37, 7, "FECHA VENCE", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(125, 52)
    pdf.cell(37, 10, datos['f_emision'].strftime("%d/%m/%Y"), 1, 0, 'C')
    pdf.cell(37, 10, datos['f_vence'].strftime("%d/%m/%Y"), 1, 1, 'C')
    
    pdf.set_xy(125, 64)
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(74, 5, "CONDICIONES DE PAGO", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(125, 69)
    pdf.cell(74, 5, datos['condiciones'].upper(), 1, 1, 'C')

    pdf.ln(12)
    # Tabla con columna de ZONA por cada ítem
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(35, 8, "ZONA", 1, 0, 'C', True)
    pdf.cell(115, 8, "DESCRIPCIÓN DEL SERVICIO", 1, 0, 'C', True)
    pdf.cell(40, 8, "VALOR", 1, 1, 'C', True)

    pdf.set_text_color(0, 0, 0)
    subtotal = sum(i['val'] for i in items)
    for item in items:
        pdf.cell(35, 9, item['zona'], 1, 0, 'C')
        pdf.cell(115, 9, item['desc'], 1, 0, 'L')
        pdf.cell(40, 9, f"$ {item['val']:,.2f}", 1, 1, 'R')

    descuento = subtotal * (desc_p / 100)
    total_neto = subtotal - descuento
    if desc_p > 0:
        pdf.cell(150, 8, f"DESCUENTO ({desc_p}%)", 1, 0, 'R')
        pdf.cell(40, 8, f"- $ {descuento:,.2f}", 1, 1, 'R')
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(150, 10, "TOTAL A PAGAR", 1, 0, 'R', True)
    pdf.cell(40, 10, f"$ {total_neto:,.2f}", 1, 1, 'R', True)

    pdf.footer_cierre()
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ MULTI-ZONA ---
st.title("🏠 Novacasa: Cotización por Zonas")
with st.form("form_zonas"):
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Cliente", "Agrupación Navarra")
    atencion = c2.text_input("Atención a", "Henry Calceto")
    id_cliente = st.text_input("NIT / Cédula")
    
    c3, c4 = st.columns(2)
    ciudad = c3.text_input("Ciudad", "Bogotá")
    tel = c4.text_input("Teléfono")
    direccion = st.text_input("Dirección")
    
    f_emision = st.date_input("Emisión", datetime.now())
    f_vence = st.date_input("Vencimiento", datetime.now() + timedelta(days=30))
    cond_pago = st.selectbox("Pago", ["A CONVENIR", "CONTADO", "50% ANTICIPO"])
    
    st.write("---")
    num = st.number_input("¿Cuántos ítems totales?", 1, 15, 1)
    servs = []
    for i in range(num):
        st.write(f"**Ítem {i+1}**")
        ca, cb, cc = st.columns([1, 2, 1])
        z = ca.text_input("Zona", placeholder="Baño", key=f"z{i}")
        d = cb.text_input("Descripción", key=f"d{i}")
        v = cc.number_input("Valor", key=f"v{i}", format="%.2f")
        servs.append({'zona': z, 'desc': d, 'val': v})
    
    desc_val = st.slider("Descuento %", 0, 100, 0)
    if st.form_submit_button("GENERAR PDF POR ZONAS"):
        d_pdf = {'nombre': nombre, 'atencion': atencion, 'id_cliente': id_cliente,
                 'ciudad': ciudad, 'tel': tel, 'direccion': direccion,
                 'f_emision': f_emision, 'f_vence': f_v, 'condiciones': cond_pago}
        pdf_f = create_pdf(d_pdf, servs, desc_val)
        st.download_button("📥 DESCARGAR", pdf_f, f"Coti_Zonas_{nombre}.pdf")
