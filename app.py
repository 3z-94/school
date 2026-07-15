import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import base64

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة الطلاب الذكي", layout="wide")
st.write("""
<style>
    body { text-align: right; direction: rtl; }
    .stMarkdown, .stButton, .stSelectbox { text-align: right; direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 النظام الرقمي الذكي لإدارة ومتابعة الطلاب")

# القوائم الأساسية
levels = [
    "الصف الثالث الابتدائي", "الصف الرابع الابتدائي", "الصف الخامس الابتدائي",
    "الصف الأول متوسط", "الصف الثاني متوسط", "الصف الثالث متوسط"
]

# محاكاة قاعدة بيانات للطلاب
if 'students_db' not in st.session_state:
    st.session_state.students_db = pd.DataFrame([
        {"الرقم": 1, "الاسم": "أحمد علي", "الفصل": "الصف الثالث الابتدائي", "حضور": 15, "غياب": 2, "المشاركة": 9, "الواجبات": 10, "المشاريع": 8, "الاختبارات": 18},
        {"الرقم": 2, "الاسم": "محمد سعود", "الفصل": "الصف الثالث الابتدائي", "حضور": 17, "غياب": 0, "المشاركة": 10, "الواجبات": 9, "المشاريع": 9, "الاختبارات": 19},
        {"الرقم": 3, "الاسم": "خالد عبد الله", "الفصل": "الصف الأول متوسط", "حضور": 14, "غياب": 3, "المشاركة": 8, "الواجبات": 7, "المشاريع": 10, "الاختبارات": 15},
    ])

# القائمة الجانبية للتحكم
st.sidebar.header("⚙️ لوحة التحكم والإدخال")
selected_level = st.sidebar.selectbox("اختر الصف الدراسي:", levels)
hijri_date = st.sidebar.text_input("التاريخ الهجري الحالي:", "15-07-1447 هـ")

# تصفية الطلاب حسب الصف الدراسي
df_filtered = st.session_state.students_db[st.session_state.students_db["الفصل"] == selected_level].copy()

# حساب الدرجة النهائية التلقائية من 60
# الحضور والغياب يحسب ديناميكياً (مثال: خصم درجة عن كل يوم غياب من أصل 10 درجات)
df_filtered["درجة الحضور (10)"] = df_filtered["غياب"].apply(lambda x: max(0, 10 - x))
df_filtered["المجموع الكلي (60)"] = (
    df_filtered["درجة الحضور (10)"] + 
    df_filtered["المشاركة"] + 
    df_filtered["الواجبات"] + 
    df_filtered["المشاريع"] + 
    df_filtered["الاختبارات"]
)

# عرض البيانات والإحصائيات
st.subheader(f"📊 كشف درجات وإحصائيات: {selected_level}")
st.caption(f"تاريخ الرصد الهجري: {hijri_date}")

# عرض جدول البيانات التفاعلي
st.dataframe(df_filtered[["الرقم", "الاسم", "حضور", "غياب", "درجة الحضور (10)", "المشاركة", "الواجبات", "المشاريع", "الاختبارات", "المجموع الكلي (60)"]], use_container_width=True)

# قسم الإحصائيات الذكية للغياب والحضور
st.subheader("📈 التحليلات الذكية للفصل")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("إجمالي أيام غياب الفصل", int(df_filtered["غياب"].sum()))
with col2:
    st.metric("إجمالي أيام حضور الفصل", int(df_filtered["حضور"].sum()))
with col3:
    st.metric("متوسط درجات الفصل الدراسي", f"{df_filtered['المجموع الكلي (60)'].mean():.2f} / 60")

# رصد سريع لطالب جديد أو تعديل غياب
st.sidebar.subheader("📝 رصد سريع / غياب يومي")
student_name = st.sidebar.selectbox("اختر اسم الطالب للتعديل:", df_filtered["الاسم"].tolist() if not df_filtered.empty else ["لا يوجد طلاب"])
status = st.sidebar.radio("حالة الطالب اليوم:", ["حاضر", "غائب"])

if st.sidebar.button("تحديث السجل اليومي"):
    idx = st.session_state.students_db[st.session_state.students_db["الاسم"] == student_name].index
    if not idx.empty:
        if status == "حاضر":
            st.session_state.students_db.loc[idx, "حضور"] += 1
        else:
            st.session_state.students_db.loc[idx, "غياب"] += 1
        st.success(f"تم تحديث سجل الطالب {student_name} بنجاح!")
        st.rerun()

# توليد ملف PDF للتقرير الشهري والاحصائيات
def generate_pdf(data, level, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # عنوان التقرير (ملاحظة: لتدعيم العربية في FPDF الحقيقية يفضل استخدام خيار الكود الموجه للـ UTF-8 أو مكتبة ReportLab)
    pdf.cell(200, 10, txt=f"Monthly Report - {level}", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Hijri Date: {date}", ln=2, align="C")
    pdf.cell(200, 10, txt="--------------------------------------------------", ln=3, align="C")
    
    for index, row in data.iterrows():
        text = f"ID: {row['الرقم']} | Name: {row['الاسم']} | Attendance: {row['حضور']} | Absence: {row['غياب']} | Total Grade: {row['المجموع الكلي (60)']}/60"
        pdf.cell(200, 10, txt=text, ln=index+4, align="L")
        
    return pdf.output(dest="S").encode("latin-1")

st.subheader("🖨️ التصدير والتقارير الشهرية")
if st.button("إنشاء التقرير الشهري وإحصائية الفصل"):
    pdf_bytes = generate_pdf(df_filtered, selected_level, hijri_date)
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="تقرير_{selected_level}_{hijri_date}.pdf" style="padding:10px; background-color:#4CAF50; color:white; border-radius:5px; text-decoration:none;">📥 تحميل إحصائية الفصل PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
