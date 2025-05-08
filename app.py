import streamlit as st
from datetime import date
import matplotlib.pyplot as plt
import db  # 匯入剛剛的 db.py

st.title("🗓️ 用藥時間軸記錄")

# 側邊欄：管理藥物清單
with st.sidebar:
    st.header("藥物管理")
    new_med = st.text_input("新增藥物名稱")
    if st.button("新增藥物"):
        if new_med.strip():
            db.add_med(new_med.strip())
            st.success(f"已新增 {new_med.strip()}")
            st.experimental_rerun()

    meds = db.get_meds()
    if meds:
        to_del = st.selectbox("刪除藥物", options=meds)
        if st.button("刪除藥物"):
            db.remove_med(to_del)
            st.success(f"已刪除 {to_del}")
            st.experimental_rerun()
    else:
        st.info("尚無任何藥物，請先新增。")

# 主畫面：新增服藥記錄
st.subheader("📝 新增服藥記錄")
meds = db.get_meds()
if meds:
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_med = st.selectbox("藥物", meds)
    with col2:
        take_day = st.date_input("日期", date.today())
    with col3:
        dosage = st.text_input("劑量", "100mg")

    if st.button("確定新增"):
        db.add_entry(sel_med, take_day.isoformat(), dosage)
        st.success(f"已為 {sel_med} 新增記錄 ({take_day}, {dosage})")
        st.experimental_rerun()
else:
    st.info("請先在側邊欄新增藥物。")

# 主畫面：繪製時間軸
st.subheader("📊 用藥時間軸")
df = db.get_all_entries_df()
if df.empty:
    st.warning("目前沒有任何服藥記錄。")
else:
    meds_unique = df['name'].unique().tolist()
    fig, ax = plt.subplots(
        figsize=(10, max(2, len(meds_unique)*0.5))
    )
    for i, med in enumerate(meds_unique):
        sub = df[df['name']==med]
        ax.scatter(sub['date'], [i]*len(sub), label=med)
    ax.set_yticks(range(len(meds_unique)))
    ax.set_yticklabels(meds_unique)
    ax.set_xlabel("日期")
    ax.grid(axis='x')
    st.pyplot(fig)
