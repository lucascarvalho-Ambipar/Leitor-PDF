import streamlit as st
from pypdf import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile

# 1. Configuração de inicialização da página
st.set_page_config(
    page_title="AMBIPAR - Gestão de PDFs", 
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeção de CSS Avançado para Identidade Visual Corporativa (#D4FF00)
st.markdown("""
<style>
    /* Ocultar menus padrões do Streamlit para focar na marca */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilização Geral do App */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Banner Superior Corporativo */
    .corporate-header {
        background-color: #1A1F2C;
        padding: 25px;
        border-radius: 8px;
        border-left: 8px solid #D4FF00;
        margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
    }
    .corporate-header h1 {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-size: 26px !important;
        letter-spacing: 0.5px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .corporate-header h1 span {
        color: #D4FF00 !important;
        font-weight: 800;
    }
    .corporate-header p {
        color: #9BA3B0 !important;
        margin: 6px 0 0 0 !important;
        font-size: 14px;
    }

    /* Customização de Botões (Cor #D4FF00 com alto contraste) */
    div.stButton > button:first-child {
        background-color: #D4FF00 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 28px !important;
        box-shadow: 0px 4px 10px rgba(212, 255, 0, 0.15);
        transition: all 0.3s ease-in-out;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background-color: #E5FF33 !important;
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(212, 255, 0, 0.3);
    }
    
    /* Botões de Download secundários */
    div.stDownloadButton > button {
        background-color: transparent !important;
        color: #D4FF00 !important;
        border: 2px solid #D4FF00 !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        transition: all 0.2s ease;
    }
    div.stDownloadButton > button:hover {
        background-color: rgba(212, 255, 0, 0.1) !important;
        color: #D4FF00 !important;
    }

    /* Customização das Abas (Tabs) */
    button[data-baseweb="tab"] {
        color: #9BA3B0 !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #D4FF00 !important;
        color: #D4FF00 !important;
        font-weight: bold !important;
    }

    /* Linhas de progresso na cor da marca */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #D4FF00 !important;
    }
    
    /* Customização de caixas de texto e inputs */
    div[data-testid="stMarkdownContainer"] strong {
        color: #D4FF00;
    }
</style>
""", unsafe_allow_html=True)

# 3. Barra Lateral (Sidebar) Organizacional
with st.sidebar:
    st.image("https://img.icons8.com/color/96/database-administrator.png", width=60)
    st.markdown("### **Painel de Controle**")
    st.markdown("---")
    st.markdown("""
    **Diretrizes de Uso:**
    * **Varredura:** Suporta múltiplos arquivos PDFs editáveis para conferência de auditoria e relatórios.
    * **Unificação:** Otimizado para consolidação de lotes massivos via arquivos compactados (.zip).
    """)
    st.markdown("---")
    st.caption("Desenvolvido para otimização de processos internos e validação de dados em larga escala.")

# 4. Banner Executivo Superior
st.markdown("""
<div class="corporate-header">
    <h1><span>AMBIPAR</span> — Sistema de Busca e Unificação de PDFs</h1>
    <p>Plataforma corporativa de automação, auditoria de termos e consolidação de documentos em lote.</p>
</div>
""", unsafe_allow_html=True)

# 5. Criação das Abas Principais
tab1, tab2 = st.tabs(["🔍 Varredura Avançada de Nomes", "🔗 Unificador de Documentos em Lote"])

# ==========================================
# ABA 1: VARREDURA DE NOMES
# ==========================================
with tab1:
    st.markdown("### Extração e Cruzamento de Dados")
    st.markdown("Insira os documentos e os termos desejados para realizar a busca indexada por página.")
    
    # Layout em colunas para organizar os inputs de forma simétrica
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_files_varredura = st.file_uploader("Upload de arquivos fontes (PDF)", type=["pdf"], accept_multiple_files=True, key="upload_varredura")
    with col2:
        nomes_busca = st.text_area("Termos ou nomes para localização (separe por vírgula):", placeholder="Ex: Nome do Colaborador, Razão Social, Tipo de Lote", height=95)

    if uploaded_files_varredura and nomes_busca:
        lista_nomes = [nome.strip() for nome in nomes_busca.split(",") if nome.strip()]
        
        st.markdown("---")
        if st.button("Executar Varredura no Banco de Arquivos", type="primary", key="btn_varredura"):
            resultados = []
            termos_encontrados_set = set()
            progresso = st.progress(0)
            
            with st.spinner("Processando acervo digital e mapeando termos..."):
                for idx, uploaded_file in enumerate(uploaded_files_varredura):
                    reader = PdfReader(uploaded_file)
                    for num_pagina in range(len(reader.pages)):
                        texto = reader.pages[num_pagina].extract_text()
                        if texto:
                            for nome in lista_nomes:
                                if nome.lower() in texto.lower():
                                    resultados.append({
                                        "Arquivo Original": uploaded_file.name,
                                        "Página Identificada": num_pagina + 1,
                                        "Termo Localizado": nome
                                    })
                                    termos_encontrados_set.add(nome)
                    progresso.progress((idx + 1) / len(uploaded_files_varredura))
            
            st.markdown("### 📊 Relatório de Conformidade")
            
            # Quadro resumo de checagem direta
            c_enc, c_alt = st.columns([1, 2])
            with c_enc:
                st.markdown("**Status de Verificação:**")
                for nome in lista_nomes:
                    if nome in termos_encontrados_set:
                        st.write(f"✅ **{nome}**")
                    else:
                        st.write(f"❌ <span style='color:#FFAAAA;'>{nome}</span>", unsafe_allow_html=True)
            
            with c_alt:
                if resultados:
                    st.success(f"Processamento concluído. Foram detectadas {len(resultados)} ocorrências dos termos.")
                    df_resultados = pd.DataFrame(resultados)
                    st.dataframe(df_resultados, use_container_width=True)
                    
                    # utf-8-sig garante abertura perfeita com acentuação correta no Excel brasileiro
                    csv = df_resultados.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Exportar Relatório de Auditoria (CSV)", data=csv, file_name="relatorio_auditoria_ambipar.csv", mime="text/csv")
                else:
                    st.warning("Nenhum dos termos mapeados foi localizado no lote de documentos atual.")

# ==========================================
# ABA 2: UNIFICADOR EM LOTE
# ==========================================
with tab2:
    st.markdown("### Consolidação de Comprovantes e Arquivos Massivos")
    st.markdown("Agilize o processamento compactando os documentos em uma pasta **.zip** antes do envio.")
    
    with st.container():
        st.markdown("<div style='background-color: #1A1F2C; padding: 20px; border-radius:6px; margin-bottom:20px;'><strong>Nota de Engenharia:</strong> O upload via pacote compactado (.zip) reduz drasticamente o tráfego de rede do navegador, permitindo a consolidação segura de milhares de registros em alta velocidade.</div>", unsafe_allow_html=True)
        
        arquivos_para_unir = st.file_uploader("Arraste o lote compactado (.zip) ou PDFs avulsos aqui:", type=["pdf", "zip"], accept_multiple_files=True, key="upload_unificar")

    if arquivos_para_unir:
        st.markdown("---")
        if st.button("Consolidar e Unificar Arquivos", type="primary", key="btn_unificar"):
            merger = PdfWriter()
            pdfs_processados = 0
            
            with st.spinner("Compilando dados, organizando páginas e gerando arquivo consolidado..."):
                for file in arquivos_para_unir:
                    if file.name.lower().endswith('.zip'):
                        with zipfile.ZipFile(file) as z:
                            pdf_names = [n for n in z.namelist() if n.lower().endswith('.pdf')]
                            for pdf_name in pdf_names:
                                with z.open(pdf_name) as f:
                                    pdf_bytes = io.BytesIO(f.read())
                                    merger.append(pdf_bytes)
                                    pdfs_processados += 1
                    
                    elif file.name.lower().endswith('.pdf'):
                        merger.append(file)
                        pdfs_processados += 1
                
                if pdfs_processados > 0:
                    output_pdf = io.BytesIO()
                    merger.write(output_pdf)
                    output_pdf.seek(0)
                    
                    st.success(f"✅ Processo concluído com sucesso. Total de {pdfs_processados} documentos unificados em lote.")
                    
                    st.download_button(
                        label="📥 Fazer Download do PDF Unificado",
                        data=output_pdf,
                        file_name="Lote_Documentos_Unificados.pdf",
                        mime="application/pdf",
                        key="download_merge"
                    )
                else:
                    st.error("Falha no processamento: Nenhum arquivo no formato PDF foi identificado na estrutura enviada.")
