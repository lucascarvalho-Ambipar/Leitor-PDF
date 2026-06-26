import streamlit as st
from pypdf import PdfReader, PdfWriter
from fpdf import FPDF
import pandas as pd
import io
import zipfile

# 1. Configuração de inicialização da página
st.set_page_config(
    page_title="AMBIPAR - Gestão de PDFs", 
    page_icon="📄", 
    layout="wide"
)

# 2. Injeção de CSS para o visual Clean (Cinza, Preto e #D4FF00)
st.markdown('''
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #F4F6F9;
    }
    .stMarkdown, label, p, .stText {
        color: #000000 !important;
    }
    h2, h3 {
        color: #000000 !important;
    }

    .corporate-header {
        background-color: #1A1F2C;
        padding: 25px;
        border-radius: 8px;
        border-left: 8px solid #D4FF00;
        margin-bottom: 25px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }
    .corporate-header h1 {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-size: 26px !important;
    }
    .corporate-header h1 span {
        color: #D4FF00 !important;
    }
    .corporate-header p {
        color: #FFFFFF !important;
        margin: 6px 0 0 0 !important;
        font-size: 14px;
    }

    div.stButton > button:first-child {
        background-color: #D4FF00 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 28px !important;
        width: 100%;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
    div.stButton > button:first-child:hover {
        background-color: #b5d900 !important;
        color: #000000 !important;
    }
    
    div.stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #D4FF00 !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #D4FF00 !important;
        color: #000000 !important;
    }

    button[data-baseweb="tab"] {
        color: #555555 !important;
        font-size: 16px !important;
        padding: 12px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #D4FF00 !important;
        color: #000000 !important;
        font-weight: bold !important;
    }

    div[data-testid="stProgress"] > div > div > div {
        background-color: #D4FF00 !important;
    }
    
    div[data-testid="stInfo"] { background-color: #E8F4FD; color: #000000; border-radius: 6px; }
    div[data-testid="stSuccess"] { background-color: #E6F4EA; color: #000000; border-radius: 6px; }
    div[data-testid="stWarning"] { background-color: #FFF3E0; color: #000000; border-radius: 6px; }
    div[data-testid="stError"] { background-color: #FCE8E6; color: #000000; border-radius: 6px; }
</style>
''', unsafe_allow_html=True)

# Função auxiliar para gerar o relatório em PDF limpo e profissional
def gerar_pdf_relatorio(lista_nomes, termos_encontrados_set, resultados):
    pdf = FPDF()
    pdf.add_page()
    
    # Configurar codificação segura para evitar erros com acentos brasileiros
    def s(texto):
        return texto.encode('latin-1', 'ignore').decode('latin-1')
    
    # Cabeçalho do PDF
    pdf.set_fill_color(26, 31, 44)
    pdf.rect(0, 0, 210, 35, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_y(12)
    pdf.cell(0, 10, s("AMBIPAR - Relatório de Auditoria de Termos"), ln=True, align="C")
    
    # Corpo do Documento
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(45)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, s("1. Resumo da Verificação de Nomes:"), ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 11)
    for nome in lista_nomes:
        status = "ENCONTRADO" if nome in termos_encontrados_set else "NAO ENCONTRADO"
        marcador = "[X]" if status == "ENCONTRADO" else "[ ]"
        pdf.cell(0, 7, s(f"{marcador} {nome} : {status}"), ln=True)
    
    if resultados:
        pdf.ln(8)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, s("2. Detalhes de Localização por Página:"), ln=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "", 10)
        for res in resultados:
            linha = f"- Termo: {res['Termo Localizado']} | Arquivo: {res['Arquivo Original']} (Pág. {res['Página Identificada']})"
            pdf.multi_cell(0, 6, s(linha))
            
    return pdf.output()

# 3. Banner Executivo Superior
st.markdown("""
<div class="corporate-header">
    <h1><span>AMBIPAR</span> - Sistema de Busca e Unificação de PDFs</h1>
    <p>Plataforma de automação, auditoria de termos e consolidação de documentos em lote.</p>
</div>
""", unsafe_allow_html=True)

# 4. Criação das Abas Principais
tab1, tab2 = st.tabs(["🔍 Varredura Avançada de Nomes", "🔗 Unificador de Documentos em Lote"])

# ==========================================
# ABA 1: VARREDURA DE NOMES
# ==========================================
with tab1:
    st.markdown("### Extração e Cruzamento de Dados")
    st.markdown("Insira os documentos e os termos desejados para realizar a busca indexada por página.")
    
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
            
            c_enc, c_alt = st.columns([1, 2])
            with c_enc:
                st.markdown("**Status de Verificação:**")
                for nome in lista_nomes:
                    if nome in termos_encontrados_set:
                        st.write(f"✅ **{nome}**")
                    else:
                        st.write(f"❌ <span style='color:#E53935;'>{nome}</span>", unsafe_allow_html=True)
            
            with c_alt:
                st.success(f"Processamento concluído. Gerando documentos de exportação...")
                df_resultados = pd.DataFrame(resultados)
                
                # Exibe a tabela na tela para conferência rápida
                if resultados:
                    st.dataframe(df_resultados, use_container_width=True)
                
                # Geração do PDF em memória
                pdf_data = gerar_pdf_relatorio(lista_nomes, termos_encontrados_set, resultados)
                
                # Criação do botão de download do PDF corporativo
                st.download_button(
                    label="📥 Baixar Relatório Oficial em PDF",
                    data=bytes(pdf_data),
                    file_name="relatorio_auditoria_ambipar.pdf",
                    mime="application/pdf"
                )

# ==========================================
# ABA 2: UNIFICADOR EM LOTE
# ==========================================
with tab2:
    st.markdown("### Consolidação de Comprovantes e Arquivos Massivos")
    st.markdown("Agilize o processamento compactando os documentos em uma pasta **.zip** antes do envio.")
    
    st.info("💡 **Nota de Engenharia:** O upload via pacote compactado (.zip) reduz o tráfego do navegador, permitindo a consolidação de milhares de registros em alta velocidade.")
        
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
