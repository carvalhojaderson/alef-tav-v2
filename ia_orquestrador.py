# ============================================================
#   ALEF-TAV - ORQUESTRADOR DE IA (7 CAMADAS)
# ============================================================
try:
    import provedores_ia
except ImportError:
    provedores_ia = None

# ============================================================
# DEFINICAO DAS 7 CAMADAS
# ============================================================
CAMADAS = {
    # 🥇 1 - Sintese academica (textos longos, ABNT)
    "sintese": [
        ("nvidia", "moonshotai/kimi-k3"),
        ("nvidia", "nvidia/nemotron-3-super-120b-a12b"),
        ("nvidia", "mistralai/mistral-nemotron"),
        ("groq",   "llama-3.3-70b-versatile"),
    ],
    # 🧠 2 - Raciocinio critico (analise, gaps)
    "raciocinio": [
        ("nvidia", "deepseek-ai/deepseek-r1"),
        ("nvidia", "nvidia/nemotron-3-super-120b-a12b"),
        ("nvidia", "moonshotai/kimi-k3"),
        ("groq",   "llama-3.3-70b-versatile"),
    ],
    # ⚡ 3 - Resposta rapida (chat, classificacao)
    "rapida": [
        ("groq",   "llama-3.3-70b-versatile"),
        ("groq",   "qwen/qwen3-32b"),
        ("groq",   "llama-3.1-8b-instant"),
        ("nvidia", "meta/llama-3.3-70b-instruct"),
    ],
    # 🌐 4 - Traducao (PT <-> EN)
    "traducao": [
        ("groq",   "qwen/qwen3-32b"),
        ("groq",   "llama-3.3-70b-versatile"),
        ("nvidia", "moonshotai/kimi-k3"),
    ],
    # 🔍 5 - Verificacao / consistencia
    "verificacao": [
        ("nvidia", "nvidia/nemotron-3-super-120b-a12b"),
        ("nvidia", "deepseek-ai/deepseek-r1"),
        ("groq",   "llama-3.3-70b-versatile"),
    ],
    # 📐 6 - Formatacao ABNT (normas, citacoes)
    "abnt": [
        ("nvidia", "mistralai/mistral-nemotron"),
        ("nvidia", "moonshotai/kimi-k3"),
        ("groq",   "llama-3.3-70b-versatile"),
    ],
    # 📋 7 - Sumarizacao executiva (curta, objetiva)
    "sumarizacao": [
        ("groq",   "llama-3.1-8b-instant"),
        ("groq",   "qwen/qwen3-32b"),
        ("nvidia", "meta/llama-3.3-70b-instruct"),
    ],
}

def _chamar(camada, prompt, max_tokens=2000, temperatura=0.3):
    """Tenta modelos da camada em ordem ate um funcionar."""
    if not provedores_ia:
        return None, "sem_provedor"
    for provedor, modelo in CAMADAS.get(camada, CAMADAS["rapida"]):
        try:
            txt = provedores_ia._openai(provedor, prompt, modelo,
                                         temperatura, max_tokens)
            if txt:
                return txt, f"{provedor}/{modelo}"
        except:
            continue
    return None, "todos_falharam"

# ============================================================
# API PUBLICA POR CAMADA
# ============================================================
def gerar_sintese(prompt, max_tokens=3000):
    return _chamar("sintese", prompt, max_tokens)

def gerar_raciocinio(prompt, max_tokens=2000):
    return _chamar("raciocinio", prompt, max_tokens)

def gerar_rapida(prompt, max_tokens=800):
    return _chamar("rapida", prompt, max_tokens)

def gerar_traducao(prompt, max_tokens=500):
    return _chamar("traducao", prompt, max_tokens)

def gerar_verificacao(prompt, max_tokens=1500):
    return _chamar("verificacao", prompt, max_tokens)

def gerar_abnt(prompt, max_tokens=2000):
    return _chamar("abnt", prompt, max_tokens)

def gerar_sumarizacao(prompt, max_tokens=400):
    return _chamar("sumarizacao", prompt, max_tokens)

# ============================================================
# TRADUCAO REAL (PT -> EN para APIs)
# ============================================================
def traduzir_pt_en(texto):
    """Traduz PT para EN usando Qwen3."""
    prompt = (
        f"Translate the following Portuguese text to English scientific "
        f"terminology. Return ONLY the translation, no explanations:\n\n"
        f"{texto}"
    )
    txt, _ = gerar_traducao(prompt, max_tokens=300)
    return txt.strip() if txt else texto

# ============================================================
# VERIFICACAO DE FATOS
# ============================================================
def verificar_consistencia(texto, fontes):
    """Verifica se o texto esta consistente com as fontes."""
    ctx = "\n".join(f"- {f[:150]}" for f in fontes[:10])
    prompt = (
        f"Verifique se o TEXTO abaixo e consistente com as FONTES.\n\n"
        f"TEXTO:\n{texto[:1000]}\n\n"
        f"FONTES:\n{ctx}\n\n"
        f"Responda:\n"
        f"- CONSISTENTE: sim/nao\n"
        f"- PROBLEMAS: (lista se houver)\n"
        f"- SUGESTOES: (1-2 itens)"
    )
    txt, _ = gerar_verificacao(prompt, max_tokens=600)
    return txt

