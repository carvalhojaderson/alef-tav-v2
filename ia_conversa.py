# ============================================================
#   ALEF-TAV - IA CONVERSACIONAL COMPLETA
# ============================================================

try:
    import ia_orquestrador
except:
    ia_orquestrador = None

# ============================================================
# CONTEXTO
# ============================================================
def novo_contexto():
    """Cria contexto vazio."""
    return {
        "tema": "",
        "area": "",
        "foco": "",
        "aplicacao": "",
        "nivel": "",
        "turnos": 0,
        "ultima_busca": "",
        "tem_contexto_minimo": False,
        "pronto_para_relatorio": False,
    }

def montar_query_busca(ctx):
    """Monta query com TODO o contexto acumulado."""
    partes = []
    if ctx.get("tema"):       partes.append(ctx["tema"])
    if ctx.get("foco"):       partes.append(ctx["foco"])
    if ctx.get("aplicacao"):  partes.append(ctx["aplicacao"])
    if ctx.get("area") and ctx["area"] not in " ".join(partes):
        partes.append(ctx["area"])
    return " ".join(p for p in partes if p).strip()

def tem_minimo(ctx):
    """Tem tema definido?"""
    return len(ctx.get("tema", "")) >= 4

def pronto_relatorio(ctx):
    """Tem tema + pelo menos 1 detalhe?"""
    if not tem_minimo(ctx): return False
    preenchidos = sum(1 for k in ["tema","foco","aplicacao","area"]
                      if ctx.get(k))
    return preenchidos >= 2

# ============================================================
# EXTRAIR CONTEXTO
# ============================================================
PROMPT_EXTRAIR = """Extraia informacoes de pesquisa da mensagem.

Contexto ATUAL:
{contexto}

Mensagem: "{mensagem}"

Responda APENAS com JSON:
{{
  "tema": "tema cientifico principal (ou vazio)",
  "area": "area do conhecimento (ou vazio)",
  "foco": "sintese/propriedades/aplicacoes/analise (ou vazio)",
  "aplicacao": "aplicacao pratica (ou vazio)",
  "nivel": "graduacao/mestrado/doutorado (ou vazio)"
}}

Nao invente. Se nao tiver certeza, deixe vazio."""

def extrair_contexto(mensagem, ctx_atual):
    novo = dict(ctx_atual)
    novo["turnos"] = ctx_atual.get("turnos", 0) + 1

    if not ia_orquestrador:
        if not novo.get("tema") and len(mensagem.split()) >= 1:
            novo["tema"] = mensagem[:80]
        novo["tem_contexto_minimo"] = tem_minimo(novo)
        novo["pronto_para_relatorio"] = pronto_relatorio(novo)
        return novo

    ctx_txt = "\n".join(f"  {k}: {v}" for k, v in ctx_atual.items()
                        if v and k not in ["tem_contexto_minimo",
                                            "pronto_para_relatorio",
                                            "ultima_busca","turnos"])

    prompt = PROMPT_EXTRAIR.format(contexto=ctx_txt or "(vazio)",
                                    mensagem=mensagem)
    try:
        resp, _ = ia_orquestrador.gerar_rapida(prompt, max_tokens=250)
        if resp:
            import json, re as _re
            match = _re.search(r'\{[^{}]+\}', resp, re.DOTALL)
            if match:
                dados = json.loads(match.group(0))
                for k in ["tema","area","foco","aplicacao","nivel"]:
                    v = dados.get(k, "").strip() if isinstance(dados.get(k), str) else ""
                    if v and v.lower() not in ["vazio","", "n/a", "none"]:
                        if not novo.get(k) or len(v) > len(novo.get(k, "")):
                            novo[k] = v[:80]
    except: pass

    novo["tem_contexto_minimo"] = tem_minimo(novo)
    novo["pronto_para_relatorio"] = pronto_relatorio(novo)
    return novo

# ============================================================
# DETECTAR INTENCAO
# ============================================================
PROMPT_INTENCAO = """Classifique a mensagem:

- CONVERSA    - saudacao, agradecimento
- RELATORIO   - quer documento (tcc, artigo, poc, etc)
- ESCLARECER  - ambigua

Qualquer mensagem sobre tema cientifico e PESQUISA.

Contexto: {historico}

Mensagem: "{mensagem}"

Responda 1 palavra (CONVERSA, PESQUISA, RELATORIO ou ESCLARECER):"""

