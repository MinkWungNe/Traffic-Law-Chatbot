import streamlit as st

st.set_page_config(page_title="Tra cứu văn bản luật", page_icon="📖", layout="wide")

st.title("📖 Tra Cứu Văn Bản Luật An Toàn Giao Thông")
st.markdown("Trang hỗ trợ xem và tìm kiếm nhanh các điều khoản trong kho dữ liệu văn bản pháp luật.")

search_query = st.text_input("🔍 Nhập từ khóa hoặc số hiệu văn bản (ví dụ: Nghị định 100, Luật GTĐB):")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📑 Danh mục văn bản đã nạp")
    st.info("Hệ thống hiện quản lý các văn bản luật hiện hành và văn bản hợp nhất mới nhất.")
    documents = [
        "1.1 - Luật TTATGT đường bộ 2024 (36/2024/QH15)",
        "1.6 - Luật Đường bộ 2024 (35/2024/QH15)",
        "2.1 - VBHN Xử phạt VPHC về TTATGT đường bộ (NĐ 168/2024/NĐ-CP)",
        "2.2 - Quy định phạt nguội (NĐ 135/2021/NĐ-CP)",
        "3.1 - VBHN Tuần tra, kiểm soát của CSGT (TT 73/2024/TT-BCA)",
        "3.4 - Quy định tốc độ và khoảng cách an toàn (TT 38/2024/TT-BGTVT)",
        "3.5 - Quy chuẩn báo hiệu đường bộ QCVN 41 (TT 51/2024/TT-BGTVT)"
    ]
    for doc in documents:
        st.write(f"- 📄 {doc}")

with col2:
    st.subheader("🔎 Kết quả tra cứu nhanh")
    if search_query:
        st.success(f"Đang tìm kiếm cho từ khóa: **{search_query}**")
        st.write("*(Tính năng tra cứu trực tiếp theo Vector Search đang được kết nối với ChromaDB)*")
    else:
        st.caption("Nhập từ khóa phía trên để bắt đầu tìm kiếm.")
