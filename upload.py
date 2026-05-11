import os
import time
from google.cloud import bigquery

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service-account-key.json")

if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise FileNotFoundError(
        f"ملف الاعتماد غير موجود: {SERVICE_ACCOUNT_FILE}\n"
        f"نزل ملف Service Account Key (JSON) من Google Cloud Console وحطه في نفس المجلد."
    )

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE
client = bigquery.Client()

# 2. هنا أهم خطوة: حطي الـ Table ID حقك من جوجل كلاود
# المسار يكون عادة بهذا الشكل: project_id.dataset_id.table_id
table_id = "smart-sand-project.sand_data.reading"

# بيانات تجريبية لإرسالها للسحابة
rows_to_insert = [
    {"temperature": 27.3, "timestamp": str(time.ctime())}
]

print("بدأنا العمل.. جاري إرسال أول نبضة للسحابة 🚀")

try:
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if not errors:
        print("مبروووك! أول معلومة من مشروعك وصلت للسحابة بنجاح.")
    else:
        print(f"فيه مشكلة بسيطة في الجدول: {errors}")
except Exception as e:
    print(f"فشل الاتصال: {e}")