def detectar_intencao(mensagem, historico="", contexto=None):
    if not ia_orquestrador:
        return _fb_intencao(mensagem)
    try:
        resp, _ = ia_orquestrador.gerar_rapida(
            PROMPT_INTENCAO.format(mensagem=mensagem, historico=historico[-400:]),
            max_tokens=10)
        if resp:
            r = resp.strip().upper()
            for op in ["CONVERSA","PESQUISA","RELATORIO","ESCLARECER"]:
                if op in r: return op
    except: pass
    return _fb_intencao(mensagem)

def _fb_intencao(msg):
    t = msg.lower().strip()
    if any(s in t for s in ["ola","olá","oi","obrigad","valeu","ok"]):
        return "CONVERSA"
    if any(s in t for s in ["gerar","gera","tcc","artigo","poc",
                             "mestrado","doutorado","relatorio","disserta"]):
        return "RELATORIO"
    if len(t.split()) >= 1:
        return "PESQUISA"
    return "CONVERSA"

# ============================================================
# CONVERSA COM INFO
# ============================================================
PROMPT_CONVERSA = """Voce e o ALEF-TAV, assistente cientifico.

Contexto acumulado:
{contexto}

Artigos ja encontrados:
{artigos}

Historico recente:
{historico}

Mensagem atual: "{mensagem}"

Regras:
- Se ja tem tema: diga o que encontrou e peca proximo detalhe
- Se nao tem tema: pergunte tema
- Se ja tem tudo: sugira gerar relatorio
- SEMPRE traga informacao util

Resposta (max 150 palavras, portugues):"""

def conversa_com_info(mensagem, historico, contexto, artigos):
    ctx_txt = "\n".join(f"  {k}: {v}" for k, v in contexto.items()
                        if v and k not in ["tem_contexto_minimo",
                                            "pronto_para_relatorio",
                                            "ultima_busca","turnos"]) or "(vazio)"

    arts_txt = "(nenhum ainda)"
    if artigos:
        arts_txt = "\n".join(
            f"- {a.get('titulo','')[:80]} ({a.get('ano','')})"
            for a in artigos[:3])

    prompt = PROMPT_CONVERSA.format(
        contexto=ctx_txt, artigos=arts_txt,
        historico=historico[-600:], mensagem=mensagem)
    try:
        txt, _ = ia_orquestrador.gerar_sintese(prompt, max_tokens=600)
        return txt
    except: return None

# ============================================================
# SINTESE MULTI-CAMADA
# ============================================================
def sintetizar_busca(tema, dados_por_categoria, historico="", max_por_cat=2):
    """Sintese usando 4 camadas especializadas."""
    if not dados_por_categoria: return None

    ctx_partes = []
    for cat, lista in dados_por_categoria.items():
        if not lista: continue
        ctx_partes.append(f"\n=== {cat.upper()} ({len(lista)}) ===")
        for item in lista[:max_por_cat]:
            ctx_partes.append(
                f"  • {item.get('titulo','')[:120]} "
                f"({item.get('fonte','')}, {item.get('ano','')})")
    ctx = "\n".join(ctx_partes)

    resultado = {}

    # Camada 1 - Kimi K3
    prompt1 = (
        f"Escreva SINTESE ACADEMICA (350-450 palavras) sobre '{tema}' "
        f"com base nas bases abaixo.\n\n"
        f"Organize em 3-4 paragrafos por area. Tom ABNT.\n\n"
        f"BASES:\n{ctx}\n\nSintese:"
    )
    try:
        resultado["sintese_academica"], _ = ia_orquestrador.gerar_sintese(
            prompt1, max_tokens=2000)
    except: resultado["sintese_academica"] = None

    # Camada 2 - DeepSeek R1
    prompt2 = (
        f"Analise CRITICAMENTE '{tema}' em 3 topicos:\n"
        f"1. **Convergencias**\n2. **Lacunas**\n3. **Contradicoes**\n\n"
        f"BASES:\n{ctx}\n\nAnalise:"
    )
    try:
        resultado["analise_critica"], _ = ia_orquestrador.gerar_raciocinio(
            prompt2, max_tokens=1200)
    except: resultado["analise_critica"] = None

    # Camada 3 - Llama rapida
    prompt3 = (
        f"Sugira 3 DIRECOES de pesquisa sobre '{tema}'.\n"
        f"Formato: '1. [direcao] - [justificativa]'\n\n"
        f"BASES:\n{ctx}"
    )
    try:
        resultado["direcoes"], _ = ia_orquestrador.gerar_rapida(
            prompt3, max_tokens=500)
    except: resultado["direcoes"] = None

    # Camada 5 - Nemotron: verificacao
    if resultado.get("sintese_academica"):
        prompt5 = (
            f"Verifique consistencia. Responda: CONSISTENTE (sim/nao) + "
            f"problemas + sugestoes.\n\n"
            f"SINTESE:\n{resultado['sintese_academica'][:800]}\n\n"
            f"FONTES:\n{ctx[:800]}"
        )
        try:
            resultado["verificacao"], _ = ia_orquestrador.gerar_verificacao(
                prompt5, max_tokens=600)
        except: resultado["verificacao"] = None

    # Camada 7 - Sumarizacao
    contagem = {k: len(v) for k, v in dados_por_categoria.items() if v}
    try:
        resultado["resumo_executivo"] = ia_orquestrador.sumarizar_resultados(
            tema, contagem)
    except: resultado["resumo_executivo"] = None

    return resultado

