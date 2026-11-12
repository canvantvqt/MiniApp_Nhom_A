import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Trợ lý dinh dưỡng học đường",
    page_icon="🥗",
    layout="wide"
)

# =========================================================
# GIAO DIỆN – giữ nguyên logic xử lí dữ liệu của ứng dụng
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Be Vietnam Pro', 'Segoe UI', Arial, sans-serif;
}
.stApp {
    background: #f6f9f7;
    color: #20332b;
}
.block-container {
    max-width: 1440px;
    padding-top: 1.15rem;
    padding-bottom: 2rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #eef8f1 0%, #f8fbf8 100%);
    border-right: 1px solid #dcebe0;
}
[data-testid="stSidebar"] .stRadio label {
    font-weight: 600;
}
.hero {
    background: linear-gradient(115deg, #14543f, #197653 60%, #35a77d);
    padding: 1.5rem 1.8rem;
    border-radius: 22px;
    color: white;
    margin-bottom: 1.1rem;
    box-shadow: 0 10px 28px #14543f20;
}
.hero h1 {
    color: white !important;
    font-weight: 800;
    font-size: clamp(1.55rem, 3vw, 2.25rem);
    margin: .25rem 0;
}
.hero p {
    color: #e7f6ed;
    margin: 0;
}
.tag {
    display: inline-block;
    padding: .3rem .7rem;
    border: 1px solid #ffffff55;
    background: #ffffff20;
    border-radius: 99px;
    font-size: .78rem;
    font-weight: 800;
}
.section {
    font-size: 1.35rem;
    font-weight: 800;
    color: #14543f;
    margin: .4rem 0;
}
.sub {
    color: #66766e;
    margin-bottom: 1rem;
}
.card, .feature-card {
    background: white;
    border: 1px solid #e1ece4;
    border-radius: 17px;
    padding: 1.05rem 1.1rem;
    height: 100%;
    box-shadow: 0 4px 14px #1946300c;
}
.card h3, .feature-card h3 {
    color: #14543f;
    font-size: 1rem;
    margin: 0 0 .45rem;
    font-weight: 800;
}
.card p, .feature-card p {
    color: #53665b;
    margin: 0;
    font-size: .9rem;
    line-height: 1.55;
}
.feature-card {
    min-height: 170px;
    background: linear-gradient(145deg, #ffffff, #f4fbf6);
}
.feature-icon {
    font-size: 2.15rem;
    line-height: 1.25;
    margin-bottom: .55rem;
}
.eyebrow {
    display: inline-block;
    background: #e8f7ee;
    color: #146345;
    border: 1px solid #c9e8d5;
    padding: .32rem .75rem;
    border-radius: 99px;
    font-weight: 800;
    font-size: .78rem;
    margin-bottom: .55rem;
}
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    margin: .6rem 0 1rem;
}
.pill {
    background: #fff;
    border: 1px solid #dcebe2;
    color: #315b47;
    border-radius: 999px;
    padding: .4rem .75rem;
    font-size: .82rem;
    font-weight: 700;
}
.school-strip {
    background: linear-gradient(90deg, #fff1f6, #f0fbf4);
    border: 1px solid #f1dce5;
    border-radius: 16px;
    padding: .8rem 1rem;
    margin: .2rem 0 1rem;
    color: #34483e;
}
.school-strip strong {
    color: #a51e58;
}
.info-panel {
    background: #ffffff;
    border: 1px solid #dcebe2;
    border-left: 5px solid #35a77d;
    border-radius: 13px;
    padding: .85rem 1rem;
    margin: .5rem 0 1rem;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e1ece4;
    padding: .9rem 1rem;
    border-radius: 15px;
}
div[data-testid="stMetricValue"] {
    color: #14543f;
    font-weight: 800;
}
.stButton > button, .stDownloadButton > button,
.stFormSubmitButton > button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 2.6rem;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #e1ece4;
    border-radius: 12px;
    overflow: hidden;
}
div[data-testid="stTabs"] button {
    font-weight: 700;
}
.footer {
    text-align: center;
    color: #61736a;
    font-size: .84rem;
    line-height: 1.7;
    padding: 1rem .5rem;
}
.small-note {
    font-size: .8rem;
    color: #718078;
}
@media (max-width: 700px) {
    .block-container {padding-left: 1rem; padding-right: 1rem;}
    .school-strip {font-size: .83rem;}
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CÁC HẰNG SỐ VÀ QUY TẮC XỬ LÍ – GIỮ NGUYÊN
# =========================================================
COL_ID = "Mã HS"
COL_HEIGHT = "Chiều cao (cm)"
COL_WEIGHT = "Cân nặng (kg)"
COL_VEG = "Số ngày ăn rau xanh, rau quả (ngày/tuần)"
COL_COMBINED = "Số lần sử dụng thức ăn nhanh và đồ uống có đường (lần/tuần)"
REQUIRED_COLUMNS = [COL_ID, COL_HEIGHT, COL_WEIGHT, COL_VEG, COL_COMBINED]
VEG_TARGET_DAYS, COMBINED_MAX_TIMES = 5, 1
VALID_RANGES = {
    COL_HEIGHT: (100, 220),
    COL_WEIGHT: (20, 150),
    COL_VEG: (0, 7),
    COL_COMBINED: (0, 30)
}


def calculate_bmi(weight_kg, height_cm):
    if pd.isna(weight_kg) or pd.isna(height_cm) or height_cm <= 0 or weight_kg <= 0:
        return None
    return round(weight_kg / ((height_cm / 100) ** 2), 1)


def validate_record(row):
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
    for col in [COL_VEG, COL_COMBINED]:
        if not float(row[col]).is_integer():
            return "Kiểm tra lại giá trị"
    return "Hợp lệ"


def score_habit(veg_days, combined_times):
    if pd.isna(veg_days) or pd.isna(combined_times):
        return None, None, None, "Chưa đủ dữ liệu để tính điểm"
    vp = 1 if veg_days >= VEG_TARGET_DAYS else 0
    cp = 1 if combined_times <= COMBINED_MAX_TIMES else 0
    total = vp + cp
    group = "Thói quen tương đối tích cực" if total == 2 else "Cần cải thiện thói quen"
    return vp, cp, total, group


def prepare_dataframe(raw_df):
    missing = [c for c in REQUIRED_COLUMNS if c not in raw_df.columns]
    if missing:
        raise ValueError("Thiếu cột bắt buộc: " + ", ".join(missing))
    df = raw_df[REQUIRED_COLUMNS].copy()
    df[COL_ID] = df[COL_ID].astype("string").str.strip()
    for col in [COL_HEIGHT, COL_WEIGHT, COL_VEG, COL_COMBINED]:
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

    def bmi_group(v):
        if pd.isna(v):
            return "Chưa có BMI"
        if v < 16:
            return "Nhóm BMI minh họa 1"
        if v < 20:
            return "Nhóm BMI minh họa 2"
        return "Nhóm BMI minh họa 3"

    df["Nhóm BMI minh họa"] = df["BMI (tham khảo)"].apply(bmi_group)
    return df


def make_csv_download(df):
    return df.to_csv(index=False).encode("utf-8-sig")


def read_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx"):
        return pd.read_excel(
            uploaded_file,
            sheet_name="Du_lieu_khao_sat",
            header=3
        )
    if name.endswith(".xls"):
        return pd.read_excel(uploaded_file, header=3)
    raise ValueError("Chỉ hỗ trợ tệp .csv, .xlsx hoặc .xls.")


def heading(title, subtitle):
    st.markdown(
        f'<div class="section">{title}</div><div class="sub">{subtitle}</div>',
        unsafe_allow_html=True
    )


def show_home_hero():
    """Hiển thị ảnh minh họa trang chủ nếu ảnh nằm cạnh app.py."""
    image_path = Path(__file__).with_name("hero_nhom_a.png")
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.markdown(
            '<div class="hero">'
            '<span class="tag">MINI APP STEM · NHÓM A · LỚP 9C</span>'
            '<h1>🥗 Trợ lý dinh dưỡng học đường</h1>'
            '<p>Khỏe mạnh hôm nay – Vững vàng tương lai!</p>'
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# NHẬN DIỆN DỰ ÁN VÀ ĐIỀU HƯỚNG
# =========================================================
st.markdown(
    '<div class="school-strip">'
    '🎓 <strong>TRƯỜNG TH, THCS & THPT TRƯNG VƯƠNG</strong>'
    ' &nbsp; · &nbsp; DỰ ÁN STEM TIN HỌC 9'
    ' &nbsp; · &nbsp; <strong>NHÓM A – LỚP 9C</strong>'
    '</div>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("## 🥗 MINI APP · NHÓM A")
    st.markdown("**TRỢ LÝ DINH DƯỠNG HỌC ĐƯỜNG**")
    st.caption("LỚP 9C · DỮ LIỆU VÌ SỨC KHỎE HỌC ĐƯỜNG")
    st.divider()
    page = st.radio(
        "ĐIỀU HƯỚNG",
        [
            "Tổng quan",
            "Tính toán cá nhân",
            "Phân tích khảo sát",
            "Kiến thức & an toàn"
        ]
    )
    st.divider()
    st.caption("🌱 Sản phẩm STEM học tập")
    st.caption("Không thay thế tư vấn y tế.")


# =========================================================
# TRANG 1 – TỔNG QUAN
# =========================================================
if page == "Tổng quan":
    show_home_hero()
    heading(
        "🌿 Khám phá ứng dụng",
        "Từ dữ liệu khảo sát đến những lựa chọn dinh dưỡng tích cực mỗi ngày."
    )
    st.markdown(
        '<div class="pill-row">'
        '<span class="pill">🥗 Ăn uống cân bằng</span>'
        '<span class="pill">💧 Uống nước an toàn</span>'
        '<span class="pill">🍎 Tăng rau xanh, trái cây</span>'
        '<span class="pill">💗 Quan tâm sức khỏe đúng cách</span>'
        '</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)
    for col, icon, title, desc in [
        (
            a, "🧮", "Tính toán cá nhân",
            "Thực hành tính BMI tham khảo và kiểm tra các tiêu chí thói quen."
        ),
        (
            b, "📊", "Phân tích khảo sát",
            "Kiểm tra dữ liệu, thống kê theo quy tắc COUNTIF, SUMIF, IF và xem biểu đồ."
        ),
        (
            c, "🥦", "Kiến thức & an toàn",
            "Tìm hiểu dinh dưỡng cân bằng, thực phẩm an toàn và giới hạn của dữ liệu."
        )
    ]:
        with col:
            st.markdown(
                f'<div class="feature-card">'
                f'<div class="feature-icon">{icon}</div>'
                f'<h3>{title}</h3><p>{desc}</p></div>',
                unsafe_allow_html=True
            )

    st.markdown("### 🎯 Hai tiêu chí học tập của dự án")
    x, y = st.columns(2)
    x.metric("🥬 Rau xanh, rau quả", "≥ 5 ngày/tuần")
    y.metric("🥤 Thức ăn nhanh + đồ uống có đường", "≤ 1 lần/tuần")

    st.success(
        "Tổng điểm 0–2 là quy ước thực hành xử lí dữ liệu, "
        "không phải thang đo sức khỏe."
    )
    st.markdown(
        "**🧭 Quy trình:** 1. Nhập dữ liệu → 2. Kiểm tra → "
        "3. Xem thống kê, biểu đồ → 4. Tải kết quả."
    )
    st.caption(
        "Lưu ý: Không dùng BMI minh họa để kết luận thiếu cân, "
        "thừa cân hoặc béo phì ở học sinh."
    )


# =========================================================
# TRANG 2 – TÍNH TOÁN CÁ NHÂN
# =========================================================
elif page == "Tính toán cá nhân":
    heading(
        "🧮 Tính toán cá nhân",
        "Thực hành công thức và quy tắc tính điểm của dự án."
    )
    st.warning(
        "BMI ở trẻ em và vị thành niên cần được diễn giải theo tuổi và giới "
        "bởi người có chuyên môn. Kết quả tại đây chỉ phục vụ học tập."
    )

    with st.container(border=True):
        with st.form("personal_form"):
            st.markdown("#### 📋 Thông tin đầu vào")
            l, r = st.columns(2)
            with l:
                height = st.number_input(
                    "📏 Chiều cao (cm)", 100.0, 220.0, 155.0, 0.5
                )
                weight = st.number_input(
                    "⚖️ Cân nặng (kg)", 20.0, 150.0, 48.0, 0.5
                )
            with r:
                veg = st.number_input(
                    "🥬 Số ngày ăn rau xanh, rau quả (ngày/tuần)",
                    0, 7, 5, 1
                )
                combined = st.number_input(
                    "🍟 Số lần dùng thức ăn nhanh và đồ uống có đường (lần/tuần)",
                    0, 30, 1, 1
                )
            submitted = st.form_submit_button(
                "✨ Tính kết quả",
                type="primary",
                use_container_width=True
            )

    if submitted:
        bmi = calculate_bmi(weight, height)
        vp, cp, total, group = score_habit(veg, combined)

        st.markdown("#### 📌 Kết quả tính toán")
        m1, m2, m3 = st.columns(3)
        m1.metric("BMI tham khảo", bmi)
        m2.metric("Tổng điểm thói quen", f"{total}/2")
        m3.metric(
            "Kết quả theo quy ước",
            "Tương đối tích cực" if total == 2 else "Cần cải thiện"
        )

        with st.container(border=True):
            st.markdown("**🔎 Chi tiết tiêu chí**")
            q, w = st.columns(2)
            q.write(f"🥬 Điểm rau xanh/rau quả: **{vp}/1**")
            w.write(f"🥤 Điểm tiêu chí gộp: **{cp}/1**")

        if veg < VEG_TARGET_DAYS:
            st.info(
                "🥬 Gợi ý: Có thể bổ sung rau xanh và rau quả đa dạng "
                "trong các bữa ăn."
            )
        if combined > COMBINED_MAX_TIMES:
            st.info(
                "💧 Gợi ý: Thử giảm tần suất thức ăn nhanh/đồ uống có đường; "
                "ưu tiên nước lọc."
            )
        if total == 2:
            st.success(
                "🌱 Thông điệp: Tiếp tục duy trì lựa chọn ăn uống đa dạng "
                "và cân bằng."
            )
        st.caption("Không dùng kết quả để đánh giá hoặc so sánh cá nhân.")


# =========================================================
# TRANG 3 – PHÂN TÍCH KHẢO SÁT
# =========================================================
elif page == "Phân tích khảo sát":
    heading(
        "📊 Phân tích dữ liệu khảo sát",
        "Tải dữ liệu, kiểm tra chất lượng và khám phá kết quả."
    )

    with st.container(border=True):
        st.markdown("#### 📂 Tải dữ liệu khảo sát")
        st.caption(
            "Excel: đọc sheet Du_lieu_khao_sat, tiêu đề ở dòng 4. "
            "CSV: hàng đầu tiên là tên cột."
        )
        uploaded = st.file_uploader(
            "Chọn tệp Excel hoặc CSV",
            type=["xlsx", "xls", "csv"]
        )

    if uploaded is not None:
        try:
            result = prepare_dataframe(read_uploaded_file(uploaded))
            st.success(
                "Đã đọc tệp thành công. Hãy kiểm tra trạng thái dữ liệu "
                "trước khi diễn giải."
            )
            valid = result[result["Kiểm tra dữ liệu"] == "Hợp lệ"].copy()
            missing = int((result["Kiểm tra dữ liệu"] == "Thiếu dữ liệu").sum())
            invalid = int(
                (result["Kiểm tra dữ liệu"] == "Kiểm tra lại giá trị").sum()
            )
            empty = int(
                (result["Kiểm tra dữ liệu"] == "Chưa nhập dữ liệu").sum()
            )

            st.markdown("#### 🧪 Chất lượng dữ liệu")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tổng bản ghi", len(result))
            m2.metric("Hợp lệ", len(valid))
            m3.metric("Thiếu dữ liệu", missing)
            m4.metric("Cần kiểm tra", invalid + empty)

            with st.expander("🔍 Xem bảng dữ liệu đã xử lí"):
                st.dataframe(
                    result,
                    use_container_width=True,
                    hide_index=True
                )

            if not valid.empty:
                scored = valid[valid["Tổng điểm thói quen"].notna()].copy()
                counts = (
                    scored["Nhóm thói quen"]
                    .value_counts()
                    .rename_axis("Nhóm")
                    .reset_index(name="Số học sinh")
                )

                st.markdown("#### 📈 Kết quả thống kê")
                left, right = st.columns([1, 1.5])
                with left:
                    st.markdown("**👥 Tổng hợp theo nhóm**")
                    st.dataframe(
                        counts,
                        use_container_width=True,
                        hide_index=True
                    )
                with right:
                    fig = px.bar(
                        counts,
                        x="Nhóm",
                        y="Số học sinh",
                        color="Nhóm",
                        title="Phân bố bản ghi theo nhóm thói quen",
                        color_discrete_sequence=["#197653", "#83c9a5"]
                    )
                    fig.update_layout(
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        font=dict(family="Arial", color="#30483b"),
                        showlegend=False,
                        margin=dict(l=10, r=10, t=55, b=10)
                    )
                    fig.update_yaxes(gridcolor="#e8f0ea", title=None)
                    st.plotly_chart(fig, use_container_width=True)

                veg_sum = (
                    valid.groupby("Nhóm thói quen", dropna=False)[COL_VEG]
                    .sum()
                    .reset_index(name="Tổng ngày ăn rau")
                )
                st.markdown("#### 🥬 Tổng số ngày ăn rau theo nhóm")
                st.dataframe(
                    veg_sum,
                    use_container_width=True,
                    hide_index=True
                )

                with st.expander("📋 Bảng chéo minh họa"):
                    cross = pd.crosstab(
                        scored["Nhóm thói quen"],
                        scored["Nhóm BMI minh họa"],
                        margins=False
                    )
                    st.dataframe(cross, use_container_width=True)
                    st.caption(
                        "Chỉ mô tả phân bố cùng xuất hiện, "
                        "không chứng minh quan hệ nhân quả."
                    )
            else:
                st.warning("Chưa có dòng dữ liệu hợp lệ để thống kê.")

            st.download_button(
                "⬇️ Tải kết quả đã xử lí (CSV)",
                make_csv_download(result),
                "ket_qua_nhom_A.csv",
                "text/csv",
                use_container_width=True
            )

        except Exception as exc:
            st.error(f"Không thể xử lí tệp: {exc}")
            st.caption(
                "Kiểm tra tên sheet, hàng tiêu đề, tên cột "
                "và định dạng dữ liệu."
            )
    else:
        st.info(
            "Chưa tải tệp. Hãy chọn bảng khảo sát Excel hoặc CSV mẫu của Nhóm A."
        )


# =========================================================
# TRANG 4 – KIẾN THỨC & AN TOÀN
# =========================================================
elif page == "Kiến thức & an toàn":
    heading(
        "📚 Kiến thức & sử dụng có trách nhiệm",
        "Hiểu công thức, giới hạn dữ liệu và vai trò AI trong quá trình phát triển."
    )
    t1, t2, t3 = st.tabs(
        ["🧮 Công thức & quy ước", "🤖 Vai trò của AI", "🛡️ An toàn dữ liệu"]
    )

    with t1:
        st.markdown("#### Công thức minh họa")
        st.code(
            "BMI = cân nặng (kg) / (chiều cao (m) ** 2)\n"
            "Điểm rau = 1 nếu số ngày ăn rau >= 5; ngược lại = 0\n"
            "Điểm tiêu chí gộp = 1 nếu số lần <= 1; ngược lại = 0\n"
            "Tổng điểm = điểm rau + điểm tiêu chí gộp",
            language="python"
        )
        st.info(
            "Các ngưỡng 5 ngày và 1 lần là quy ước học tập, "
            "không phải tiêu chuẩn y tế."
        )

    with t2:
        st.write(
            "AI hỗ trợ gợi ý giao diện, tạo bản nháp mã, giải thích câu lệnh "
            "và hỗ trợ tìm lỗi trong giai đoạn phát triển."
        )
        st.success(
            "Khi chạy, ứng dụng tính toán bằng Python theo quy tắc đã lập trình; "
            "không gọi API AI."
        )

    with t3:
        st.write(
            "- Không dùng BMI hoặc điểm 0–2 để chẩn đoán, xếp loại hay gắn nhãn học sinh.\n"
            "- BMI trẻ em/vị thành niên cần diễn giải theo tuổi và giới bởi người có chuyên môn.\n"
            "- Không nhập họ tên, số điện thoại, địa chỉ hoặc dữ liệu nhận dạng cá nhân.\n"
            "- Chỉ dùng dữ liệu khảo sát khi đã được phép; lưu trữ và chia sẻ có trách nhiệm.\n"
            "- Dữ liệu mô phỏng phải được ghi rõ là dữ liệu mô phỏng.\n"
            "- Thống kê mô tả không chứng minh quan hệ nguyên nhân – kết quả."
        )
        st.warning("Ứng dụng là sản phẩm học tập, không thay thế tư vấn y tế.")


# =========================================================
# CHÂN TRANG
# =========================================================
st.divider()
st.markdown(
    '<div class="footer">'
    '🥗 <b>DỮ LIỆU VÌ SỨC KHỎE HỌC ĐƯỜNG</b><br>'
    'Mini App STEM – Tin học 9 · <b>Nhóm A – Lớp 9C</b><br>'
    'Dữ liệu trung thực · Xử lí đúng · Truyền thông có trách nhiệm<br>'
    '<span class="small-note">TVS · Sản phẩm học tập, không thay thế tư vấn y tế</span>'
    '</div>',
    unsafe_allow_html=True
)

