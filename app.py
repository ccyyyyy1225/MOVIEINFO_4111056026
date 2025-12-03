# app.py
import streamlit as st
import pandas as pd
import os

# --------------------------
# 頁面設定
# --------------------------
st.set_page_config(
    page_title="電影搜尋與資訊查詢",
    page_icon="🎬",
    layout="wide"
)

# --------------------------
# 標題與說明
# --------------------------
st.title("🎬 物聯網 HW3：電影搜尋與資訊查詢")

st.markdown("""
在下方輸入 **電影名稱關鍵字**，就可以查詢對應的電影資訊。  
若專案中有準備電影海報圖片，也會一併顯示出來 📷  
""")

# --------------------------
# 資料讀取
# --------------------------
@st.cache_data
def load_data():
    # 請確認 movie_info_from_10pages.csv 與 app.py 在同一層資料夾
    df = pd.read_csv("movie_info_from_10pages.csv")
    return df

try:
    df = load_data()
    st.success("✅ 已成功載入電影資料！")
except Exception as e:
    st.error("❌ 無法載入 `movie_info_from_10pages.csv`，請確認檔案是否存在於專案根目錄。")
    st.stop()

# --------------------------
# 嘗試尋找海報欄位
# --------------------------
POSTER_COL_CANDIDATES = ["Poster", "Poster_URL", "Image_URL", "Image", "Poster_Path", "PosterPath", "poster"]

poster_col = None
for c in POSTER_COL_CANDIDATES:
    if c in df.columns:
        poster_col = c
        break

if poster_col is None:
    st.info("ℹ️ 目前資料中未發現海報欄位（例如 Poster_URL、Image_URL），將只顯示文字資訊。")

# --------------------------
# 顯示原始資料預覽（可收合）
# --------------------------
with st.expander("👀 查看原始資料（前 10 筆）"):
    st.dataframe(df.head(10))

# --------------------------
# 關鍵字搜尋
# --------------------------
st.subheader("🔍 依電影名稱關鍵字搜尋")

keyword = st.text_input("請輸入電影名稱或關鍵字，例如：`泰坦尼克`、`Shawshank` 等", "")

if not keyword:
    st.warning("請先輸入關鍵字再進行搜尋。")
else:
    # 對 Title 欄位做不分大小寫的關鍵字搜尋
    if "Title" not in df.columns:
        st.error("資料中找不到 `Title` 欄位，請確認 CSV 欄位名稱。")
    else:
        result_df = df[df["Title"].astype(str).str.contains(keyword, case=False, na=False)]

        if result_df.empty:
            st.error("找不到符合關鍵字的電影，請嘗試其他關鍵字～")
        else:
            st.success(f"找到 {len(result_df)} 筆符合「{keyword}」的電影。")

            # 如果超過 1 筆，就讓使用者選一部
            if len(result_df) > 1:
                movie_titles = result_df["Title"].tolist()
                selected_title = st.selectbox("有多部電影符合，請選擇其中一部：", movie_titles)
                movie = result_df[result_df["Title"] == selected_title].iloc[0]
            else:
                movie = result_df.iloc[0]

            # --------------------------
            # 顯示電影詳細資訊
            # --------------------------
            st.markdown("---")
            st.subheader(f"🎞 選擇的電影：{movie['Title']}")

            col_info, col_poster = st.columns([2, 1])

            with col_info:
                # 資料欄位防禦性取值（避免沒有該欄位就當掉）
                categories = movie["Categories"] if "Categories" in movie.index else "（無資料）"
                region_duration = movie["Region_Duration"] if "Region_Duration" in movie.index else "（無資料）"
                release_date = movie["Release_Date"] if "Release_Date" in movie.index else "（無資料）"

                st.markdown("**📌 基本資訊**")
                st.write(f"- 🎭 類型：{categories}")
                st.write(f"- 🌍 地區／片長：{region_duration}")
                st.write(f"- 📅 上映日期：{release_date}")

                # 如果你之後想再顯示評分，可以把下面註解打開
                # if "Score" in movie.index:
                #     st.write(f"- ⭐ 評分：{movie['Score']}")

            # --------------------------
            # 顯示海報圖片（若有欄位）
            # --------------------------
            with col_poster:
                if poster_col is not None:
                    poster_val = str(movie[poster_col])
                    if poster_val and poster_val.lower() != "nan":
                        st.markdown("**🎨 海報**")

                        # 如果是網址
                        if poster_val.startswith("http://") or poster_val.startswith("https://"):
                            st.image(poster_val, use_container_width=True)
                        else:
                            # 視為專案中的檔案路徑，例如 "posters/1.jpg"
                            if os.path.exists(poster_val):
                                st.image(poster_val, use_container_width=True)
                            else:
                                st.info("找不到對應的海報圖片檔案，請確認路徑是否正確。")
                    else:
                        st.info("此電影目前沒有海報資料。")
                else:
                    st.info("此專案尚未設定海報欄位，僅顯示文字資訊。")

# --------------------------
# Footer
# --------------------------
st.markdown("---")
