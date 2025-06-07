import streamlit as st
import random
import itertools
import matplotlib.pyplot as plt
from PIL import Image
import os

# 定数（5ペア対応）
MEN = ["A", "B", "C", "D", "E"]
WOMEN = ["V", "W", "X", "Y", "Z"]
IMAGE_DIR = "img"

# UI タイトル
st.title("安定結婚問題 - 5人バージョン + 可視化")

# セッションステート初期化
if 'men_prefs' not in st.session_state or 'women_prefs' not in st.session_state:
    st.session_state.men_prefs = {m: random.sample(WOMEN, len(WOMEN)) for m in MEN}
    st.session_state.women_prefs = {w: random.sample(MEN, len(MEN)) for w in WOMEN}

# 好み初期化ボタン
if st.sidebar.button("好みをランダム初期化"):
    st.session_state.men_prefs = {m: random.sample(WOMEN, len(WOMEN)) for m in MEN}
    st.session_state.women_prefs = {w: random.sample(MEN, len(MEN)) for w in WOMEN}

# 安定性判定関数

def is_stable(matching, men_prefs, women_prefs):
    man2woman = {m: w for m, w in matching}
    woman2man = {w: m for m, w in matching}
    for m, w in matching:
        for w2 in men_prefs[m][:men_prefs[m].index(w)]:
            if women_prefs[w2].index(m) < women_prefs[w2].index(woman2man[w2]):
                return False
    for w, m in woman2man.items():
        for m2 in women_prefs[w][:women_prefs[w].index(m)]:
            if men_prefs[m2].index(w) < men_prefs[m2].index(man2woman[m2]):
                return False
    return True

# 全安定マッチング列挙

def all_stable_matchings(men_prefs, women_prefs):
    stable = []
    for perm in itertools.permutations(WOMEN):
        matching = list(zip(MEN, perm))
        if is_stable(matching, men_prefs, women_prefs):
            stable.append(matching)
    return stable

# 不満度計算

def calculate_dissatisfaction(matching, men_prefs, women_prefs):
    m_score = sum(men_prefs[m].index(w) for m, w in matching)
    w_score = sum(women_prefs[w].index(m) for m, w in matching)
    total = m_score + w_score
    diff = abs(m_score - w_score)
    maxd = max(max(men_prefs[m].index(w), women_prefs[w].index(m)) for m, w in matching)
    return total, m_score, w_score, diff, maxd

# 図示関数

def draw_matching(matching, men_prefs, women_prefs):
    """固定順 (A-E 左, V-Z 右) で斜め線を描く"""
    fig, ax = plt.subplots(figsize=(4, 2.5), dpi=300)
    ax.axis('off')
    spacing = 0.18
    x_m, x_w = 0.25, 0.75
    icon_w, icon_h = int(30 * 1.0), int(45 * 0.5)  # 横幅をさらに拡大
    half_h = icon_h / 300  # 軽微オフセット (表示 dpi=300)
    for m, w in matching:
        y_m = -MEN.index(m) * spacing
        y_w = -WOMEN.index(w) * spacing
        # 線 (斜め or横)
        ax.plot([x_m, x_w], [y_m, y_w], 'k-', lw=1)
        # 男性アイコン
        m_path = os.path.join(IMAGE_DIR, f"{m}.png")
        if os.path.exists(m_path):
            img_m = Image.open(m_path).resize((icon_w, icon_h), Image.LANCZOS)
            ax.imshow(img_m, extent=(x_m-0.04, x_m+0.04, y_m-half_h, y_m+half_h))
        # 女性アイコン
        w_path = os.path.join(IMAGE_DIR, f"{w}.png")
        if os.path.exists(w_path):
            img_w = Image.open(w_path).resize((icon_w, icon_h), Image.LANCZOS)
            ax.imshow(img_w, extent=(x_w-0.04, x_w+0.04, y_w-half_h, y_w+half_h))
        # ラベル
        ax.text(x_m-0.04, y_m, f"({men_prefs[m].index(w)}) {m}", ha='right', va='center', fontsize=6)
        ax.text(x_w+0.04, y_w, f"{w} ({women_prefs[w].index(m)})", ha='left', va='center', fontsize=6)
    ax.set_xlim(0,1)
    ax.set_ylim(- (len(MEN)-1)*spacing - 0.2, spacing)
    return fig

# メイン表示

# 好み入力
st.subheader("現在の好み")
cols_m, cols_w = st.columns(2)
with cols_m:
    for m in MEN:
        prefs = st.multiselect(f"{m}", WOMEN, default=st.session_state.men_prefs[m], key=f"men_{m}")
        if len(prefs) == len(WOMEN): st.session_state.men_prefs[m] = prefs
with cols_w:
    for w in WOMEN:
        prefs = st.multiselect(f"{w}", MEN, default=st.session_state.women_prefs[w], key=f"women_{w}")
        if len(prefs) == len(MEN): st.session_state.women_prefs[w] = prefs

# 安定マッチング一覧
st.subheader("安定マッチング一覧")
stable_list = all_stable_matchings(st.session_state.men_prefs, st.session_state.women_prefs)
st.write(f"全 {len(stable_list)} 件 見つかりました。")

for i in range(0, len(stable_list), 2):
    col_pair = st.columns(2)
    for offset in range(2):
        if i+offset >= len(stable_list):
            continue
        match = stable_list[i+offset]
        total, ms, ws, diff, maxd = calculate_dissatisfaction(match, st.session_state.men_prefs, st.session_state.women_prefs)
        with col_pair[offset]:
            st.markdown(
                f"<div style='margin-bottom:-4px;font-size:14px'><b>{i+offset+1}. 不満度合計 {total} (男性 {ms}, 女性 {ws}), 差 {diff}, 最大 {maxd}</b></div>",
                unsafe_allow_html=True)
            st.pyplot(draw_matching(match, st.session_state.men_prefs, st.session_state.women_prefs))
