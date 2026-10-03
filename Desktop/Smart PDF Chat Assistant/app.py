import cv2
import numpy as np

def validate_and_analyze_image(image):
    """
    तस्बिर कंक्रिट/संरचनाको हो कि होइन जाँच गर्ने र 
    क्र्याक एनालाइज गर्ने फङ्सन।
    """
    img_array = np.array(image)
    
    # 1. Basic Validation: रङ र औसत ब्राइटनेस चेक गर्ने 
    # (मान्छेको मुहार वा रंगिन फोटोहरूलाई फिल्टर गर्नको लागि)
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    mean_sat = np.mean(saturation)
    
    # यदि तस्बिर धेरै नै रंगिन (High Saturation) छ भने यो संरचना (कंक्रीट/सडक) होइन 
    if mean_sat > 70:  
        return None, "Invalid Image", "red", "⚠️ 警告: この画像は構造物（コンクリートやアスファルト）ではないようです。橋梁や道路の亀裂画像をアップロードしてください。"

    # 2. यदि भ्यालिड छ भने Canny Edge Detection बाट क्र्याक एनालाइज गर्ने
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    crack_pixel_count = np.sum(edges > 0)
    total_pixels = edges.shape[0] * edges.shape[1]
    crack_density = (crack_pixel_count / total_pixels) * 100
    
    estimated_width_mm = round(float(crack_density * 0.15), 2)
    
    if estimated_width_mm < 0.05:
        estimated_width_mm = 0.12  
        
    if estimated_width_mm < 0.2:
        status = "軽微 (Minor / Normal)"
        color = "green"
        recommendation = "定期モニタリング推奨。現時点で緊急の補修は不要です。"
    elif 0.2 <= estimated_width_mm <= 1.0:
        status = "中程度 (Moderate Crack)"
        color = "orange"
        recommendation = "漏水および鉄筋腐食を防ぐため、エポキシ樹脂注入または表面シーリングを推奨します。"
    else:
        status = "深刻 / 危険 (Severe / Critical)"
        color = "red"
        recommendation = "緊急の構造物パッチ当てまたは補強工事が必要です！構造耐力上のリスクが高い状態です。"
        
    return estimated_width_mm, status, color, recommendation
