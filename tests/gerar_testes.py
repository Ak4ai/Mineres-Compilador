from pathlib import Path

BASE_DIR = Path("entradas")

CASOS_VALIDOS = BASE_DIR / "casos_validos"
ERROS_SINTATICOS = BASE_DIR / "erros_sintaticos"

def criar_arquivo(pasta: Path, nome: str, conteudo: str):
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome
    caminho.write_text(conteudo.strip() + "\n", encoding="utf-8")


def gerar_testes():
    # =========================
    # CASOS VÁLIDOS
    # =========================

    criar_arquivo(CASOS_VALIDOS, "valido_bloco_vazio.txt", """
bora_cumpade main()
simbora
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_multiplas_variaveis.txt", """
bora_cumpade main()
simbora
    trem_di_numeru a, b, c uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_expressao_complexa.txt", """
bora_cumpade main()
simbora
    trem_di_numeru x uai
    x fica_assim_entao 1 + 2 veiz 3 uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_if_else.txt", """
bora_cumpade main()
simbora
    uai_se(eh)
        para_o_trem uai
    uai_senao
        toca_o_trem uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_while.txt", """
bora_cumpade main()
simbora
    enquanto_tiver_trem(eh)
        para_o_trem uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_for_completo.txt", """
bora_cumpade main()
simbora
    roda_esse_trem(x fica_assim_entao 0; x < 10; x fica_assim_entao x + 1)
        para_o_trem uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_for_vazio.txt", """
bora_cumpade main()
simbora
    roda_esse_trem(; ; )
        para_o_trem uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_case.txt", """
bora_cumpade main()
simbora
    dependenu(x) simbora
        du_casu 1: para_o_trem uai
        du_casu 2: toca_o_trem uai
        uai_so: para_o_trem uai
    cabo
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_io_multiplo.txt", """
bora_cumpade main()
simbora
    oia_proce_ve("a", "b", "c") uai
cabo
""")

    criar_arquivo(CASOS_VALIDOS, "valido_blocos_aninhados.txt", """
bora_cumpade main()
simbora
    simbora
        simbora
            para_o_trem uai
        cabo
    cabo
cabo
""")

    # =========================
    # ERROS SINTÁTICOS
    # =========================

    criar_arquivo(ERROS_SINTATICOS, "erro_sem_simbora.txt", """
bora_cumpade main()
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_virgula_sem_identificador.txt", """
bora_cumpade main()
simbora
    trem_di_numeru a, uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_operador_sem_operando.txt", """
bora_cumpade main()
simbora
    x fica_assim_entao 1 + uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_if_sem_parenteses.txt", """
bora_cumpade main()
simbora
    uai_se eh para_o_trem uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_while_sem_condicao.txt", """
bora_cumpade main()
simbora
    enquanto_tiver_trem()
        para_o_trem uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_for_sem_ponto_virgula.txt", """
bora_cumpade main()
simbora
    roda_esse_trem(x fica_assim_entao 0 x < 10; )
        para_o_trem uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_case_sem_casos.txt", """
bora_cumpade main()
simbora
    dependenu(x) simbora
    cabo
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_dois_default.txt", """
bora_cumpade main()
simbora
    dependenu(x) simbora
        uai_so: para_o_trem uai
        uai_so: toca_o_trem uai
    cabo
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_io_virgula_final.txt", """
bora_cumpade main()
simbora
    oia_proce_ve("a", ) uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_bloco_fechamento.txt", """
bora_cumpade main()
simbora
    simbora
        para_o_trem uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_ta_bao.txt", """
bora_cumpade main()
simbora
    ta_bao uai
cabo
""")

    criar_arquivo(ERROS_SINTATICOS, "erro_lixo_apos_programa.txt", """
bora_cumpade main()
simbora
    uai
cabo

lixo
""")

    print("✅ Todos os testes foram gerados com sucesso!")


if __name__ == "__main__":
    gerar_testes()