import streamlit as st
from PIL import Image
from utils import validate_and_analyze_image

# Page Config
st.set_page_config(
    page_title="構造物亀裂自動解析・補修アドバイザー",
    page_icon="🌉",
    layout="centered"
)

# App Header
st.title("🌉 構造物亀裂自動解析・補修アドバイザー")
st.markdown("### 4年次 卒業研究 (Sotsugyo Kenkyu)")
st.write("道路や橋梁の亀裂画像をアップロードしてください。AIが構造物の有効性を検証し、亀裂の深刻度を自動測定して最適な補修方法を提案します。")

st.markdown("---")

# File Uploader
uploaded_file = st.file_uploader("橋梁や道路の亀裂画像を選択してください (JPG/PNG)...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # तस्बिर देखाउने
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_container_width=True)
    
    st.markdown("### 🔍 画像解析およびバリデーション中...")
    
    # बटन थिचेपछि एनालाइज गर्ने
    if st.button("亀裂解析を実行して補修レポートを表示"):
        with st.spinner("画像を検証し、深刻度を計算しています..."):
            # नयाँ भ्यालिडेशनसहितको फङ्सन कल गर्ने
            result = validate_and_analyze_image(image)
            
        # यदि भ्यालिडेशन फेल भयो भने (Invalid image)
        if result[0] is None:
            st.error(result[3]) # Error message
        else:
            width_mm, status, color, recommendation = result
            st.success("解析完了！")
            
            # रिजल्ट देखाउने बक्सहरू
            st.markdown("### 📊 評価レポート (Assessment Report)")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(label="推定亀裂幅 (Estimated Width)", value=f"{width_mm} mm")
            with col2:
                st.metric(label="深刻度ステータス (Severity)", value=status)
                
            # मर्मतको सिफारिस देखाउने
            st.markdown("### 🛠️ メンテナンス推奨事項 (Repair Advisor)")
            if color == "green":
                st.success(recommendation)
            elif color == "orange":
                st.warning(recommendation)
            else:
                st.error(recommendation)
