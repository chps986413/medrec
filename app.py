# app.py
import streamlit as st
from datetime import date, datetime, time
import matplotlib.pyplot as plt
import db  # 匯入 db.py

st.title("🗓️ 用藥時間軸記錄")

# 側邊欄：藥物管理
with st.sidebar:
    st.header("藥物管理")
    new_med = st.text_input("新增藥物名稱")
    if st.button("新增藥物"):
        if new_med.strip():
            db.add_med(new_med.strip())
            st.success(f"已新增 {new_med.strip()}")

    meds = db.get_meds()
    if meds:
        to_del = st.selectbox("刪除藥物", options=meds)
        if st.button("刪除藥物"):
            db.remove_med(to_del)
            st.success(f"已刪除 {to_del}")
    else:
        st.info("尚無任何藥物，請先新增。")

# 主畫面：新增服藥記錄
st.subheader("📝 新增服藥記錄")
meds = db.get_meds()
if meds:
    col1, col2, col3, col4 = st.columns([2,2,2,2])
    with col1:
        sel_med = st.selectbox("藥物", meds)
    with col2:
        sel_date = st.date_input("日期", date.today())
    with col3:
        # 產生 00:00, 00:30, …, 23:30
        half_hours = [time(h, m) for h in range(24) for m in (0, 30)]
        sel_time = st.selectbox("時間", half_hours)
    with col4:
        dosage = st.text_input("劑量", "100mg")

    if st.button("確定新增"):
        dt = datetime.combine(sel_date, sel_time)
        db.add_entry(sel_med, dt.isoformat(), dosage)
        st.success(f"已為 {sel_med} 新增記錄 ({dt.strftime('%Y-%m-%d %H:%M')}, {dosage})")
else:
    st.info("請先新增藥物。")

# 主畫面：用藥時間軸
st.subheader("📊 用藥時間軸")
_df = db.get_all_entries_df()
if _df.empty:
    st.warning("目前沒有任何服藥記錄。")
else:
    meds_unique = _df['name'].unique().tolist()
    fig, ax = plt.subplots(figsize=(10, max(2, len(meds_unique)*0.5)))
    for i, med in enumerate(meds_unique):
        sub = _df[_df['name']==med]
        ax.scatter(sub['date'], [i]*len(sub), label=med)
    ax.set_yticks(range(len(meds_unique)))
    ax.set_yticklabels(meds_unique)
    ax.set_xlabel("日期")
    ax.grid(axis='x')
    st.pyplot(fig)

# 管理現有紀錄
st.subheader("🗂️ 管理現有紀錄")
_df2 = db.get_all_entries_df()
if _df2.empty:
    st.info("目前沒有任何記錄。")
else:
    for idx, row in _df2.iterrows():
        entry_id = row['id']
        date_str = row['date'].strftime("%Y-%m-%d %H:%M")
        st.write(f"**{row['name']}** — {date_str} — {row['dosage']}", key=idx)
        c1, c2 = st.columns([1,1])
        if c1.button("刪除", key=f"del-{entry_id}"):
            db.delete_entry(entry_id)
        if c2.button("編輯", key=f"edit-{entry_id}"):
            pass
