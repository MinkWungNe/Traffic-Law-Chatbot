import streamlit as st

st.set_page_config(page_title="Đánh giá & Benchmark RAG", page_icon="📊", layout="wide")

st.title("📊 Báo Cáo Đánh Giá & Thử Nghiệm Mô Hình RAG")
st.markdown("Trang thống kê kết quả benchmark trên tập dữ liệu câu hỏi thực tế.")

col1, col2, col3 = st.columns(3)
col1.metric("Tổng số câu hỏi đánh giá", "734 câu", "+100% hoàn thành")
col2.metric("Độ chính xác truy xuất (Recall@3)", "88.5%", "+5.2%")
col3.metric("Điểm tương đồng ngữ nghĩa (Cosine)", "0.86", "+0.04")

st.divider()

st.subheader("📋 Chi tiết kết quả kiểm thử mẫu")
st.dataframe([
    {"ID": 507, "Chủ đề": "Trang phục thanh tra giao thông", "Trạng thái": "Đạt", "Điểm RAG": 0.92},
    {"ID": 508, "Chủ đề": "Chứng minh nhân dân/Căn cước thanh tra", "Trạng thái": "Đạt", "Điểm RAG": 0.95},
    {"ID": 510, "Chủ đề": "Dừng phương tiện khi có dấu hiệu vi phạm", "Trạng thái": "Đạt", "Điểm RAG": 0.89},
    {"ID": 526, "Chủ đề": "Kiểm tra xe đưa đón học sinh", "Trạng thái": "Đạt", "Điểm RAG": 0.91},
], use_container_width=True)
