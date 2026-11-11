# ============================================================
# MINI APP: TRỢ LÝ DINH DƯỠNG HỌC ĐƯỜNG
# Dự án STEM "Dữ liệu vì sức khỏe học đường" - Nhóm A
# Công nghệ: Python + Streamlit + Pandas + Plotly
#
# LƯU Ý VỀ AI:
# AI chỉ hỗ trợ nhóm trong giai đoạn phát triển mã nguồn.
# Khi chạy, ứng dụng dùng các quy tắc và phép tính Python,
# KHÔNG gọi API AI và KHÔNG tự chẩn đoán sức khỏe.
# ============================================================

from io import BytesIO
import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------- 1. CẤU HÌNH TRANG ----------------------
# set_page_config phải được gọi trước các lệnh hiển thị Streamlit.
st.set_page_config(
    page_title="Trợ lý dinh dưỡng học đường",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------- 2. HẰNG SỐ DÙNG CHUNG -----------------
# Tập trung tên cột tại một nơi để dễ sửa khi cấu trúc Excel thay đổi.
COL_ID = "Mã HS"
COL_HEIGHT = "Chiều cao (cm)"
COL_WEIGHT = "Cân nặng (kg)"
COL_VEG = "Số ngày ăn rau xanh, rau quả (ngày/tuần)"
COL_COMBINED = "Số lần sử dụng thức ăn nhanh và đồ uống có đường (lần/tuần)"

REQUIRED_COLUMNS = [COL_ID, COL_HEIGHT, COL_WEIGHT, COL_VEG, COL_COMBINED]

# Quy ước học tập của dự án (không phải thang đánh giá y tế).
VEG_TARGET_DAYS = 5
COMBINED_MAX_TIMES = 1

# Khoảng kỹ thuật để phát hiện lỗi nhập liệu, không phải giới hạn sức khỏe.
VALID_RANGES = {
    COL_HEIGHT: (100, 220),
    COL_WEIGHT: (20, 150),
    COL_VEG: (0, 7),
    COL_COMBINED: (0, 30),
}


# ---------------------- 3. HÀM XỬ LÝ DỮ LIỆU -------------------
def calculate_bmi(weight_kg, height_cm):
    """Tính BMI tham khảo. Trả về None nếu thiếu/sai dữ liệu."""
    if pd.isna(weight_kg) or pd.isna(height_cm):
        return None
    if height_cm <= 0 or weight_kg <= 0:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def validate_record(row):
    """
    Kiểm tra dữ liệu đầu vào.
    Kết quả: Hợp lệ / Thiếu dữ liệu / Kiểm tra lại giá trị.
    """
    values = [row.get(c) for c in REQUIRED_COLUMNS]
    if all(pd.isna(v) or str(v).strip() == "" for v in values):
        return "Chưa nhập dữ liệu"

    for col in REQUIRED_COLUMNS:
        value = row.get(col)
        if pd.isna(value) or str(value).strip() == "":
            return "Thiếu dữ liệu"

    for col, (low, high) in VALID_RANGES.items():
        try:
            value = float(row[col])
        except (TypeError, ValueError):
            return "Kiểm tra lại giá trị"
        if value < low or value > high:
            return "Kiểm tra lại giá trị"

    # Các biến khảo sát tần suất và ngày phải là số nguyên.
    for col in [COL_VEG, COL_COMBINED]:
        if float(row[col]).is_integer() is False:
            return "Kiểm tra lại giá trị"

    return "Hợp lệ"


def score_habit(veg_days, combined_times):
    """
    Chấm 2 tiêu chí theo quy ước đã thống nhất:
    - Rau xanh/rau quả >= 5 ngày/tuần: 1 điểm.
    - Thức ăn nhanh + đồ uống có đường <= 1 lần/tuần: 1 điểm.
    Không tính nếu thiếu một trong hai biến.
    """
    if pd.isna(veg_days) or pd.isna(combined_times):
        return None, None, None, "Chưa đủ dữ liệu để tính điểm"

    veg_point = 1 if veg_days >= VEG_TARGET_DAYS else 0
    combined_point = 1 if combined_times <= COMBINED_MAX_TIMES else 0
    total = veg_point + combined_point
    group = "Thói quen tương đối tích cực" if total == 2 else "Cần cải thiện thói quen"
    return veg_point, combined_point, total, group


def prepare_dataframe(raw_df):
    """
    Chuẩn hóa bảng tải lên:
    - Kiểm tra đủ 5 cột khảo sát.
    - Ép kiểu số ở các cột số.
    - Tính BMI, điểm và nhóm.
    - Giữ dữ liệu gốc, không tự điền giá trị thiếu.
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in raw_df.columns]
    if missing:
        raise ValueError("Thiếu cột bắt buộc: " + ", ".join(missing))

    df = raw_df[REQUIRED_COLUMNS].copy()
    df[COL_ID] = df[COL_ID].astype("string").str.strip()

    numeric_cols = [COL_HEIGHT, COL_WEIGHT, COL_VEG, COL_COMBINED]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["BMI (tham khảo)"] = df.apply(
        lambda r: calculate_bmi(r[COL_WEIGHT], r[COL_HEIGHT]), axis=1
    )
    df["Kiểm tra dữ liệu"] = df.apply(validate_record, axis=1)

    scored = df.apply(
        lambda r: score_habit(r[COL_VEG], r[COL_COMBINED]), axis=1
    )
    df["Điểm rau xanh"] = [x[0] for x in scored]
    df["Điểm tiêu chí gộp"] = [x[1] for x in scored]
    df["Tổng điểm thói quen"] = [x[2] for x in scored]
    df["Nhóm thói quen"] = [x[3] for x in scored]

    # Nhóm BMI chỉ để minh họa kỹ thuật IF/COUNTIF, không phải phân loại y tế.
    def illustrative_bmi_group(value):
        if pd.isna(value):
            return "Chưa có BMI"
        if value < 16:
            return "Nhóm BMI minh họa 1"
        if value < 20:
            return "Nhóm BMI minh họa 2"
        return "Nhóm BMI minh họa 3"

    df["Nhóm BMI minh họa"] = df["BMI (tham khảo)"].apply(illustrative_bmi_group)
    return df


def make_csv_download(df):
    """Tạo nội dung CSV UTF-8 có BOM để mở thuận tiện bằng Excel tiếng Việt."""
    return df.to_csv(index=False).encode("utf-8-sig")


def read_uploaded_file(uploaded_file):
    """Đọc CSV hoặc Excel; không yêu cầu kết nối cơ sở dữ liệu."""
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Chỉ hỗ trợ tệp .csv, .xlsx hoặc .xls.")


# ---------------------- 4. GIAO DIỆN CHUNG ---------------------
st.title("🥗 Trợ lý dinh dưỡng học đường")
st.caption("Mini App STEM – Dự án “Dữ liệu vì sức khỏe học đường” | Nhóm A")

with st.sidebar:
    st.header("Điều hướng")
    page = st.radio(
        "Chọn chức năng",
        ["Giới thiệu", "Tính toán cá nhân", "Phân tích dữ liệu khảo sát", "Kiến thức & an toàn"],
    )
    st.divider()
    st.caption("Phiên bản học tập – không thay thế tư vấn y tế.")

# ---------------------- 5. TRANG GIỚI THIỆU --------------------
if page == "Giới thiệu":
    st.subheader("Từ dữ liệu đến thông điệp dinh dưỡng")
    st.write(
        "Ứng dụng minh họa cách nhập dữ liệu, tính toán theo quy ước học tập, "
        "tổng hợp kết quả và truyền tải thông điệp tích cực về thói quen ăn uống."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Nhóm khảo sát 5 thông tin")
        for item in REQUIRED_COLUMNS:
            st.write("• " + item)
    with c2:
        st.markdown("### Hai tiêu chí học tập")
        st.write(f"• Ăn rau xanh/rau quả: từ {VEG_TARGET_DAYS} ngày/tuần trở lên.")
        st.write(f"• Thức ăn nhanh và đồ uống có đường: không quá {COMBINED_MAX_TIMES} lần/tuần.")
    st.info(
        "Điểm 0–2 là quy ước của dự án để thực hành xử lí dữ liệu, "
        "không phải thang đo hay kết luận về tình trạng sức khỏe."
    )
    st.markdown("### Quy trình sử dụng")
    st.write("1. Nhập thử thông tin cá nhân hoặc chọn tệp khảo sát.")
    st.write("2. Kiểm tra dữ liệu trước khi xem kết quả.")
    st.write("3. Đọc bảng thống kê và thông điệp gợi ý.")
    st.write("4. Tải kết quả để phục vụ báo cáo học tập.")

# ---------------------- 6. TÍNH TOÁN CÁ NHÂN -------------------
elif page == "Tính toán cá nhân":
    st.subheader("Thử tính chỉ số và điểm thói quen")
    st.warning(
        "Chỉ dùng cho mục đích học tập. BMI ở trẻ em/vị thành niên cần được "
        "diễn giải theo tuổi và giới; ứng dụng không chẩn đoán."
    )
    with st.form("personal_form"):
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Chiều cao (cm)", min_value=100.0, max_value=220.0, value=155.0, step=0.5)
            weight = st.number_input("Cân nặng (kg)", min_value=20.0, max_value=150.0, value=48.0, step=0.5)
        with col2:
            veg = st.number_input("Số ngày ăn rau xanh, rau quả (ngày/tuần)", min_value=0, max_value=7, value=5, step=1)
            combined = st.number_input(
                "Số lần sử dụng thức ăn nhanh và đồ uống có đường (lần/tuần)",
                min_value=0, max_value=30, value=1, step=1
            )
        submitted = st.form_submit_button("Tính kết quả", type="primary")

    if submitted:
        bmi = calculate_bmi(weight, height)
        vp, cp, total, group = score_habit(veg, combined)
        a, b, c = st.columns(3)
        a.metric("BMI tham khảo", bmi)
        b.metric("Tổng điểm thói quen", f"{total}/2")
        c.metric("Nhóm theo quy ước", "Tương đối tích cực" if total == 2 else "Cần cải thiện")
        st.markdown("#### Kết quả từng tiêu chí")
        st.write(f"- Điểm rau xanh/rau quả: **{vp}**")
        st.write(f"- Điểm tiêu chí gộp: **{cp}**")
        if veg < VEG_TARGET_DAYS:
            st.info("Gợi ý: Có thể bổ sung rau xanh và rau quả đa dạng trong các bữa ăn.")
        if combined > COMBINED_MAX_TIMES:
            st.info("Gợi ý: Thử giảm tần suất thức ăn nhanh/đồ uống có đường; ưu tiên nước lọc và lựa chọn phù hợp.")
        if total == 2:
            st.success("Thông điệp: Tiếp tục duy trì những lựa chọn ăn uống đa dạng và cân bằng.")
        st.caption("Kết quả theo quy ước học tập; không dùng để đánh giá hoặc so sánh cá nhân.")

# ---------------------- 7. PHÂN TÍCH TỆP KHẢO SÁT -------------
elif page == "Phân tích dữ liệu khảo sát":
    st.subheader("Tải lên và phân tích bảng khảo sát")
    st.write("Tệp cần có đúng 5 cột khảo sát như mẫu Excel của Nhóm A.")
    uploaded = st.file_uploader("Chọn tệp Excel hoặc CSV", type=["xlsx", "xls", "csv"])
    if uploaded is not None:
        try:
            raw = read_uploaded_file(uploaded)
            result = prepare_dataframe(raw)
            st.success("Đã đọc tệp. Hãy kiểm tra trạng thái dữ liệu trước khi diễn giải.")
            st.dataframe(result, use_container_width=True, hide_index=True)

            valid = result[result["Kiểm tra dữ liệu"] == "Hợp lệ"].copy()
            missing_count = int((result["Kiểm tra dữ liệu"] == "Thiếu dữ liệu").sum())
            invalid_count = int((result["Kiểm tra dữ liệu"] == "Kiểm tra lại giá trị").sum())
            not_entered = int((result["Kiểm tra dữ liệu"] == "Chưa nhập dữ liệu").sum())

            st.markdown("### Kiểm tra chất lượng dữ liệu")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tổng dòng", len(result))
            m2.metric("Hợp lệ", len(valid))
            m3.metric("Thiếu dữ liệu", missing_count)
            m4.metric("Cần kiểm tra", invalid_count + not_entered)

            if not valid.empty:
                st.markdown("### Thống kê thói quen – chỉ trên dòng hợp lệ")
                scored = valid[valid["Tổng điểm thói quen"].notna()].copy()
                group_counts = scored["Nhóm thói quen"].value_counts().rename_axis("Nhóm").reset_index(name="Số học sinh")
                st.dataframe(group_counts, use_container_width=True, hide_index=True)

                chart = px.bar(
                    group_counts, x="Nhóm", y="Số học sinh", color="Nhóm",
                    title="Số bản ghi theo nhóm thói quen"
                )
                st.plotly_chart(chart, use_container_width=True)

                veg_sum = valid.groupby("Nhóm thói quen", dropna=False)[COL_VEG].sum().reset_index(name="Tổng ngày ăn rau")
                st.markdown("### Tổng số ngày ăn rau theo nhóm")
                st.dataframe(veg_sum, use_container_width=True, hide_index=True)

                # Bảng chéo chỉ mô tả phân bố; không suy ra quan hệ nhân quả.
                cross = pd.crosstab(
                    scored["Nhóm thói quen"],
                    scored["Nhóm BMI minh họa"],
                    margins=False
                )
                st.markdown("### Bảng chéo minh họa")
                st.dataframe(cross, use_container_width=True)
                st.caption("Bảng chéo chỉ mô tả phân bố cùng xuất hiện, không chứng minh quan hệ nhân quả.")
            else:
                st.warning("Chưa có dòng dữ liệu hợp lệ để thống kê. Hãy kiểm tra tệp và dữ liệu đầu vào.")

            st.download_button(
                "Tải kết quả đã xử lí (CSV)",
                data=make_csv_download(result),
                file_name="ket_qua_nhom_A.csv",
                mime="text/csv",
            )
        except Exception as exc:
            st.error(f"Không thể xử lí tệp: {exc}")
            st.write("Hãy kiểm tra tên cột, định dạng tệp và kiểu dữ liệu.")
    else:
        st.info("Chưa tải tệp. Có thể dùng file Excel Nhóm A hoặc CSV mẫu trong thư mục data/.")

# ---------------------- 8. KIẾN THỨC, GIỚI HẠN VÀ AN TOÀN -----
elif page == "Kiến thức & an toàn":
    st.subheader("Hiểu đúng kết quả – sử dụng có trách nhiệm")
    st.markdown("### Công thức và quy ước")
    st.code(
        "BMI = cân nặng (kg) / (chiều cao (m) ** 2)\n"
        "Điểm rau = 1 nếu số ngày ăn rau >= 5; ngược lại = 0\n"
        "Điểm tiêu chí gộp = 1 nếu số lần <= 1; ngược lại = 0\n"
        "Tổng điểm = điểm rau + điểm tiêu chí gộp",
        language="python",
    )
    st.markdown("### Vai trò của AI trong dự án")
    st.write(
        "AI hỗ trợ học sinh và giáo viên trong giai đoạn phát triển: gợi ý giao diện, "
        "tạo bản nháp mã, giải thích câu lệnh và hỗ trợ tìm lỗi. Khi chạy, ứng dụng "
        "thực hiện phép tính bằng Python theo quy tắc đã lập trình; không gọi API AI."
    )
    st.markdown("### Giới hạn và nguyên tắc an toàn")
    st.write("- Không dùng BMI hoặc điểm 0–2 để chẩn đoán, xếp loại hay gắn nhãn học sinh.")
    st.write("- BMI trẻ em/vị thành niên cần diễn giải theo tuổi và giới bởi người có chuyên môn.")
    st.write("- Không nhập họ tên, số điện thoại, địa chỉ hoặc dữ liệu nhận dạng cá nhân.")
    st.write("- Chỉ dùng dữ liệu khảo sát khi đã được phép; lưu trữ và chia sẻ có trách nhiệm.")
    st.write("- Dữ liệu mô phỏng phải được ghi rõ là dữ liệu mô phỏng.")
    st.write("- Thống kê mô tả không chứng minh nguyên nhân – kết quả.")
    st.info("Ứng dụng là sản phẩm học tập và truyền thông cộng đồng, không thay thế tư vấn của nhân viên y tế.")

# ---------------------- 9. CHÂN TRANG --------------------------
st.divider()
st.caption("Sản phẩm STEM học tập của Nhóm A | Dữ liệu trung thực – xử lí đúng – truyền thông có trách nhiệm.")
