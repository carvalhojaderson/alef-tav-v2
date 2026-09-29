# ============================================================
#   ALEF-TAV v16 - Assistente Cientifico
# ============================================================
#   Chat + 92 bases + 7 camadas de IA + Relatorios
# ============================================================

import streamlit as st
import re, uuid
from datetime import datetime

try:
    from bases_v5 import buscar_multibase, contar_bases
    BASES_OK = True
except:
    BASES_OK = False

try:
    from relatorios_v5 import (tcc_doc, mestrado_doc, doutorado_doc,
        artigo_doc, tecnico_doc, poc_doc, financeiro_doc, captacao_doc,
        executivo_doc, rotas_doc, cronograma_doc)
    RELS_OK = True
except Exception as e:
    RELS_OK = False
    RELS_ERRO = str(e)

try:
    import ia_orquestrador
    import ia_conversa
    IA_OK = True
except Exception as e:
    IA_OK = False
    IA_ERRO = str(e)

st.set_page_config(page_title="ALEF-TAV", page_icon="*", layout="wide")

try:
    import universal as u
    SIMS_OK = True
except:
    SIMS_OK = False
    u = None

# ============================================================
# TRADUCAO
# ============================================================
TRAD = {
    "diamante": "diamond",
    "grafeno": "graphene",
    "silicio": "silicon",
    "energia": "energy",
    "quantico": "quantum",
    "celula": "cell",
    "cancer": "cancer",
    "proteina": "protein",
}
STOP = set([
    "de", "da", "do", "das", "dos", "a", "o", "as", "os", "e",
    "em", "no", "na", "nos", "nas", "para", "por", "com",
    "um", "uma", "que", "como", "sobre",
])

def traduzir(t):
    palavras = re.findall(r'\w+', t.lower())
    return " ".join(TRAD.get(p, p) for p in palavras if p not in STOP)

# ============================================================
# FILTRO DE ARTIGOS
# ============================================================
def score_art(a, pergunta):
    txt = (a.get("titulo", "") + " " + a.get("resumo", "")).lower()
    ta = set(re.findall(r'\w{3,}', txt)) - STOP
    tp = set(re.findall(r'\w{3,}', pergunta.lower())) - STOP
    p1 = min(len(ta & tp) / max(len(tp), 1) * 2.5, 1.0)
    try:
        ano = int(a.get("ano", 2024))
    except:
        ano = 2024
    p3 = max(0, 1 - (2026 - ano) / 25)
    return (p1 * 3.0 + p3 * 1.0) / 4.0

def filtrar(arts, pergunta):
    if not arts:
        return []
    sc = [(a, score_art(a, pergunta)) for a in arts]
    sc.sort(key=lambda x: -x[1])
    return [a for a, _ in sc[:max(3, int(len(sc) * 0.2))]]

# ============================================================
# SIMULACOES
# ============================================================
def rodar_sims(pergunta, arts):
    if not SIMS_OK:
        return {}
    ss = set(u.SIMULADORES.keys())
    txt = " ".join(
        a.get("titulo", "") + " " + a.get("resumo", "")
        for a in arts
    ).lower()
    prefs = []
    if any(k in txt for k in ["theor", "quant", "relat"]):
        prefs += [s for s in ss if "quant" in s or "relat" in s]
    if any(k in txt for k in ["experiment", "measur"]):
        prefs += [s for s in ss if "estat" in s or "cinet" in s]
    if not prefs:
        prefs = list(ss)[:5]
    ids = list(set(prefs))[:5]
    res = {}
    for sid in ids:
        if sid in u.SIMULADORES:
            try:
                res[sid] = u.SIMULADORES[sid](pergunta, {})
            except:
                pass
    return res

# ============================================================
# ESTADO
# ============================================================
if "conversas" not in st.session_state:
    cid = str(uuid.uuid4())[:8]
    ctx_inicial = ia_conversa.novo_contexto() if IA_OK else {}
    st.session_state.conversas = {
        cid: {
            "id": cid,
            "titulo": "Nova conversa",
            "criada": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "mensagens": [],
            "artigos": {},
            "dados_bases": {},
            "contexto": ctx_inicial,
        }
    }
    st.session_state.conv_ativa = cid

def cc():
    return st.session_state.conversas[st.session_state.conv_ativa]

def nova():
    cid = str(uuid.uuid4())[:8]
    ctx_inicial = ia_conversa.novo_contexto() if IA_OK else {}
    st.session_state.conversas[cid] = {
        "id": cid,
        "titulo": "Nova conversa",
        "criada": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "mensagens": [],
        "artigos": {},
        "dados_bases": {},
        "contexto": ctx_inicial,
    }
    st.session_state.conv_ativa = cid

