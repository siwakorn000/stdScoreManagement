# from supabase import create_client, Client

# # ใส่ URL และ KEY ของคุณจากหน้า API Settings ใน Supabase
# SUPABASE_URL = "https://xaatsoinadrctwxrqqtk.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhhYXRzb2luYWRyY3R3eHJxcXRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk0NTA4OTUsImV4cCI6MjEwNTAyNjg5NX0.t3nXHNAuzXFRSgGpKIqtfeEyCBdgRSFuFOliA4oKA-s"

# try:
#     # สร้างการเชื่อมต่อ
#     supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
#     # ลองดึงข้อมูลจากตาราง subject มา 1 รายการเพื่อทดสอบ
#     response = supabase.table('subject').select('*').limit(1).execute()
    
#     print("✅ เชื่อมต่อ Supabase สำเร็จ!")
#     print("ข้อมูลตัวอย่างที่ดึงได้:", response.data)
    
# except Exception as e:
#     print("❌ เชื่อมต่อไม่สำเร็จ เกิดข้อผิดพลาด:")
#     print(e)