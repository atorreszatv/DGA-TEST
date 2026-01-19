import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Diagnóstico Duval 1", layout="centered")

# --- 1. GEOMETRÍA DEL TRIÁNGULO (ESTÁNDAR) ---
def ternario_a_cartesiano(ch4, c2h4, c2h2):
    total = ch4 + c2h4 + c2h2
    if total == 0: return 0, 0
    pct_ch4 = (ch4 / total) * 100
    pct_c2h4 = (c2h4 / total) * 100
    x = pct_c2h4 + (0.5 * pct_ch4)
    y = (np.sqrt(3) / 2) * pct_ch4
    return x, y

def dibujar_grid(ax, valor, eje, **kwargs):
    if eje == 0: # CH4
        p1 = ternario_a_cartesiano(valor, 100-valor, 0)
        p2 = ternario_a_cartesiano(valor, 0, 100-valor)
    elif eje == 1: # C2H4
        p1 = ternario_a_cartesiano(100-valor, valor, 0)
        p2 = ternario_a_cartesiano(0, valor, 100-valor)
    elif eje == 2: # C2H2
        p1 = ternario_a_cartesiano(100-valor, 0, valor)
        p2 = ternario_a_cartesiano(0, 100-valor, valor)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], **kwargs)

# --- 2. LÓGICA DE DIAGNÓSTICO ---
def obtener_diagnostico(ch4, c2h4, c2h2):
    if ch4 >= 98: return "PD - Descargas Parciales"
    if c2h2 < 4 and c2h4 < 20: return "T1 - Falla Térmica < 300 °C"
    if c2h2 < 4 and 20 <= c2h4 < 50: return "T2 - Falla Térmica 300-700 °C"
    if c2h2 < 15 and c2h4 >= 50: return "T3 - Falla Térmica > 700 °C"
    
    # Ajuste visual: D1 y D2 separadas por 29% en C2H2
    if c2h4 < 23 and c2h2 >= 13: 
        if c2h2 < 29: return "D1 - Descargas Baja Energía"
        else: return "D1/D2 - Zona Crítica"
        
    if c2h4 >= 23 and c2h2 >= 29: return "D2 - Descargas Alta Energía"
    
    return "DT - Mezcla Térmica/Eléctrica"

# --- 3. DEFINICIÓN DE ZONAS (GEOMETRÍA CORREGIDA) ---
def obtener_zonas():
    zonas = []
    # PD
    zonas.append({'lbl': 'PD', 'col': '#E0FFFF', 'pts': [(100,0,0), (98,2,0), (98,0,2)]})
    # T1
    zonas.append({'lbl': 'T1', 'col': '#FFFACD', 'pts': [(98,2,0), (80,20,0), (76,20,4), (96,0,4)]})
    # T2
    zonas.append({'lbl': 'T2', 'col': '#FFD700', 'pts': [(80,20,0), (50,50,0), (46,50,4), (76,20,4)]})
    # T3
    zonas.append({'lbl': 'T3', 'col': '#FF8C00', 'pts': [(50,50,0), (0,100,0), (0,85,15), (35,50,15)]})
    # D1
    zonas.append({'lbl': 'D1', 'col': '#87CEFA', 'pts': [(87,0,13), (64,23,13), (48,23,29), (0,23,77), (0,0,100)]})
    # D2
    zonas.append({'lbl': 'D2', 'col': '#9370DB', 'pts': [(48,23,29), (0,71,29), (0,23,77)]})
    # DT
    zonas.append({'lbl': 'DT', 'col': '#D3D3D3', 'pts': [(96,0,4), (76,20,4), (46,50,4), (35,50,15), (0,85,15), (0,71,29), (48,23,29), (64,23,13), (87,0,13)]})
    return zonas

