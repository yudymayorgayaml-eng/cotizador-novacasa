import streamlit as st
from fpdf import FPDF
from datetime import datetime, timedelta
import os

class PDF(FPDF):
    def header(self):
        # Franja roja superior
        self.set_fill_color(218, 37, 29) 
        self.rect(0, 0, 210, 10, 'F')
        
        # BUSCAR LOGO (Busca el archivo que subiste a GitHub)
        logo_path = 'logo_novacasa.png'
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 15, 55) 
        else:
            # Texto de respaldo si el logo no carga
            self.set_font('Arial', 'B', 22)
            self.set_text_color(40, 40, 40)
            self.set_xy(10, 15)
            self.cell(0, 10, 'NOVACASA', ln=True)
            self.set_font('Arial', '', 9)
            self.set_text_color(150, 0, 0)
            self.cell(0, -2, 'remodelación::reparaciones locativas', ln=True)
            
        self.ln(25)

    def footer_cierre(self):
        # Cuadro de Observaciones al final del PDF
        self.set_y(-65)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 7, ' OBSERVACIONES', 0, 1, 'C', True)
        
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 8)
        self.set_draw_color(218, 37, 29)
        obs_texto = (
            "::: Para comenzar el trabajo es necesario recibir aprobación expresa de esta cotización.\n"
            "::: El valor incluye materiales, mano de obra e instalación.\n"
            "::: Entrega del proyecto a convenir con el cliente.\n"
            "::: El valor no incluye descuento por retenciones ni impuestos adicionales."
        )
        self.multi_cell(0, 5, obs_texto, border='LRB')

def create_pdf(datos, items, desc_p):
    pdf = PDF()
    pdf.add_page()
    
    # Colores de bordes y líneas (Rojo Novacasa)
    pdf.set_draw_color(218, 37, 29)
    pdf.set_line_width(0.4)

    # --- BLOQUE CLIENTE (CERRADO) ---
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    pdf.set_xy(10, 45)
    pdf.cell(110, 7, "CLIENTE", 1, 1, 'L', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.rect(10, 52, 110, 22) # Marco del cuadro cliente
    pdf.set_xy(12, 54)
    pdf.multi_cell(55, 4.5, f"NOMBRE: {datos['nombre']}\nATENCIÓN: {datos['atencion']}\nDIRECCIÓN: {datos['direccion']}")
    pdf.set_xy(67, 54)
    # Aquí aparece NIT / CÉDULA en el PDF
    pdf.multi_cell(50, 4.5, f"NIT / CÉDULA: {datos['id_cliente']}\nCIUDAD: {datos['ciudad']}\nTEL: {datos['tel']}")

    # --- BLOQUE FECHAS Y CONDICIONES ---
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(125, 45)
    pdf.cell(37, 7, "FECHA EMISIÓN", 1, 0, 'C', True)
    pdf.cell(37, 7, "FECHA VENCE", 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(125, 52)
    pdf.cell(37, 12, datos['f_emision'].strftime("%d/%m/%Y"), 1, 0, 'C')
    pdf.cell(37, 12, datos['f_vence'].strftime("%d/%m/%Y"), 1, 1, 'C')

    pdf.set_xy(125, 66)
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(74, 5, "CONDICIONES DE PAGO", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(125, 71)
    pdf.cell(74, 6, datos['condiciones'].upper(), 1, 1, 'C')

    pdf.ln(12)

    # --- TABLA DE DETALLE ---
    pdf.set_fill_color(40, 40, 40)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(30, 8, "ZONA", 1, 0, 'C', True)
    pdf.cell(120, 8, "DESCRIPCIÓN DEL SERVICIO", 1, 0, 'C', True)
    pdf.cell(40, 8, "VALOR", 1, 1, 'C', True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 9)
    subtotal = 0
    for i, item in enumerate(items):
        z = datos['zona'] if i == 0 else ""
        pdf.cell(30, 9, z, 1, 0, 'C')
        pdf.cell(120, 9, item['desc'], 1, 0, 'L')
        pdf.cell(40, 9, f"$ {item['val']:,.2f}", 1, 1, 'R')
        subtotal += item['val']

    # Cálculos de Descuento
    monto_desc = subtotal * (desc_p / 100)
    total_neto = subtotal - monto_desc

    if desc_p > 0:
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(150, 8, f"DESCUENTO ({desc_p}%)", 1, 0, 'R')
        pdf.cell(40, 8, f"- $ {monto_desc:,.2f}", 1, 1, 'R')

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(150, 10, "TOTAL A PAGAR", 1, 0, 'R', True)
    pdf.cell(40, 10, f"$ {total_neto:,.2f}", 1, 1, 'R', True)

    pdf.footer_cierre()
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Novacasa App", page_icon="🏠")
st.title("🏠 Generador de Cotizaciones Novacasa")

with st.form("formulario_principal"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Cliente", "Agrupación Navarra")
        atencion = st.text_input("Atención a", "Henry Calceto")
        # Cambio aquí: Ahora pregunta NIT / CÉDULA
        id_cliente = st.text_input("NIT / Cédula")
    
    with col2:
        ciudad = st.text_input("Ciudad", "Bogotá")
        tel = st.text_input("Teléfono")
        direccion = st.text_input("Dirección")
    
    st.write("---")
    c3, c4, c5 = st.columns(3)
    f_emision = c3.date_input("Fecha Emisión", datetime.now())
    f_vence = c4.date_input("Fecha Vencimiento", datetime.now() + timedelta(days=30))
    pago = c5.selectbox("Condiciones de Pago", ["A CONVENIR", "CONTADO", "50% ANTICIPO"])
    
    zona_txt = st.text_input("Zona del Proyecto", "PORTERIA")
    
    st.write("### Servicios a Cotizar")
    n_servicios = st.number_input("Número de ítems", 1, 15, 1)
    servicios_lista = []
    for i in range(n_servicios):
        ca, cb = st.columns([3, 1])
        d = ca.text_input(f"Descripción {i+1}", key=f"desc_{i}")
        v = cb.number_input(f"Valor {i+1}", key=f"val_{i}", format="%.2f")
        servicios_lista.append({'desc': d, 'val': v})
    
    st.write("---")
    porcentaje_desc = st.slider("Aplicar Descuento (%)", 0, 100, 0)
    
    boton_generar = st.form_submit_button("GENERAR Y DESCARGAR PDF")

if boton_generar:
    datos_completos = {
        'nombre': nombre, 'atencion': atencion, 'id_cliente': id_cliente,
        'ciudad': ciudad, 'tel': tel, 'direccion': direccion,
        'f_emision': f_emision, 'f_vence': f_vence, 
        'condiciones': pago, 'zona': zona_txt
    }
    archivo_pdf = create_pdf(datos_completos, servicios_lista, porcentaje_desc)
    st.success("¡PDF generado con éxito!")
    st.download_button(
        label="📥 Descargar Cotización",
        data=archivo_pdf,
        file_name=f"Cotizacion_{nombre}.pdf",
        mime="application/pdf"
    )