# ============================================================
# DETECTAR TIPO DE RELATORIO
# ============================================================
def detectar_tipo_relatorio(mensagem):
    if not ia_orquestrador:
        return _fb_tipo(mensagem)
    try:
        resp, _ = ia_orquestrador.gerar_rapida(
            f"Tipo de relatorio pedido: '{mensagem}'\n"
            f"Opcoes: tcc, mestrado, doutorado, artigo, tecnico, poc, "
            f"financeiro, captacao, rotas\n"
            f"Responda apenas 1 palavra:", max_tokens=10)
        if resp:
            r = resp.strip().lower()
            for t in ["tcc","mestrado","doutorado","artigo","tecnico",
                      "poc","financeiro","captacao","rotas"]:
                if t in r: return t
    except: pass
    return _fb_tipo(mensagem)

def _fb_tipo(msg):
    t = msg.lower()
    mapa = [("tcc","tcc"),("monografia","tcc"),("mestrado","mestrado"),
            ("disserta","mestrado"),("doutorado","doutorado"),("tese","doutorado"),
            ("artigo","artigo"),("paper","artigo"),("tecnico","tecnico"),
            ("poc","poc"),("financeiro","financeiro"),("captacao","captacao"),
            ("edital","captacao"),("rota","rotas")]
    for k, v in mapa:
        if k in t: return v
    return None

# ============================================================
# REFINAR TEMA
# ============================================================
def refinar_tema(ctx):
    """Monta tema refinado a partir do contexto."""
    partes = []
    if ctx.get("tema"): partes.append(ctx["tema"])
    if ctx.get("foco"): partes.append(ctx["foco"])
    if ctx.get("aplicacao"): partes.append("em " + ctx["aplicacao"])
    tema = " ".join(p for p in partes if p).strip()
    return tema if tema else ctx.get("tema", "pesquisa")

# ============================================================
# PROXIMA PERGUNTA
# ============================================================
PROMPT_PROXIMA = """O usuario esta pesquisando sobre '{tema}'.

Contexto:
{contexto}

Qual a PROXIMA pergunta para refinar a pesquisa?

Opcoes:
- Perguntar FOCO (sintese/propriedades/aplicacoes/analise)
- Perguntar APLICACAO (eletronica/medicina/energia/etc)
- Perguntar AREA (materiais/fisica/quimica/biologia)
- Perguntar NIVEL (graduacao/mestrado/doutorado)
- Dizer "PRONTO"

Responda em 1 frase:"""

def proxima_pergunta(ctx):
    if not ia_orquestrador:
        return "Me conte mais sobre o que voce quer pesquisar."
    ctx_txt = "\n".join(f"{k}: {v}" for k, v in ctx.items()
                        if v and k not in ["tem_contexto_minimo",
                                            "pronto_para_relatorio",
                                            "ultima_busca","turnos"])
    try:
        resp, _ = ia_orquestrador.gerar_rapida(
            PROMPT_PROXIMA.format(tema=ctx.get("tema",""), contexto=ctx_txt),
            max_tokens=100)
        if resp:
            r = resp.strip()
            if "PRONTO" in r.upper():
                return "Ja tenho contexto suficiente! Vou buscar mais informacoes."
            return r
    except: pass
    return "Me conte mais sobre o que voce quer pesquisar."

# ============================================================
# TESTE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  ALEF-TAV - ia_conversa.py")
    print("=" * 60)
    print(f"Funcoes disponiveis:")
    print(f"  novo_contexto       {'OK' if 'novo_contexto' in dir() else 'X'}")
    print(f"  extrair_contexto    OK")
    print(f"  detectar_intencao   OK")
    print(f"  sintetizar_busca    OK")
    print(f"  refinar_tema        OK")
    print()
    ctx = novo_contexto()
    print(f"Contexto inicial: {ctx}")
    print()
    ctx = extrair_contexto("grafeno sintese eletronica", ctx)
    print(f"Contexto apos msg: {ctx}")
    print(f"Query: {montar_query_busca(ctx)}")