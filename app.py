import streamlit as st
from pypdf import PdfReader, PdfWriter
import pandas as pd
import io

# Configuração da página
st.set_page_config(page_title="Hub de Automação de PDFs", page_icon="📄", layout="wide")

# Aplicando o toque profissional com a cor #D4FF00 via CSS (barra superior e botões)
st.markdown("""
<style>
/* Linha de destaque no topo do site */
.stApp {
    border-top: 5px solid #D4FF00;
}
/* Estilizando o botão principal para a cor solicitada */
div.stButton > button:first-child {
    background-color: #D4FF00;
    color: #000000; /* Texto preto para dar contraste com o verde/amarelo neon */
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

# Criando as abas do site
tab1, tab2 = st.tabs(["🔍 Varredura de Nomes", "🔗 Unificador de Comprovantes (Merge)"])

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
            total_arquivos = len(uploaded_files_varredura)
            
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
                    
                    progresso.progress((idx + 1) / total_arquivos)
            
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
# ABA 2: UNIFICADOR DE PDFs
# ==========================================
with tab2:
    st.header("🔗 Unificar Comprovantes")
    st.markdown("Junte milhares de PDFs unitários em um único arquivo estruturado.")
    
    # Dica importante para o usuário sobre volume
    st.info("💡 **Dica de Performance:** Se for processar 4.000 comprovantes, o navegador do seu computador pode ficar lento ao selecionar todos de uma vez. Se isso acontecer, tente fazer upload em lotes (ex: 500 por vez).")
    
    arquivos_para_unir = st.file_uploader("Selecione todos os comprovantes (a ordem de seleção será a ordem do PDF final):", type=["pdf"], accept_multiple_files=True, key="upload_unificar")

    if arquivos_para_unir:
        st.write(f"📁 **{len(arquivos_para_unir)} arquivos carregados e prontos para união.**")
        
        if st.button("Unir Arquivos Agora", type="primary", key="btn_unificar"):
            merger = PdfWriter()
            
            progresso_merge = st.progress(0)
            total_merge = len(arquivos_para_unir)
            
            with st.spinner("Unindo comprovantes... Isso pode levar alguns segundos dependendo da quantidade."):
                for idx, pdf in enumerate(arquivos_para_unir):
                    # Adiciona cada pdf ao objeto merger
                    merger.append(pdf)
                    progresso_merge.progress((idx + 1) / total_merge)
                
                # Salva o arquivo final na memória para download
                output_pdf = io.BytesIO()
                merger.write(output_pdf)
                output_pdf.seek(0)
                
            st.success("✅ PDFs unidos com sucesso!")
            
            st.download_button(
                label="📥 Baixar PDF Unificado",
                data=output_pdf,
                file_name="Comprovantes_Unificados.pdf",
                mime="application/pdf",
                key="download_merge"
            )
