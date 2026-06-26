import streamlit as st
from pypdf import PdfReader
import pandas as pd

# Configuração da página do Streamlit
st.set_page_config(page_title="Varredura de PDFs", page_icon="📄", layout="wide")

st.title("📄 Sistema de Varredura de Arquivos PDF")
st.markdown("""
Este aplicativo realiza uma busca automatizada por nomes ou termos específicos dentro de arquivos PDF editáveis.
1. Faça o upload de um ou mais arquivos.
2. Insira os nomes separados por vírgula.
3. Clique em 'Iniciar Varredura'.
""")

# Área de Upload de Arquivos
uploaded_files = st.file_uploader("Carregue seus arquivos PDF", type=["pdf"], accept_multiple_files=True)

# Campo para inserir os nomes de busca
nomes_busca = st.text_input("Nomes para buscar (separe por vírgula):", placeholder="Ex: João Silva, Maria Souza, Lucas Rodrigues")

if uploaded_files and nomes_busca:
    # Limpa e organiza a lista de nomes digitados pelo usuário
    lista_nomes = [nome.strip() for nome in nomes_busca.split(",") if nome.strip()]
    
    if st.button("Iniciar Varredura", type="primary"):
        resultados = []
        termos_encontrados_set = set()
        
        # Barra de progresso visual
        progresso = st.progress(0)
        total_arquivos = len(uploaded_files)
        
        with st.spinner("Analisando documentos..."):
            for idx, uploaded_file in enumerate(uploaded_files):
                # Inicializa o leitor do PDF
                reader = PdfReader(uploaded_file)
                total_paginas = len(reader.pages)
                
                for num_pagina in range(total_paginas):
                    pagina = reader.pages[num_pagina]
                    texto = pagina.extract_text()
                    
                    if texto:
                        for nome in lista_nomes:
                            # Busca insensível a maiúsculas/minúsculas (case-insensitive)
                            if nome.lower() in texto.lower():
                                resultados.append({
                                    "Arquivo": uploaded_file.name,
                                    "Página": num_pagina + 1,
                                    "Nome Encontrado": nome
                                })
                                termos_encontrados_set.add(nome)
                
                # Atualiza a barra de progresso
                progresso.progress((idx + 1) / total_arquivos)
        
        # Exibição dos Resultados
        st.subheader("📊 Resultado da Análise")
        
        if resultados:
            st.success(f"Varredura concluída com sucesso! Encontradas {len(resultados)} ocorrências.")
            
            # Mostra quais termos foram localizados e quais faltaram
            st.markdown("**Resumo dos termos:**")
            for nome in lista_nomes:
                if nome in termos_encontrados_set:
                    st.write(f"✅ **{nome}**: Encontrado")
                else:
                    st.write(f"❌ **{nome}**: Não encontrado")
            
            # Tabela detalhada dos resultados
            df_resultados = pd.DataFrame(resultados)
            st.dataframe(df_resultados, use_container_width=True)
            
            # Permitir download dos resultados em formato CSV
            csv = df_resultados.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Baixar Relatório em CSV",
                data=csv,
                file_name="relatorio_varredura_pdf.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhum dos nomes informados foi localizado nos arquivos enviados.")
            
            st.markdown("**Resumo dos termos:**")
            for nome in lista_nomes:
                st.write(f"❌ **{nome}**: Não encontrado")
elif uploaded_files or nomes_busca:
    st.info("Por favor, certifique-se de carregar pelo menos um arquivo PDF e preencher a lista de nomes para iniciar.")
