# AI BI Assistant (bez AI)

Jednoduchá Streamlit aplikace pro rychlé vyhodnocení CSV dat:
- náhled dat
- profil sloupců (typ, chybějící hodnoty, unikáty, příklad)
- KPI pro numerické sloupce
- jednoduchý trendový graf v čase (pokud dataset obsahuje datumový sloupec)

> Manažerské shrnutí je zatím pravidlové (bez volání AI). AI část lze doplnit později.

## Spuštění lokálně

### 1) Vytvoření a aktivace virtuálního prostředí
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1

2) Instalace závislostí
pip install streamlit pandas numpy matplotlib

3) Spuštění aplikace
streamlit run app.py

Použití

Nahraj CSV soubor

Aplikace zobrazí základní metriky, profil a KPI

Pokud najde sloupec s názvem obsahujícím date nebo datum, zkusí vykreslit trend

Poznámky

Pro správné parsování datumů se doporučuje formát ISO (YYYY-MM-DD) nebo běžné české formáty (DD.MM.YYYY).

Pokud dataset neobsahuje datumový sloupec nebo numerické sloupce, graf se nezobrazí.