# --- 4. FUNCIÓN GRAFICADORA PARA WEB ---
def generar_grafico(ch4, c2h4, c2h2, diagnostico):
    fig, ax = plt.subplots(figsize=(10, 9))
    
    # Zonas
    zonas = obtener_zonas()
    for z in zonas:
        pts = [ternario_a_cartesiano(*p) for p in z['pts']]
        poly = patches.Polygon(pts, closed=True, facecolor=z['col'], edgecolor='black', linewidth=1.2, zorder=1)
        ax.add_patch(poly)
        cx = sum(p[0] for p in pts)/len(pts)
        cy = sum(p[1] for p in pts)/len(pts)
        if z['lbl'] == 'PD': cy -= 1.5
        if z['lbl'] == 'D1': cx += 5; cy += 5
        if z['lbl'] == 'D2': cy -= 1
        if z['lbl'] == 'T3': cx -= 2
        if z['lbl'] == 'DT': cy -= 3
        ax.text(cx, cy, z['lbl'], ha='center', va='center', fontsize=11, fontweight='bold', zorder=2, color='#333')

    # Marco
    A, B, C = (50, 86.602), (100, 0), (0, 0)
    ax.plot([C[0], B[0], A[0], C[0]], [C[1], B[1], A[1], C[1]], 'k-', linewidth=2.5, zorder=5)

    # Grid y Ejes
    for i in range(10, 100, 10):
        dibujar_grid(ax, i, 0, color='gray', lw=0.5, ls=':', alpha=0.5, zorder=3)
        dibujar_grid(ax, i, 1, color='gray', lw=0.5, ls=':', alpha=0.5, zorder=3)
        dibujar_grid(ax, i, 2, color='gray', lw=0.5, ls=':', alpha=0.5, zorder=3)
        px, py = ternario_a_cartesiano(i, 100-i, 0)
        ax.text(px + 2, py, str(i), fontsize=9, va='center', ha='left', color='#444')
        px, py = ternario_a_cartesiano(0, i, 100-i)
        ax.text(px, py - 3, str(i), fontsize=9, va='top', ha='center', color='#444')
        px, py = ternario_a_cartesiano(100-i, 0, i)
        ax.text(px - 2, py, str(i), fontsize=9, va='center', ha='right', color='#444')

    # Títulos Ejes
    ax.text(50, -9, '% C2H4 (Etileno)', ha='center', fontsize=12, fontweight='bold')
    ax.text(78, 45, '% CH4 (Metano)', ha='center', rotation=60, fontsize=12, fontweight='bold')
    ax.text(22, 45, '% C2H2 (Acetileno)', ha='center', rotation=-60, fontsize=12, fontweight='bold')
    
    # 100% Markers
    ax.text(50, 90, '100%', ha='center', color='blue', fontsize=9, fontweight='bold')
    ax.text(104, 0, '100%', ha='left', color='green', fontsize=9, fontweight='bold')
    ax.text(-4, 0, '100%', ha='right', color='red', fontsize=9, fontweight='bold')

    # Ploteo Muestra
    px, py = ternario_a_cartesiano(ch4, c2h4, c2h2)
    dibujar_grid(ax, ch4, 0, color='blue', lw=1.5, ls='--', zorder=6)
    dibujar_grid(ax, c2h4, 1, color='green', lw=1.5, ls='--', zorder=6)
    dibujar_grid(ax, c2h2, 2, color='red', lw=1.5, ls='--', zorder=6)
    ax.plot(px, py, marker='o', color='crimson', markersize=9, markeredgecolor='white', markeredgewidth=1.5, zorder=10)
    
    info = f"Muestra:\nCH4: {ch4:.1f}%\nC2H4: {c2h4:.1f}%\nC2H2: {c2h2:.1f}%"
    ax.annotate(info, xy=(px, py), xytext=(110, 85),
                arrowprops=dict(facecolor='black', arrowstyle='->', connectionstyle="arc3,rad=.2"),
                bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="black", alpha=0.9),
                fontsize=10, zorder=10)

    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# --- 5. INTERFAZ DE USUARIO (MAIN) ---
def main():
    st.title("Diagnóstico de Transformadores")
    st.subheader("Método Triángulo de Duval 1 - IEEE C57.104")
    st.markdown("Ingrese las concentraciones de gases en ppm reportadas por el instrumento.")

    col1, col2, col3 = st.columns(3)
    with col1:
        g_ch4 = st.number_input("Metano (CH4) ppm", min_value=0.0, step=1.0)
    with col2:
        g_c2h4 = st.number_input("Etileno (C2H4) ppm", min_value=0.0, step=1.0)
    with col3:
        g_c2h2 = st.number_input("Acetileno (C2H2) ppm", min_value=0.0, step=1.0)

    if st.button("Generar Diagnóstico", type="primary"):
        suma = g_ch4 + g_c2h4 + g_c2h2
        if suma == 0:
            st.error("La suma de gases no puede ser 0.")
        else:
            pct_ch4 = (g_ch4 / suma) * 100
            pct_c2h4 = (g_c2h4 / suma) * 100
            pct_c2h2 = (g_c2h2 / suma) * 100
            
            diag = obtener_diagnostico(pct_ch4, pct_c2h4, pct_c2h2)
            
            st.success(f"**Resultado:** {diag}")
            
            # Gráfico
            fig = generar_grafico(pct_ch4, pct_c2h4, pct_c2h2, diag)
            st.pyplot(fig)
            st.caption("Gráfico generado según norma IEEE C57.104-2019.")

if __name__ == "__main__":
    main()