def historico_txt(conv):
    out = []
    for m in conv.get("mensagens", [])[-8:]:
        role = "User" if m["role"] == "user" else "ALEF"
        out.append(role + ": " + m["content"][:200])
    return "\n".join(out)

# ============================================================
# FUNCOES AUXILIARES
# ============================================================
def buscar_e_atualizar(conv, query, tema_original):
    with st.spinner("Buscando '" + query + "' em 92 bases..."):
        query_en = traduzir(query)
        if BASES_OK:
            try:
                dados = buscar_multibase(query_en, tema_original)
            except:
                dados = {}
        else:
            dados = {}

        if "dados_bases" not in conv:
            conv["dados_bases"] = {}
        for k, v in dados.items():
            if isinstance(v, list):
                conv["dados_bases"].setdefault(k, [])
                links_existentes = {a.get("link") for a in conv["dados_bases"][k]}
                for item in v:
                    if item.get("link") not in links_existentes:
                        conv["dados_bases"][k].append(item)
                        links_existentes.add(item.get("link"))

        for a in dados.get("literatura", []):
            k = a.get("link") or a.get("titulo", "")[:80]
            if k and k not in conv["artigos"]:
                conv["artigos"][k] = a

        todos_arts = list(conv["artigos"].values())
        filt = filtrar(todos_arts, tema_original) if todos_arts else []
        sims = rodar_sims(tema_original, filt)

    try:
        contagem = contar_bases(conv["dados_bases"])
    except:
        contagem = {}

    return filt, sims, contagem

def montar_resumo_categorias(conv, contagem):
    if not contagem:
        return []
    ICONES = {
        "literatura": "Literatura",
        "cientifica": "Ciencia",
        "patentes": "Patentes",
        "clinicos": "Clinicos",
        "quimica": "Quimica",
        "materiais": "Materiais",
        "genomica": "Genomica",
        "proteina": "Proteinas",
        "dados": "Datasets",
        "gov_br": "Gov BR",
        "gov_intl": "Gov INTL",
        "recalls": "Recalls",
        "normas": "Normas",
        "colaboracao": "Pesquisadores",
        "referencia": "Referencia",
        "livros": "Livros",
        "desafios": "Desafios",
        "terra": "Terra",
        "web": "Web",
        "financiamento": "Financiamento",
    }
    r = []
    total = sum(v for v in contagem.values() if v > 0)
    cats_ativas = len([v for v in contagem.values() if v > 0])
    r.append("**" + str(total) + " resultados em " + str(cats_ativas) + " categorias**")
    r.append("")
    ordenado = sorted(
        [(k, v) for k, v in contagem.items() if v > 0],
        key=lambda x: -x[1],
    )
    for cat, qtd in ordenado:
        icone = ICONES.get(cat, cat.title())
        r.append("- **" + icone + "**: " + str(qtd) + " resultados")
    r.append("")
    return r

def listar_top_por_categoria(conv, lim_por_cat=2):
    r = []
    for cat, lista in conv.get("dados_bases", {}).items():
        if not lista:
            continue
        r.append("**" + cat.title() + "** (" + str(len(lista)) + " resultados):")
        for item in lista[:lim_por_cat]:
            titulo = item.get("titulo", "")[:100]
            link = item.get("link", "")
            fonte = item.get("fonte", "")
            if link:
                r.append("  - [" + titulo + "](" + link + ") *(" + fonte + ")*")
            else:
                r.append("  - " + titulo + " *(" + fonte + ")*")
        if len(lista) > lim_por_cat:
            r.append("  - _+" + str(len(lista) - lim_por_cat) + " mais..._")
        r.append("")
    return r

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ALEF-TAV")
    st.caption("Assistente Cientifico v16")

    if st.button("+ Nova conversa", use_container_width=True, type="primary"):
        nova()
        st.rerun()

    st.markdown("---")
    st.markdown("**Conversas**")
    for cid, c in list(st.session_state.conversas.items()):
        p = "> " if cid == st.session_state.conv_ativa else "  "
        if st.button(p + c["titulo"][:25], key="c_" + cid, use_container_width=True):
            st.session_state.conv_ativa = cid
            st.rerun()

    st.markdown("---")
    st.caption("Bases: " + ("OK" if BASES_OK else "X"))
    st.caption("Relatorios: " + ("OK" if RELS_OK else "X"))
    st.caption("IA: " + ("OK" if IA_OK else "X"))

    if IA_OK:
        try:
            disp = ia_orquestrador.disponiveis()
            if disp:
                st.markdown("---")
                st.markdown("**IA ativa**")
                for p in disp:
                    st.caption("- " + p)
        except:
            pass

    conv = cc()
    ctx = conv.get("contexto", {})
    if ctx.get("tema"):
        st.markdown("---")
        st.markdown("**Contexto**")
        if ctx.get("tema"):
            st.caption("Tema: " + ctx["tema"])
        if ctx.get("area"):
            st.caption("Area: " + ctx["area"])
        if ctx.get("foco"):
            st.caption("Foco: " + ctx["foco"])
        if ctx.get("aplicacao"):
            st.caption("Aplicacao: " + ctx["aplicacao"])
        st.caption("Turnos: " + str(ctx.get("turnos", 0)))
        if ctx.get("pronto_para_relatorio"):
            st.success("Pronto para relatorio")

    if conv.get("artigos"):
        st.caption("Artigos: " + str(len(conv["artigos"])))

