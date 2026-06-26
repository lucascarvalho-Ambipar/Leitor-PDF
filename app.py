import streamlit as st
from pypdf import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile

# Configuração da página
st.set_page_config(page_title="Hub de Automação de PDFs", page_icon="📄", layout="wide")

# Aplicando o toque profissional com a cor #D4FF00 via CSS
st.markdown("""
<style>
.stApp { border-top: 5px solid #D4FF00; }
div.stButton > button:first-child {
    background-color: #D4FF00;
    color: #000000;
    font-weight: bold;
    border: none;
    border-radius: 5px;
}
div.stButton > button:first-child:hover {
    background-color: #b5d900;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 Hub de Automação de PDFs")
st.markdown("Selecione a ferramenta que deseja utilizar nas abas abaixo:")

tab1, tab2 = st.tabs(["🔍 Varredura de Nomes", "🔗 Unificador de Comprovantes em Lote"])

# ==========================================
# ABA 1: VARREDURA DE NOMES
# ==========================================
with tab1:
    st.header("🔍 Varredura de Arquivos")
    st.markdown("Busque nomes específicos dentro de múltiplos PDFs.")
    
    uploaded_files_varredura = st.file_uploader("Carregue os PDFs para varredura", type=["pdf"], accept_multiple_files=True, key="upload_varredura")
    nomes_busca = st.text_input("Nomes para buscar (separe por vírgula):", placeholder="Ex: João Silva, Maria Souza")

    if uploaded_files_varredura and nomes_busca:
        lista_nomes = [nome.strip() for nome in nomes_busca.split(",") if nome.strip()]
        
        if st.button("Iniciar Varredura", type="primary", key="btn_varredura"):
            resultados = []
            termos_encontrados_set = set()
            progresso = st.progress(0)
            
            with st.spinner("Analisando documentos..."):
                for idx, uploaded_file in enumerate(uploaded_files_varredura):
                    reader = PdfReader(uploaded_file)
                    for num_pagina in range(len(reader.pages)):
                        texto = reader.pages[num_pagina].extract_text()
                        if texto:
                            for nome in lista_nomes:
                                if nome.lower() in texto.lower():
                                    resultados.append({
                                        "Arquivo": uploaded_file.name,
                                        "Página": num_pagina + 1,
                                        "Nome Encontrado": nome
                                    })
                                    termos_encontrados_set.add(nome)
                    progresso.progress((idx + 1) / len(uploaded_files_varredura))
            
            st.subheader("📊 Resultado da Análise")
            if resultados:
                st.success(f"Varredura concluída! {len(resultados)} ocorrências.")
                df_resultados = pd.DataFrame(resultados)
                st.dataframe(df_resultados, use_container_width=True)
                
                csv = df_resultados.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 Baixar Relatório (CSV)", data=csv, file_name="relatorio_varredura.csv", mime="text/csv")
            else:
                st.warning("Nenhum nome localizado.")

# ==========================================
# ABA 2: UNIFICADOR (COM SUPORTE A ZIP)
# ==========================================
with tab2:
    st.header("🔗 Unificar Comprovantes (Lote/ZIP)")
    st.markdown("Junte milhares de comprovantes submetendo um único arquivo **.zip** ou PDFs avulsos.")
    
    arquivos_para_unir = st.file_uploader("Selecione um arquivo .zip (ou vários PDFs):", type=["pdf", "zip"], accept_multiple_files=True, key="upload_unificar")

    if arquivos_para_unir:
        st.info("💡 **Dica:** Ao subir um arquivo .zip, o sistema processará todos os PDFs contidos nele em alta velocidade na nuvem.")
        
        if st.button("Unir Arquivos Agora", type="primary", key="btn_unificar"):
            merger = PdfWriter()
            pdfs_processados = 0
            
            with st.spinner("Processando e unindo comprovantes... Isso pode levar alguns segundos."):
                for file in arquivos_para_unir:
                    # Se for um arquivo ZIP
                    if file.name.lower().endswith('.zip'):
                        with zipfile.ZipFile(file) as z:
                            # Filtra apenas arquivos PDF dentro do ZIP
                            pdf_names = [n for n in z.namelist() if n.lower().endswith('.pdf')]
                            
                            for pdf_name in pdf_names:
                                with z.open(pdf_name) as f:
                                    # Lê o PDF da memória do ZIP e adiciona ao unificador
                                    pdf_bytes = io.BytesIO(f.read())
                                    merger.append(pdf_bytes)
                                    pdfs_processados += 1
                    
                    # Se for um PDF direto
                    elif file.name.lower().endswith('.pdf'):
                        merger.append(file)
                        pdfs_processados += 1
                
                if pdfs_processados > 0:
                    output_pdf = io.BytesIO()
                    merger.write(output_pdf)
                    output_pdf.seek(0)
                    
                    st.success(f"✅ Sucesso! {pdfs_processados} comprovantes foram extraídos e unidos em um único PDF.")
                    st.download_button(
                        label="📥 Baixar PDF Unificado",
                        data=output_pdf,
                        file_name="Comprovantes_Lote_Unificado.pdf",
                        mime="application/pdf",
                        key="download_merge"
                    )
                else:
                    st.error("Nenhum arquivo PDF foi encontrado dentro do(s) arquivo(s) enviado(s)."
