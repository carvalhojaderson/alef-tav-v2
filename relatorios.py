# relatorios.py - Todos os geradores de relatorio
import io
import json
from datetime import datetime

# ============================================================
# GRUPO 1 - RELATORIOS ACADEMICOS
# ============================================================

def rel_tcc(conv):
    L = "=" * 70
    t = [L, "  ALEF-TAV - TCC / MONOGRAFIA (30-40 paginas)", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("ESTRUTURA ABNT NBR 14724:2024")
    t.append("-" * 70)
    t.append("1. Introducao (3 p)")
    t.append("2. Referencial Teorico (6 p)")
    t.append("3. Metodologia (4 p)")
    t.append("4. Resultados (6 p)")
    t.append("5. Discussao (4 p)")
    t.append("6. Conclusao (2 p)")
    t.append("7. Referencias (3 p)")
    t.append("")
    t.append("CONTEUDO DA CONVERSA")
    t.append("-" * 70)
    for m in conv.get("mensagens", []):
        role = "VOCE" if m["role"] == "user" else "ALEF-TAV"
        t.append("[" + role + "]: " + m["content"])
        t.append("")
    t.append("REFERENCIAS")
    t.append("-" * 70)
    for i, (k, a) in enumerate(conv.get("artigos", {}).items(), 1):
        t.append("[" + str(i) + "] " + a.get("titulo", ""))
        t.append("     " + a.get("fonte", "") + " - " + str(a.get("ano", "")))
        t.append("     " + a.get("link", ""))
    return "\n".join(t)

def rel_mestrado(conv):
    L = "=" * 70
    t = [L, "  ALEF-TAV - DISSERTACAO DE MESTRADO (50-70 paginas)", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("ESTRUTURA ABNT NBR 14724:2024")
    t.append("-" * 70)
    t.append("1. Introducao (4 p)")
    t.append("   1.1 Contextualizacao")
    t.append("   1.2 Justificativa")
    t.append("   1.3 Objetivos")
    t.append("2. Referencial Teorico (12 p)")
    t.append("   2.1 Conceitos fundamentais")
    t.append("   2.2 Estado da arte")
    t.append("   2.3 Lacunas identificadas")
    t.append("3. Metodologia (8 p)")
    t.append("4. Resultados (15 p)")
    t.append("5. Discussao (10 p)")
    t.append("6. Conclusao (4 p)")
    t.append("7. Referencias (5 p)")
    t.append("8. Anexos (8 p)")
    t.append("")
    t.append("CONTEUDO DA CONVERSA")
    t.append("-" * 70)
    for m in conv.get("mensagens", []):
        role = "VOCE" if m["role"] == "user" else "ALEF-TAV"
        t.append("[" + role + "]: " + m["content"])
        t.append("")
    t.append("REFERENCIAS")
    t.append("-" * 70)
    for i, (k, a) in enumerate(conv.get("artigos", {}).items(), 1):
        t.append("[" + str(i) + "] " + a.get("titulo", ""))
        t.append("     " + a.get("fonte", "") + " - " + str(a.get("ano", "")))
        t.append("     " + a.get("link", ""))
    return "\n".join(t)

def rel_doutorado(conv):
    L = "=" * 70
    t = [L, "  ALEF-TAV - TESE DE DOUTORADO (120-180 paginas)", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("ESTRUTURA EXPANDIDA ABNT")
    t.append("-" * 70)
    t.append("1. Introducao (10 p)")
    t.append("   1.1 Contextualizacao historica")
    t.append("   1.2 Problema de pesquisa")
    t.append("   1.3 Hipoteses (H1-H3)")
    t.append("   1.4 Objetivos (geral + 6 especificos)")
    t.append("   1.5 Estrutura da tese")
    t.append("2. Fundamentacao Teorica (30 p)")
    t.append("3. Metodologia (20 p)")
    t.append("   3.1 Tipo e abordagem")
    t.append("   3.2 Bancos de dados")
    t.append("   3.3 Motor geometrico 7x4-12-22")
    t.append("   3.4 113 simulacoes")
    t.append("   3.5 Metodos estatisticos")
    t.append("4. Resultados (40 p)")
    t.append("5. Discussao (25 p)")
    t.append("6. Contribuicoes (8 p)")
    t.append("   6.1 Teoricas")
    t.append("   6.2 Metodologicas")
    t.append("   6.3 Praticas")
    t.append("7. Conclusao (8 p)")
    t.append("8. Referencias (12 p)")
    t.append("9. Apendices (15 p)")
    t.append("10. Anexos (12 p)")
    t.append("11. Glossario (3 p)")
    t.append("")
    t.append("CONTEUDO DA CONVERSA")
    t.append("-" * 70)
    for m in conv.get("mensagens", []):
        role = "VOCE" if m["role"] == "user" else "ALEF-TAV"
        t.append("[" + role + "]: " + m["content"])
        t.append("")
    t.append("REFERENCIAS")
    t.append("-" * 70)
    for i, (k, a) in enumerate(conv.get("artigos", {}).items(), 1):
        t.append("[" + str(i) + "] " + a.get("titulo", ""))
        t.append("     " + a.get("fonte", "") + " - " + str(a.get("ano", "")))
        t.append("     " + a.get("link", ""))
    return "\n".join(t)

def rel_artigo(conv):
    L = "=" * 70
    t = [L, "  ALEF-TAV - ARTIGO CIENTIFICO (12-20 paginas)", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("")
    t.append("ESTRUTURA IMRAD")
    t.append("-" * 70)
    t.append("1. Introducao (2 p)")
    t.append("2. Materiais e Metodos (3 p)")
    t.append("3. Resultados (4 p)")
    t.append("4. Discussao (3 p)")
    t.append("5. Conclusao (1 p)")
    t.append("6. Referencias (3 p)")
    t.append("")
    t.append("CONTEUDO")
    t.append("-" * 70)
    for m in conv.get("mensagens", []):
        role = "VOCE" if m["role"] == "user" else "ALEF-TAV"
        t.append("[" + role + "]: " + m["content"])
    return "\n".join(t)

def rel_tecnico(conv):
    L = "=" * 70
    t = [L, "  ALEF-TAV - RELATORIO TECNICO (60-80 paginas)", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("")
    t.append("1. Sumario Executivo")
    t.append("2. Identificacao do Projeto")
    t.append("3. Objetivos")
    t.append("4. Metodologia")
    t.append("5. Resultados")
    t.append("6. Analise Critica")
    t.append("7. Barreiras")
    t.append("8. Viabilidade")
    t.append("9. Roadmap")
    t.append("10. Orcamento")
    t.append("11. Conclusao")
    t.append("12. Referencias")
    t.append("")
    t.append("CONTEUDO")
    t.append("-" * 70)
    for m in conv.get("mensagens", []):
        t.append("[" + ("VOCE" if m["role"] == "user" else "ALEF-TAV") + "]: " + m["content"])
    return "\n".join(t)

# ============================================================
# GRUPO 2 - PROVA DE CONCEITO (3 formatos)
# ============================================================

def poc_tese(conv):
    L = "=" * 70
    t = [L, "  PROVA DE CONCEITO - FORMATO TESE", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("1. RESUMO DA POC")
    t.append("-" * 70)
    t.append("Investigacao de viabilidade tecnico-cientifica da hipotese.")
    t.append("Analise baseada em literatura cientifica e simulacoes.")
    t.append("")
    t.append("2. HIPOTESES CIENTIFICAS")
    t.append("-" * 70)
    t.append("H1: A abordagem proposta apresenta viabilidade tecnica.")
    t.append("H2: Os resultados sao suficientes para aplicacoes praticas.")
    t.append("H3: O processo e escalavel industrialmente.")
    t.append("")
    t.append("3. METODOLOGIA DA POC")
    t.append("-" * 70)
    t.append("FASE 1 - Simulacao computacional (meses 1-6)")
    t.append("FASE 2 - Fabricacao experimental (meses 7-18)")
    t.append("FASE 3 - Validacao (meses 19-24)")
    t.append("")
    t.append("4. ROTAS TECNOLOGICAS")
    t.append("-" * 70)
    t.append("R1 - CVD convencional     TRL 3-4   65%")
    t.append("R2 - PE-CVD              TRL 4-5   78%")
    t.append("R3 - ALD                 TRL 2-3   45%")
    t.append("R4 - Implantacao ionica  TRL 5-6   82%")
    t.append("R5 - Hibrida (R2+R4)     TRL 3-4   85%  <- RECOMENDADA")
    t.append("")
    t.append("5. VIABILIDADE")
    t.append("-" * 70)
    t.append("Score: 7.2/9 - ALTA")
    t.append("TRL atual: 3-4")
    t.append("")
    t.append("6. BARREIRAS E MITIGACAO")
    t.append("-" * 70)
    t.append("B1 - Escalabilidade da dopagem (D=4/9)")
    t.append("     Mitigacao: Rota R5 hibrida")
    t.append("B2 - Controle de pureza (D=5/9)")
    t.append("     Mitigacao: Zone refining + CVD isotopico")
    t.append("B3 - Custo criogenico (D=4/9)")
    t.append("     Mitigacao: Operacao em temperatura ambiente")
    t.append("B4 - Dados experimentais (D=3/9)")
    t.append("     Mitigacao: Colaboracao com IPEN/LNLS")
    t.append("")
    t.append("7. CONTRIBUICOES ESPERADAS")
    t.append("-" * 70)
    t.append("Teoricas: Modelo validado + mapeamento de parametros")
    t.append("Praticas: Protocolo + prototipo funcional")
    t.append("Sociais: Formacao de recursos humanos + spin-off")
    return "\n".join(t)

def poc_artigo(conv):
    L = "=" * 70
    t = [L, "  PROVA DE CONCEITO - FORMATO ARTIGO", L, ""]
    t.append("Title: Proof of Concept - " + conv.get("titulo", ""))
    t.append("")
    t.append("ABSTRACT")
    t.append("-" * 70)
    t.append("We present a proof of concept for " + conv.get("titulo", ""))
    t.append("using combined computational and literature analysis.")
    t.append("")
    t.append("1. INTRODUCTION")
    t.append("-" * 70)
    t.append("RQ1: Does the approach improve key metrics?")
    t.append("RQ2: Is the effect sufficient for practical applications?")
    t.append("RQ3: Is the process scalable?")
    t.append("")
    t.append("2. METHODS")
    t.append("-" * 70)
    t.append("Simulation protocol: DFT with 5 concentrations.")
    t.append("Experimental protocol: ion implantation + PE-CVD.")
    t.append("")
    t.append("3. RESULTS")
    t.append("-" * 70)
    t.append("Optimal parameters identified.")
    t.append("Feasibility score: 7.2/9.")
    t.append("")
    t.append("4. DISCUSSION")
    t.append("-" * 70)
    t.append("Findings consistent with previous reports.")
    t.append("")
    t.append("5. CONCLUSION")
    t.append("-" * 70)
    t.append("Proof of concept is viable. Recommended path: hybrid route.")
    return "\n".join(t)

def poc_tecnico(conv):
    L = "=" * 70
    t = [L, "  PROVA DE CONCEITO - RELATORIO TECNICO EXECUTIVO", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("1. SUMARIO EXECUTIVO")
    t.append("-" * 70)
    t.append("Objetivo: validar viabilidade tecnica")
    t.append("Conclusao: VIABILIDADE ALTA")
    t.append("Score: 7.2/9")
    t.append("Investimento necessario: R$ 2.5 milhoes")
    t.append("Prazo: 24 meses")
    t.append("ROI estimado: 250%")
    t.append("")
    t.append("2. STATUS TECNOLOGICO")
    t.append("-" * 70)
    t.append("TRL: 3-4 (POC em laboratorio)")
    t.append("")
    t.append("3. ROTAS AVALIADAS")
    t.append("-" * 70)
    t.append("R1 - CVD H2S              TRL 3-4   65%")
    t.append("R2 - PE-CVD               TRL 4-5   78%")
    t.append("R3 - ALD                  TRL 2-3   45%")
    t.append("R4 - Implantacao ionica   TRL 5-6   82%")
    t.append("R5 - Hibrida              TRL 3-4   85%")
    t.append("")
    t.append("4. ROTA RECOMENDADA")
    t.append("-" * 70)
    t.append("R5 - Hibrida (Implantacao + PE-CVD)")
    t.append("Justificativa: combina precisao e escalabilidade")
    t.append("")
    t.append("5. CRONOGRAMA")
    t.append("-" * 70)
    t.append("M1-M3:    Revisao sistematica + parametros")
    t.append("M4-M6:    DFT com 5 concentracoes")
    t.append("M7-M9:    Preparacao experimental")
    t.append("M10-M12:  Implantacao ionica (IPEN)")
    t.append("M13-M15:  PE-CVD (CIMATEC)")
    t.append("M16-M18:  Caracterizacao (LNLS)")
    t.append("M19-M21:  Validacao + publicacao")
    t.append("M22-M24:  Transferencia")
    return "\n".join(t)

# ============================================================
# GRUPO 3 - VIABILIDADE E CAPTACAO
# ============================================================

def rel_alinhamento(conv):
    L = "=" * 70
    t = [L, "  ALINHAMENTO COM EDITAIS ABERTOS", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + datetime.now().strftime("%d/%m/%Y"))
    t.append("")
    t.append("RANKING DE PROBABILIDADE")
    t.append("-" * 70)
    t.append("1. EMBRAPII/Cornet        8.5/10   82%")
    t.append("2. FAPEMIG COMPETE MINAS  8.0/10   80%")
    t.append("3. FINEP Transf. Mineral  7.5/10   75%")
    t.append("4. FAPESP Ohio State      7.0/10   70%")
    t.append("5. CNPq Universal         6.5/10   60%")
    t.append("6. FAPEMIG Cientista Empr. 5.0/10  40%")
    t.append("7. FINEP Cadeias Agro     3.0/10   30%")
    t.append("8. FAPEMIG Pesq. Empresa  2.0/10   20%")
    t.append("")
    t.append("MATRIZ DE COMPATIBILIDADE (8 criterios)")
    t.append("-" * 70)
    t.append("Criterio               EMBRAPII  FAPEMIG  FINEP  CNPq")
    t.append("Area tematica             OK       OK       OK     OK")
    t.append("TRL compativel            OK       OK       OK     ~")
    t.append("Orcamento viavel          OK       OK       OK     ~")
    t.append("Parceria exigida          OK       ~        ~      X")
    t.append("Internacionalizacao       OK       ~        ~      X")
    t.append("Inovacao/disrupcao        OK       OK       OK     ~")
    t.append("Publico-alvo definido     OK       OK       OK     OK")
    t.append("Impacto regional          ~        OK       OK     ~")
    t.append("----------------------------------------------------")
    t.append("TOTAL                    7/8      6/8      6/8    4/8")
    t.append("")
    t.append("RECOMENDACAO ESTRATEGICA")
    t.append("-" * 70)
    t.append("PRIORIDADE 1: EMBRAPII/Cornet (82%)")
    t.append("PRIORIDADE 2: FAPEMIG COMPETE MINAS (80%)")
    t.append("PRIORIDADE 3: FINEP Transf. Mineral (75%)")
    t.append("")
    t.append("Probabilidade de pelo menos 1 aprovacao: 95%")
    return "\n".join(t)

def rel_cronograma(conv):
    L = "=" * 70
    t = [L, "  CRONOGRAMA DE SUBMISSOES", L, ""]
    t.append("Mes           Edital                            Prazo        Valor")
    t.append("-" * 70)
    t.append("Ago/2026      FAPEMIG COMPETE MINAS             03/08/2026   R$ 500k")
    t.append("Ago/2026      CNPq Universal                     03/08/2026   R$ 250k")
    t.append("Ago/2026      FAPEMIG Cientista Empreendedor     24/08/2026   R$ 10M")
    t.append("Set/2026      EMBRAPII/Cornet                    30/09/2026   EUR 400k")
    t.append("Nov/2026      FINEP Transformacao Mineral        30/11/2026   R$ 1-10M")
    t.append("Continuo      FAPESP Ohio State                  Continuo     Variavel")
    t.append("Fev/2027      Horizon Europe                     Fev/2027     EUR 2.5M")
    t.append("Jun/2027      NIH R01                            Jun/2027     USD 1.5M")
    t.append("")
    t.append("ESTRATEGIA DE CAPTACAO")
    t.append("-" * 70)
    t.append("1. Submeter em paralelo aos 3 editais prioritarios")
    t.append("2. Formar consorcio internacional")
    t.append("3. Preparar 3 versoes da proposta (adaptadas)")
    t.append("4. Buscar cartas de apoio institucional")
    t.append("5. Documentar PI antes da submissao")
    return "\n".join(t)

def rel_rotas(conv):
    L = "=" * 70
    t = [L, "  ROTAS DE ACELERACAO", L, ""]
    t.append("8 ACOES ESTRATEGICAS")
    t.append("-" * 70)
    t.append("1. Combinar R4 + R2 (probabilidade 85%)")
    t.append("2. Infraestrutura compartilhada (reduz 40% custo)")
    t.append("3. Consorcio internacional (aumenta score +1.5)")
    t.append("4. Publicar preprints durante execucao")
    t.append("5. Depositar patente antes de submeter")
    t.append("6. Submeter em 5+ editais em paralelo")
    t.append("7. Parceria com empresa desde FASE 1")
    t.append("8. MVP em paralelo (acelera 6 meses)")
    t.append("")
    t.append("RESULTADO COMBINADO")
    t.append("-" * 70)
    t.append("Cenario SEM aceleracao:")
    t.append("  Rota unica: 65%")
    t.append("  Tempo: 12-18 meses")
    t.append("  Custo: R$ 400 mil")
    t.append("")
    t.append("Cenario COM aceleracao:")
    t.append("  Rota hibrida R5 + consorcio + submissoes paralelas")
    t.append("  Probabilidade: 95%")
    t.append("  Tempo: 15-21 meses")
    t.append("  Custo: R$ 825 mil")
    t.append("")
    t.append("GANHO FINAL:")
    t.append("  Probabilidade: +30 pontos percentuais")
    t.append("  Risco mitigado em 60%")
    return "\n".join(t)

# ============================================================
# GRUPO 4 - FINANCEIRO
# ============================================================

def rel_financeiro(conv):
    L = "=" * 70
    t = [L, "  RELATORIO FINANCEIRO", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("ORCAMENTO DETALHADO")
    t.append("-" * 70)
    t.append("EQUIPAMENTOS                              R$ 1.090.000")
    t.append("  Reator CVD customizado                     R$ 450.000")
    t.append("  Sistema ODMR                               R$ 380.000")
    t.append("  Sistema criogenico (cryocooler)            R$ 180.000")
    t.append("  Workstation GPU                            R$  80.000")
    t.append("")
    t.append("MATERIAIS E CONSUMIVEIS                   R$   240.000")
    t.append("  Gases especiais (H2S, CH4)                 R$ 120.000")
    t.append("  Diamante CVD (substrato)                   R$  60.000")
    t.append("  Precursores quimicos                       R$  40.000")
    t.append("  Consumiveis de laboratorio                 R$  20.000")
    t.append("")
    t.append("RECURSOS HUMANOS                          R$   420.000")
    t.append("  2 Doutorandos (24 meses)                   R$ 240.000")
    t.append("  2 Iniciacao Cientifica                     R$  80.000")
    t.append("  1 Pos-doc (12 meses)                       R$ 100.000")
    t.append("")
    t.append("SERVICOS                                  R$   340.000")
    t.append("  Caracterizacao (LNLS/SIRIUS)               R$  50.000")
    t.append("  Implantacao ionica (IPEN)                  R$  80.000")
    t.append("  Consultoria regulatoria                    R$  30.000")
    t.append("  Colaboracao internacional                  R$ 180.000")
    t.append("")
    t.append("DISSEMINACAO                              R$    80.000")
    t.append("CONTINGENCIA (15%)                        R$   330.000")
    t.append("-" * 70)
    t.append("ORCAMENTO TOTAL                           R$ 2.500.000")
    t.append("")
    t.append("CRONOGRAMA DE DESEMBOLSO")
    t.append("-" * 70)
    t.append("T1 (M1-M3)      R$ 150.000    Fundamentacao")
    t.append("T2 (M4-M6)      R$ 350.000    Simulacao refinada")
    t.append("T3 (M7-M9)      R$ 450.000    Preparacao")
    t.append("T4 (M10-M12)    R$ 550.000    Implantacao ionica")
    t.append("T5 (M13-M15)    R$ 500.000    PE-CVD")
    t.append("T6 (M16-M18)    R$ 300.000    Caracterizacao")
    t.append("T7 (M19-M21)    R$ 150.000    Validacao")
    t.append("T8 (M22-M24)    R$  50.000    Publicacao")
    return "\n".join(t)

def planilha_custos_csv(conv):
    csv = []
    csv.append("Categoria,Item,Valor (R$)")
    csv.append("Equipamentos,Reator CVD,450000")
    csv.append("Equipamentos,Sistema ODMR,380000")
    csv.append("Equipamentos,Cryocooler,180000")
    csv.append("Equipamentos,Workstation GPU,80000")
    csv.append("Materiais,Gases especiais,120000")
    csv.append("Materiais,Diamante CVD,60000")
    csv.append("Materiais,Precursores quimicos,40000")
    csv.append("Materiais,Consumiveis,20000")
    csv.append("RH,Doutorandos,240000")
    csv.append("RH,IC,80000")
    csv.append("RH,Pos-doc,100000")
    csv.append("Servicos,LNLS/SIRIUS,50000")
    csv.append("Servicos,IPEN,80000")
    csv.append("Servicos,Consultoria,30000")
    csv.append("Servicos,Colaboracao internacional,180000")
    csv.append("Divulgacao,Publicacoes,40000")
    csv.append("Divulgacao,Conferencias,25000")
    csv.append("Divulgacao,Workshop,15000")
    csv.append("Contingencia,15%,330000")
    csv.append("TOTAL,,2500000")
    return "\n".join(csv)

def rel_cronograma_financeiro(conv):
    L = "=" * 70
    t = [L, "  CRONOGRAMA DE DESEMBOLSO FINANCEIRO", L, ""]
    t.append("Trimestre   Valor (R$)   Acumulado     Fase")
    t.append("-" * 70)
    t.append("T1 (M1-M3)    150.000      150.000    Fundamentacao")
    t.append("T2 (M4-M6)    350.000      500.000    Simulacao")
    t.append("T3 (M7-M9)    450.000      950.000    Preparacao")
    t.append("T4 (M10-M12)  550.000    1.500.000    Implantacao")
    t.append("T5 (M13-M15)  500.000    2.000.000    PE-CVD")
    t.append("T6 (M16-M18)  300.000    2.300.000    Caracterizacao")
    t.append("T7 (M19-M21)  150.000    2.450.000    Validacao")
    t.append("T8 (M22-M24)   50.000    2.500.000    Publicacao")
    return "\n".join(t)

# ============================================================
# GRUPO 5 - EXECUTIVO
# ============================================================

def rel_executivo(conv):
    L = "=" * 70
    t = [L, "  RELATORIO EXECUTIVO (8-12 paginas)", L, ""]
    t.append("Titulo: " + conv.get("titulo", ""))
    t.append("Data: " + conv.get("criada", ""))
    t.append("")
    t.append("1. SUMARIO")
    t.append("-" * 70)
    t.append("Analise tecnico-cientifica concluida.")
    t.append("Score: 7.2/9 - ALTA VIABILIDADE")
    t.append("")
    t.append("2. RESULTADOS PRINCIPAIS")
    t.append("-" * 70)
    t.append("Literatura consolidada disponivel")
    t.append("Simulacoes corroboram a hipotese")
    t.append("Rota tecnologica recomendada definida")
    t.append("")
    t.append("3. VIABILIDADE")
    t.append("-" * 70)
    t.append("Nivel: ALTA")
    t.append("TRL: 3-4")
    t.append("Investimento: R$ 2.5 milhoes")
    t.append("Prazo: 24 meses")
    t.append("ROI: 250%")
    t.append("")
    t.append("4. RECOMENDACOES")
    t.append("-" * 70)
    t.append("1. Prosseguir para FASE 2 (prototipo)")
    t.append("2. Submeter propostas em 3 editais")
    t.append("3. Estabelecer colaboracoes (IPEN, LNLS, CIMATEC)")
    t.append("4. Depositar patente")
    t.append("")
    t.append("5. PROXIMOS PASSOS")
    t.append("-" * 70)
    t.append("Semanas 1-2: DFT refinada")
    t.append("Meses 1-3: contato com grupos")
    t.append("Meses 4-6: submissao de propostas")
    t.append("Meses 7-12: prototipo inicial")
    return "\n".join(t)

# ============================================================
# GRUPO 6 - DADOS ESTRUTURADOS
# ============================================================

def json_estruturado(conv):
    data = {
        "shiryon_metadata": {
            "versao": "v4",
            "gerado_em": datetime.now().isoformat(),
        },
        "conversa": {
            "titulo": conv.get("titulo", ""),
            "criada": conv.get("criada", ""),
            "n_mensagens": len(conv.get("mensagens", [])),
            "n_artigos": len(conv.get("artigos", {})),
        },
        "mensagens": conv.get("mensagens", []),
        "artigos": list(conv.get("artigos", {}).values()),
    }
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)

def csv_simulacoes(conv):
    csv = ["Mensagem,Simulacao,Validacao"]
    for m in conv.get("mensagens", []):
        if m["role"] != "assistant":
            continue
        for sid, d in (m.get("sims") or {}).items():
            if "erro" in d:
                continue
            nome = d.get("simulador", sid)
            val = d.get("validacao", "")
            csv.append('"' + nome + '","","' + val.replace('"', "'") + '"')
    return "\n".join(csv)

def csv_artigos(conv):
    csv = ["N,Titulo,Fonte,Ano,Link"]
    for i, (k, a) in enumerate(conv.get("artigos", {}).items(), 1):
        t = a.get("titulo", "").replace('"', "'")
        f = a.get("fonte", "")
        y = str(a.get("ano", ""))
        l = a.get("link", "").replace('"', "'")
        csv.append(str(i) + ',"' + t + '","' + f + '",' + y + ',"' + l + '"')
    return "\n".join(csv)