# ============================================================
# MAIN
# ============================================================
conv = cc()

if not conv["mensagens"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align:center;color:#8b5cf6;'>*</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align:center;font-weight:400;'>ALEF-TAV</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;color:#8e8e8e;'>Como posso ajudar hoje?</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#8e8e8e;font-size:0.85em;'>"
        "Converso, busco em 92 bases e gero relatorios com 7 camadas de IA.<br>"
        "<b>Exemplos:</b> graphene oxide | diamond NV centers | CRISPR"
        "</p>",
        unsafe_allow_html=True,
    )

for msg in conv["mensagens"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sims") and msg["role"] == "assistant":
            with st.expander("Simulacoes"):
                for sid, d in list(msg["sims"].items())[:5]:
                    if "erro" in d:
                        continue
                    st.caption("- " + d.get("simulador", sid))

# ============================================================
# INPUT
# ============================================================
pergunta = st.chat_input("Digite qualquer coisa...")

if pergunta:
    conv["mensagens"].append({"role": "user", "content": pergunta})
    if conv["titulo"] == "Nova conversa":
        conv["titulo"] = pergunta[:50]

    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        historico = historico_txt(conv)
        ctx = conv.get("contexto", {})

        if IA_OK:
            with st.spinner("Analisando..."):
                intencao = ia_conversa.detectar_intencao(pergunta, historico, ctx)
        else:
            intencao = "PESQUISA"

        if IA_OK:
            with st.spinner("Atualizando contexto..."):
                ctx = ia_conversa.extrair_contexto(pergunta, ctx)
                conv["contexto"] = ctx

        st.caption("Intencao: **" + intencao + "** | turno " + str(ctx.get("turnos", 0)))

        # ====================================================
        # RELATORIO
        # ====================================================
        if intencao == "RELATORIO":
            if IA_OK:
                tipo = ia_conversa.detectar_tipo_relatorio(pergunta)
            else:
                tipo = None
                t = pergunta.lower()
                for k in ["tcc", "mestrado", "doutorado", "artigo",
                          "tecnico", "poc", "financeiro", "captacao", "rotas"]:
                    if k in t:
                        tipo = k
                        break

            if not conv.get("artigos"):
                resposta = (
                    "Sem artigos no contexto. Me conte o tema primeiro.\n\n"
                    "**Exemplos:** `graphene oxide`, `diamond NV`"
                )
                st.markdown(resposta)
                conv["mensagens"].append({
                    "role": "assistant",
                    "content": resposta,
                    "sims": {},
                })
            elif not tipo:
                resposta = (
                    "Nao entendi o tipo. Opcoes:\n"
                    "- `gera um tcc`\n"
                    "- `quero um artigo`\n"
                    "- `faz uma poc`"
                )
                st.markdown(resposta)
                conv["mensagens"].append({
                    "role": "assistant",
                    "content": resposta,
                    "sims": {},
                })
            else:
                if ctx.get("tema"):
                    tema_final = ia_conversa.refinar_tema(ctx)
                else:
                    tema_final = conv["titulo"]
                conv["titulo"] = tema_final[:50]

                st.markdown("**Gerando " + tipo.upper() + "...**")
                st.caption("Tema: " + tema_final + " | Artigos: " + str(len(conv["artigos"])))

                with st.spinner("Sintetizando com IA (1-2 min)..."):
                    mapa = {
                        "tcc": (tcc_doc, "tcc.doc"),
                        "mestrado": (mestrado_doc, "mestrado.doc"),
                        "doutorado": (doutorado_doc, "doutorado.doc"),
                        "artigo": (artigo_doc, "artigo.doc"),
                        "tecnico": (tecnico_doc, "tecnico.doc"),
                        "poc": (poc_doc, "poc.doc"),
                        "financeiro": (financeiro_doc, "financeiro.doc"),
                        "captacao": (captacao_doc, "captacao.doc"),
                        "rotas": (rotas_doc, "rotas.doc"),
                    }
                    try:
                        fn, nome = mapa[tipo]
                        conteudo = fn(conv)
                        st.success(tipo.upper() + " pronto!")
                        st.download_button(
                            "Baixar " + nome,
                            conteudo,
                            file_name=nome,
                            mime="application/msword",
                            use_container_width=True,
                        )
                        resposta = "Relatorio **" + tipo.upper() + "** gerado."
                    except Exception as e:
                        st.error("Erro: " + str(e))
                        resposta = "Erro: " + str(e)

                st.markdown(resposta)
                conv["mensagens"].append({
                    "role": "assistant",
                    "content": resposta,
                    "sims": {},
                })

        # ====================================================
        # CONVERSA
        # ====================================================
        elif intencao == "CONVERSA":
            if IA_OK:
                with st.spinner("Respondendo..."):
                    resposta = ia_conversa.conversa_com_info(
                        pergunta, historico, ctx, []
                    )
                if not resposta:
                    resposta = "Ola! Sobre qual tema voce quer pesquisar?"
            else:
                resposta = "Ola! Sobre qual tema voce quer pesquisar?"

            st.markdown(resposta)
            conv["mensagens"].append({
                "role": "assistant",
                "content": resposta,
                "sims": {},
            })

        # ====================================================
        # PESQUISA
        # ====================================================
        elif intencao == "PESQUISA":
            if ctx.get("tem_contexto_minimo"):
                query = ia_conversa.montar_query_busca(ctx)
                tema_query = ia_conversa.refinar_tema(ctx)

                st.markdown("Buscando: `" + query + "`")

                filt, sims, contagem = buscar_e_atualizar(conv, query, tema_query)

                r = []
                r.append("### Resultados para: `" + query + "`")
                r.append("")

                r.extend(montar_resumo_categorias(conv, contagem))

                top = listar_top_por_categoria(conv, lim_por_cat=2)
                if top:
                    r.append("---")
                    r.append("**Principais resultados:**")
                    r.append("")
                    r.extend(top)

                if IA_OK:
                    with st.spinner("Sintetizando..."):
                        resultado_ia = ia_conversa.sintetizar_busca(
                            tema_query,
                            conv.get("dados_bases", {}),
                            historico,
                            max_por_cat=2,
                        )

                    if resultado_ia:
                        r.append("---")

                        if resultado_ia.get("resumo_executivo"):
                            r.append("### Resumo Executivo")
                            r.append("")
                            r.append(resultado_ia["resumo_executivo"])
                            r.append("")

                        if resultado_ia.get("sintese_academica"):
                            r.append("### Sintese Academica")
                            r.append("")
                            r.append(resultado_ia["sintese_academica"])
                            r.append("")

                        if resultado_ia.get("analise_critica"):
                            r.append("### Analise Critica")
                            r.append("")
                            r.append(resultado_ia["analise_critica"])
                            r.append("")

                        if resultado_ia.get("direcoes"):
                            r.append("### Direcoes Sugeridas")
                            r.append("")
                            r.append(resultado_ia["direcoes"])
                            r.append("")

                if sims:
                    r.append("---")
                    r.append("**Simulacoes:**")
                    for sid, d in list(sims.items())[:5]:
                        if "erro" in d:
                            continue
                        r.append("- " + d.get("simulador", sid))
                    r.append("")

                if ctx.get("pronto_para_relatorio"):
                    r.append("---")
                    r.append("### Pronto para relatorios")
                    r.append("")
                    r.append("Escolha:")
                    r.append("- `gera um tcc`")
                    r.append("- `quero um artigo`")
                    r.append("- `faz uma dissertacao`")
                    r.append("- `gera uma poc`")
                else:
                    if IA_OK:
                        with st.spinner("Preparando pergunta..."):
                            prox = ia_conversa.proxima_pergunta(ctx)
                        r.append("---")
                        r.append(prox)

                rtxt = "\n".join(r)
                st.markdown(rtxt)
                conv["mensagens"].append({
                    "role": "assistant",
                    "content": rtxt,
                    "sims": sims,
                })

            else:
                if IA_OK:
                    with st.spinner("Conversando..."):
                        resposta = ia_conversa.conversa_com_info(
                            pergunta, historico, ctx, []
                        )
                    if not resposta:
                        resposta = "Me conte sobre qual tema voce quer pesquisar."
                else:
                    resposta = "Me conte sobre qual tema voce quer pesquisar."

                st.markdown(resposta)
                conv["mensagens"].append({
                    "role": "assistant",
                    "content": resposta,
                    "sims": {},
                })

        # ====================================================
        # ESCLARECER
        # ====================================================
        else:
            resposta = (
                "Nao entendi. Voce quer:\n"
                "1. Conversar sobre um tema?\n"
                "2. Pesquisar algo cientifico?\n"
                "3. Gerar um relatorio?"
            )
            st.markdown(resposta)
            conv["mensagens"].append({
                "role": "assistant",
                "content": resposta,
                "sims": {},
            })

    st.rerun()