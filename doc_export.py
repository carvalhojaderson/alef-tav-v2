# doc_export.py - Converte relatorio TXT para RTF (.doc com formatacao)
def _esc(s):
    return (s.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
             .replace("\t", "\\tab "))

def to_rtf(texto, titulo="ALEF-TAV"):
    rtf = []
    rtf.append(r"{\rtf1\ansi\ansicpg1252\deff0")
    rtf.append(r"{\fonttbl{\f0 Arial;}{\f1 Courier New;}{\f2 Times New Roman;}}")
    rtf.append(r"{\colortbl;\red0\green0\blue0;\red139\green92\blue246;\red100\green100\blue100;}")
    rtf.append(r"\viewkind4\uc1\deflang1046")
    rtf.append(r"\paperw11906\paperh16838")
    rtf.append(r"\margl1701\margr1134\margt1701\margb1134")
    rtf.append(r"\pard\f0\fs22")
    for linha in texto.split("\n"):
        s = linha.rstrip()
        if not s:
            rtf.append(r"\par"); continue
        if s.startswith("=") and len(s) >= 20:
            rtf.append(r"\pard\sb240\sa120\qc\b\fs28\cf2 " + _esc(s) + r"\b0\cf1\fs22\par"); continue
        if s.startswith("-") and len(s) >= 20:
            rtf.append(r"\pard\sa120\par"); continue
        is_table = (s.startswith("+") or s.startswith("|") or
                    (s.startswith(" ") and ("|" in s or "+" in s[:5])))
        if is_table:
            rtf.append(r"\pard\f1\fs18\sa0\li0 " + _esc(s) + r"\f0\fs22\par"); continue
        is_chart = ((s.startswith("    ") and any(c in s for c in ["|","/","\\","#","+"]))
                    or ("|" in s and "#" in s))
        if is_chart:
            rtf.append(r"\pard\f1\fs18\sa0\li0 " + _esc(s) + r"\f0\fs22\par"); continue
        if s.startswith("      ") and len(s) > 30:
            rtf.append(r"\pard\f0\fs20\li2268\sa60 " + _esc(s.strip()) + r"\par"); continue
        if (len(s) < 80 and s[0].isdigit() and "." in s[:5] and s.upper() != s):
            rtf.append(r"\pard\sb180\sa80\b\fs24 " + _esc(s) + r"\b0\fs22\par"); continue
        if s.isupper() and 3 < len(s) < 80:
            rtf.append(r"\pard\sb160\sa100\b\fs24 " + _esc(s) + r"\b0\fs22\par"); continue
        if s.startswith("[") and "]" in s[:6]:
            rtf.append(r"\pard\f0\fs20\sa60\li0\fi-340 " + _esc(s) + r"\par"); continue
        rtf.append(r"\pard\f0\fs22\qj\sa120 " + _esc(s) + r"\par")
    rtf.append("}")
    return "\n".join(rtf).encode("latin-1", errors="replace")