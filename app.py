import os
import streamlit as st
from collections import defaultdict
from auth_wrapper import run_signed_query

FIRM_IDS = {"berkshire": "1088", "blackrock": "1034"}

st.title("🐋 WhaleWisdom Top Holdings Analyzer")

firm_choices = st.multiselect("Choose firms:", FIRM_IDS.keys(), default=list(FIRM_IDS.keys()))
top_n = st.slider("Top N holdings per firm", 1, 20, 5)
result_n = st.slider("Top results to show", 1, 10, 3)
quarter_id = st.text_input("Quarter ID", value="185")

if not os.getenv("WW_SHARED_KEY") or not os.getenv("WW_SECRET_KEY"):
    st.error("Set WW_SHARED_KEY and WW_SECRET_KEY in your environment.")
    st.stop()

def get_holdings(fid):
    args = {"command": "filer_holdings", "filer_id": fid, "quarter_id": quarter_id}
    result = run_signed_query(args)
    return [(h["ticker"], float(h["percent_portfolio"])) for h in result.get("holdings", [])[:top_n]]

def aggregate():
    agg = defaultdict(list)
    for name in firm_choices:
        for t, p in get_holdings(FIRM_IDS[name]):
            agg[t].append(p)
    return sorted([(t, sum(p)/len(p)) for t, p in agg.items()], key=lambda x: x[1], reverse=True)

if st.button("Analyze"):
    try:
        with st.spinner("Processing..."):
            results = aggregate()
        st.subheader("Top Holdings")
        for ticker, avg_pct in results[:result_n]:
            st.write(f"**{ticker.upper()}** — {avg_pct:.2f}%")
    except Exception as e:
        st.error(str(e))