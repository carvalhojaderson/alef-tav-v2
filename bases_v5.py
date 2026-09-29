
# ============ SCOPUS (institucional) — ACRESCENTADO ============
try:
    from modulo_scopus import buscar_scopus
    SCOPUS_OK = True
except Exception as e:
    SCOPUS_OK = False
    SCOPUS_ERRO = str(e)

if SCOPUS_OK:
    @_registra("scopus_institucional", "literatura", modo="API-Key")
    def r_scopus(q, n=4):
        return buscar_scopus(q, n)