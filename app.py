import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI BI Assistant (bez AI)", layout="wide")
st.title("AI BI Assistant 🧾 (profil + KPI + graf) — bez AI")

def profile_df(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append({
            "column": col,
            "dtype": str(s.dtype),
            "missing": int(s.isna().sum()),
            "missing_%": round(float(s.isna().mean() * 100), 2),
            "unique": int(s.nunique(dropna=True)),
            "example": "" if s.dropna().empty else str(s.dropna().iloc[0])[:50],
        })
    return pd.DataFrame(rows)

def numeric_kpis(df: pd.DataFrame) -> pd.DataFrame:
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        return pd.DataFrame(columns=["metric", "value"])
    total_cells = num.size
    missing_cells = int(num.isna().sum().sum())
    return pd.DataFrame([
        {"metric": "Numeric columns", "value": num.shape[1]},
        {"metric": "Numeric missing cells", "value": missing_cells},
        {"metric": "Numeric missing %", "value": round(missing_cells / total_cells * 100, 2) if total_cells else 0},
    ])


# načtení
uploaded = st.file_uploader("Nahraj CSV", type=["csv"])

if uploaded is None:
    st.info("Nahraj prosím CSV soubor.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception:
    uploaded.seek(0)
    df = pd.read_csv(uploaded, sep=";")
    
# pokus o automatické převedení datumových sloupců
for col in df.columns:
    if "date" in col.lower() or "datum" in col.lower():
        df[col] = pd.to_datetime(df[col], errors="coerce")

# základní info
col1, col2, col3 = st.columns(3)
col1.metric("Řádky", f"{len(df):,}".replace(",", " "))
col2.metric("Sloupce", f"{len(df.columns)}")
col3.metric("Chybějící hodnoty", f"{int(df.isna().sum().sum()):,}".replace(",", " "))

st.subheader("Náhled dat")
st.dataframe(df.head(50), use_container_width=True)

# profil sloupců
st.subheader("Profil sloupců")
prof = profile_df(df)
st.dataframe(prof, use_container_width=True)

# KPI pro numerické sloupce
st.subheader("Rychlé KPI (numerické sloupce)")
kpi = numeric_kpis(df)
st.dataframe(kpi, use_container_width=True)

st.subheader("Graf (pokud jde): trend v čase")

df_dt = df.copy()
date_candidates = [c for c in df_dt.columns if "date" in c.lower() or "datum" in c.lower()]
date_col = None

for c in date_candidates:
    dt = pd.to_datetime(df_dt[c], errors="coerce")
    if dt.notna().sum() >= 1:
        df_dt[c] = dt
        date_col = c
        break

num_cols = df_dt.select_dtypes(include=[np.number]).columns.tolist()

if date_col and num_cols:
    # defaultně vybereme první numerický sloupec (např. revenue)
    metric_col = st.selectbox("Vyber numerickou metriku", num_cols, index=0)

    g = df_dt.dropna(subset=[date_col]).copy()
    g["day"] = g[date_col].dt.date  # denní agregace (u malých dat je to lepší než měsíční)
    series = g.groupby("day")[metric_col].sum().sort_index()

    if len(series) >= 1:
        fig = plt.figure()
        plt.plot(series.index, series.values, marker="o")
        plt.xticks(rotation=45)
        plt.title(f"{metric_col} v čase")
        plt.tight_layout()
        st.pyplot(fig)
        st.write("Hodnoty:", series.to_frame(name=metric_col))
    else:
        st.warning("Nemám žádná platná data pro vykreslení (zkontroluj datumový sloupec).")
else:
    st.info("Nenašel jsem datumový sloupec (např. 'date'/'datum') nebo numerický sloupec pro graf.")

st.subheader("🧠 „Manažerské shrnutí“ (pravidla, bez AI)")

if st.button("Vygeneruj shrnutí"):
    rows = len(df)
    cols = len(df.columns)
    missing_total = int(df.isna().sum().sum())
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # hezký text
    st.success("Shrnutí bylo vygenerováno (bez AI).")

    st.markdown(
        f"""
**Shrnutí dat**
- Počet řádků: **{rows}**
- Počet sloupců: **{cols}**
- Chybějící hodnoty celkem: **{missing_total}**
- Číselné sloupce: **{", ".join(numeric_cols) if numeric_cols else "žádné"}**
        """.strip()
    )

    # detailní tabulka s metrikami pro číselné sloupce
    if numeric_cols:
        num = df[numeric_cols]
        summary = pd.DataFrame({
            "součet": num.sum(numeric_only=True),
            "průměr": num.mean(numeric_only=True),
            "min": num.min(numeric_only=True),
            "max": num.max(numeric_only=True),
        }).reset_index().rename(columns={"index": "sloupec"})

        st.markdown("**Základní metriky (číselné sloupce)**")
        st.dataframe(summary, use_container_width=True)

        st.markdown("**Doporučení**")
        st.markdown(
            "- Sleduj trend hlavní metriky v čase (graf výše).\n"
            "- Když přidáš sloupce jako region/produkt, půjde udělat segmentace.\n"
            "- Ověřuj výkyvy (dny s extrémně nízkou/vysokou hodnotou)."
        )
    else:
        st.warning("V datech nejsou žádné číselné sloupce, takže nelze spočítat metriky.")