# ============================================================
# SINTESE POR SECAO
# ============================================================
def _ctx(conv, n=8):
    arts = list(conv.get("artigos", {}).values())[:n]
    return "\n".join(f"[{i}] {a.get('titulo','')[:100]} ({a.get('ano','')})"
                     for i, a in enumerate(arts, 1))

def sintetizar_introducao(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Escreva introducao academica (150-200 palavras) sobre '{tema}' "
        f"em portugues, ABNT. Artigos:\n\n{_ctx(conv)}\n\nApenas o texto."
    )
    txt, _ = gerar_sintese(prompt)
    return txt

def sintetizar_referencial(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Escreva referencial teorico (400-500 palavras) sobre '{tema}', "
        f"organizado em 3 correntes. Citacoes (Autor, ano).\n\n"
        f"{_ctx(conv)}\n\nApenas o texto."
    )
    txt, _ = gerar_sintese(prompt, max_tokens=4000)
    return txt

def sintetizar_conclusao(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Escreva conclusao academica (150-200 palavras) sobre '{tema}', "
        f"sintetizando achados e recomendacoes."
    )
    txt, _ = gerar_sintese(prompt)
    return txt

def sintetizar_discussao(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Discussao academica (300-400 palavras) sobre '{tema}' com: "
        f"(i) implicacoes teoricas; (ii) praticas; (iii) limitacoes; "
        f"(iv) trabalhos futuros."
    )
    txt, _ = gerar_raciocinio(prompt, max_tokens=3000)
    return txt

def sintetizar_analise_critica(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Analise critica de '{tema}' em 4 topicos: "
        f"(1) consistencia teorica; (2) convergencia; (3) limitacoes; "
        f"(4) implicacoes."
    )
    txt, _ = gerar_raciocinio(prompt, max_tokens=1500)
    return txt

def sintetizar_barreiras(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Liste 6 barreiras para '{tema}' (B1-B6), cada uma com "
        f"descricao + nivel D=X/9."
    )
    txt, _ = gerar_raciocinio(prompt, max_tokens=1200)
    return txt

def sintetizar_viabilidade(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Avalie viabilidade de '{tema}' em 6 linhas: Score (0-9), "
        f"TRL atual, TRL alvo, prazo, investimento, payback."
    )
    txt, _ = gerar_raciocinio(prompt, max_tokens=800)
    return txt

def sintetizar_rotas(conv):
    tema = conv.get("titulo", "tema")
    prompt = (
        f"Proponha 5 rotas (R1-R5) para '{tema}' com: nome, TRL, "
        f"probabilidade, recomendacao."
    )
    txt, _ = gerar_raciocinio(prompt, max_tokens=1200)
    return txt

# ============================================================
# MELHORAR RESPOSTA DO CHAT (usa camada rapida)
# ============================================================
def melhorar_resposta_chat(pergunta, artigos):
    if not artigos: return None
    ctx = "\n".join(f"- {a.get('titulo','')[:120]} ({a.get('ano','')})"
                    for a in artigos[:5])
    prompt = (
        f"Pergunta: '{pergunta}'\n\n"
        f"Artigos:\n{ctx}\n\n"
        f"Resposta academica curta (100-150 palavras):"
    )
    txt, _ = gerar_rapida(prompt, max_tokens=800)
    return txt

# ============================================================
# SUMARIZAR RESULTADOS (camada 7)
# ============================================================
def sumarizar_resultados(tema, contagem):
    """Resumo executivo dos resultados."""
    ctx = "\n".join(f"- {k}: {v} resultados" for k, v in contagem.items() if v > 0)
    prompt = (
        f"Resuma em 3 bullets (max 15 palavras cada) os resultados "
        f"da busca sobre '{tema}':\n\n{ctx}"
    )
    txt, _ = gerar_sumarizacao(prompt, max_tokens=300)
    return txt

# ============================================================
# UTILITARIOS
# ============================================================
def testar():
    if not provedores_ia: return {}
    return provedores_ia.testar_todos()

def disponiveis():
    if not provedores_ia: return []
    return provedores_ia.provedores_disponiveis()

def info_camadas():
    return {
        "1 - Sintese":     "Kimi K3 → Nemotron → Mistral",
        "2 - Raciocinio":  "DeepSeek R1 → Nemotron → Kimi K3",
        "3 - Rapida":      "Llama 3.3 → Qwen3 → Llama 3.1",
        "4 - Traducao":    "Qwen3 32B → Llama 3.3 → Kimi K3",
        "5 - Verificacao": "Nemotron 120B → DeepSeek R1",
        "6 - ABNT":        "Mistral Nemotron → Kimi K3",
        "7 - Sumarizacao": "Llama 3.1 → Qwen3",
    }

if __name__ == "__main__":
    print("=" * 60)
    print("  ALEF-TAV - 7 Camadas de IA")
    print("=" * 60)
    print(f"Provedores: {disponiveis()}")
    print()
    print("Camadas:")
    for k, v in info_camadas().items():
        print(f"  {k}: {v}")