import streamlit as st
from pypdf import PdfReader, PdfWriter
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
    /* Ocultar menus padrões */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fundo Clean Cinza Claro e Texto Padrão Preto */
    .stApp {
        background-color: #F4F6F9;
    }
    .stMarkdown, label, p, .stText {
        color: #000000 !important;
    }
    h2, h3 {
        color: #000000 !important;
    }

    /* Banner Superior */
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

    /* Botões Primários */
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
    
    /* Botões de Download */
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

    /* Customização das Abas (Tabs) */
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

    /* Barra de progresso */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #D4FF00 !important;
    }
    
    /* Caixas de notificação */
    div[data-testid="stInfo"] { background-color: #E8F4FD; color: #000000; border-radius: 6px; }
    div[data-testid="stSuccess"] { background-color: #E6F4EA; color: #000000; border-radius: 6px; }
    div[data-testid="stWarning"] { background-color: #FFF3E0; color: #000000; border-radius: 6px; }
    div[data-testid="stError"] { background-color: #FCE8E6; color: #000000; border-radius: 6px; }
</style>
''', unsafe_allow_html=True)

# 3. Banner Executivo Superior
st.markdown("""
<div class="corporate-header">
    <h1><span>AMBIPAR</span> - Sistema de Busca e Extração de PDFs</h1>
    <p>Plataforma para localização rápida de comprovantes e consolidação de lotes.</p>
</div>
""", unsafe_allow_html=True)

# 4. Criação das Abas Principais
tab1, tab2, tab3 = st.tabs([
    "🔍 Busca - PDF Único", 
    "📂 Busca - PDFs Unitários (ZIP)", 
    "🔗 Unificador de Lotes"
])

# ==========================================
# ABA 1: VARREDURA E EXTRAÇÃO (PDF ÚNICO)
# ==========================================
with tab1:
    st.markdown("### Extração Consolidada (1 Arquivo Final)")
    st.markdown("Busque por termos e receba **um único arquivo PDF** contendo todas as páginas encontradas.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_files_varredura = st.file_uploader("Upload do(s) arquivo(s) fonte (PDF)", type=["pdf"], accept_multiple_files=True, key="upload_varredura_1")
    with col2:
        nomes_busca = st.text_area("Termos ou valores para buscar (separe por PONTO E VÍRGULA):", placeholder="Ex: João da Silva; Maria de Souza; 107,54", height=95, key="text_busca_1")

    if uploaded_files_varredura and nomes_busca:
        arquivos_invalidos = [f.name for f in uploaded_files_varredura if not f.name.lower().endswith('.pdf')]
        
        if arquivos_invalidos:
            st.error(f"⚠️ Arquivo(s) bloqueado(s): {', '.join(arquivos_invalidos)}")
        else:
            lista_nomes = [nome.strip() for nome in nomes_busca.split(";") if nome.strip()]
            
            st.markdown("---")
            if st.button("Buscar e Extrair (PDF Único)", type="primary", key="btn_varredura_1"):
                resultados = []
                termos_encontrados_set = set()
                pdf_extracao = PdfWriter()
                teve_extracao = False
                
                progresso = st.progress(0)
                
                with st.spinner("Lendo arquivos e unificando comprovantes..."):
                    for idx, uploaded_file in enumerate(uploaded_files_varredura):
                        reader = PdfReader(uploaded_file)
                        paginas_ja_extraidas = set()
                        
                        for num_pagina in range(len(reader.pages)):
                            texto = reader.pages[num_pagina].extract_text()
                            if texto:
                                for nome in lista_nomes:
                                    if nome.lower() in texto.lower():
                                        resultados.append({"Arquivo Original": uploaded_file.name, "Página Extraída": num_pagina + 1, "Termo Vinculado": nome})
                                        termos_encontrados_set.add(nome)
                                        
                                        if num_pagina not in paginas_ja_extraidas:
                                            pdf_extracao.add_page(reader.pages[num_pagina])
                                            paginas_ja_extraidas.add(num_pagina)
                                            teve_extracao = True
                                            
                        progresso.progress((idx + 1) / len(uploaded_files_varredura))
                
                st.markdown("### 📊 Resultado da Operação")
                c_enc, c_alt = st.columns([1, 2])
                with c_enc:
                    st.markdown("**Status da Busca:**")
                    for nome in lista_nomes:
                        if nome in termos_encontrados_set:
                            st.write(f"✅ **{nome}**")
                        else:
                            st.write(f"❌ <span style='color:#E53935;'>{nome}</span>", unsafe_allow_html=True)
                with c_alt:
                    if teve_extracao:
                        st.success("Busca finalizada! As páginas foram separadas com sucesso.")
                        output_pdf = io.BytesIO()
                        pdf_extracao.write(output_pdf)
                        output_pdf.seek(0)
                        
                        st.download_button("📥 Baixar PDF Consolidado", data=output_pdf, file_name="Comprovantes_Extraidos_Unificado.pdf", mime="application/pdf")
                        st.dataframe(pd.DataFrame(resultados), use_container_width=True)
                    else:
                        st.warning("Nenhum comprovante encontrado.")

# ==========================================
# ABA 2: VARREDURA E EXTRAÇÃO (PDFs UNITÁRIOS EM ZIP)
# ==========================================
with tab2:
    st.markdown("### Extração Unitária (Múltiplos Arquivos)")
    st.markdown("Busque por termos e receba **uma pasta compactada (.ZIP)** com arquivos PDF separados para cada termo encontrado.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_files_unitarios = st.file_uploader("Upload do(s) arquivo(s) fonte (PDF)", type=["pdf"], accept_multiple_files=True, key="upload_varredura_2")
    with col2:
        nomes_busca_unit = st.text_area("Termos ou valores para buscar (separe por PONTO E VÍRGULA):", placeholder="Ex: João da Silva; Maria de Souza; 107,54", height=95, key="text_busca_2")

    if uploaded_files_unitarios and nomes_busca_unit:
        arquivos_invalidos = [f.name for f in uploaded_files_unitarios if not f.name.lower().endswith('.pdf')]
        
        if arquivos_invalidos:
            st.error(f"⚠️ Arquivo(s) bloqueado(s): {', '.join(arquivos_invalidos)}")
        else:
            lista_nomes = [nome.strip() for nome in nomes_busca_unit.split(";") if nome.strip()]
            
            st.markdown("---")
            if st.button("Buscar e Extrair (Pasta ZIP)", type="primary", key="btn_varredura_2"):
                resultados_unit = []
                termos_encontrados_set_unit = set()
                
                # Cria um "criador de PDF" independente para CADA nome pesquisado
                escritores_por_nome = {nome: PdfWriter() for nome in lista_nomes}
                teve_extracao_unitaria = False
                
                progresso_unit = st.progress(0)
                
                with st.spinner("Lendo arquivos e gerando PDFs individuais..."):
                    for idx, uploaded_file in enumerate(uploaded_files_unitarios):
                        reader = PdfReader(uploaded_file)
                        
                        for num_pagina in range(len(reader.pages)):
                            texto = reader.pages[num_pagina].extract_text()
                            if texto:
                                for nome in lista_nomes:
                                    if nome.lower() in texto.lower():
                                        resultados_unit.append({"Arquivo Original": uploaded_file.name, "Página Extraída": num_pagina + 1, "Termo Vinculado": nome})
                                        termos_encontrados_set_unit.add(nome)
                                        # Adiciona a página apenas no PDF daquele nome específico
                                        escritores_por_nome[nome].add_page(reader.pages[num_pagina])
                                        teve_extracao_unitaria = True
                                        
                        progresso_unit.progress((idx + 1) / len(uploaded_files_unitarios))
                
                st.markdown("### 📊 Resultado da Operação")
                c_enc, c_alt = st.columns([1, 2])
                with c_enc:
                    st.markdown("**Status da Busca:**")
                    for nome in lista_nomes:
                        if nome in termos_encontrados_set_unit:
                            st.write(f"✅ **{nome}**")
                        else:
                            st.write(f"❌ <span style='color:#E53935;'>{nome}</span>", unsafe_allow_html=True)
                with c_alt:
                    if teve_extracao_unitaria:
                        st.success("Busca finalizada! Os arquivos individuais foram gerados.")
                        
                        # Cria o arquivo ZIP na memória
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for nome, writer in escritores_por_nome.items():
                                if len(writer.pages) > 0: # Se achou páginas para esse nome
                                    pdf_bytes = io.BytesIO()
                                    writer.write(pdf_bytes)
                                    
                                    # Limpa o nome para evitar erro no arquivo (remove barras e acentos problemáticos)
                                    nome_arquivo_limpo = "".join(c for c in nome if c.isalnum() or c in " ._-").strip()
                                    if not nome_arquivo_limpo:
                                        nome_arquivo_limpo = "documento_extraido"
                                        
                                    zip_file.writestr(f"{nome_arquivo_limpo}.pdf", pdf_bytes.getvalue())
                        
                        zip_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Baixar Pasta ZIP com PDFs Separados", 
                            data=zip_buffer, 
                            file_name="Comprovantes_Individuais.zip", 
                            mime="application/zip"
                        )
                        st.dataframe(pd.DataFrame(resultados_unit), use_container_width=True)
                    else:
                        st.warning("Nenhum comprovante correspondente aos termos pesquisados foi encontrado.")

# ==========================================
# ABA 3: UNIFICADOR EM LOTE
# ==========================================
with tab3:
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
                    st.download_button("📥 Fazer Download do PDF Unificado", data=output_pdf, file_name="Lote_Documentos_Unificados.pdf", mime="application/pdf", key="download_merge")
                else:
                    st.error("Falha no processamento: Nenhum arquivo no formato PDF foi identificado na estrutura enviada.")
