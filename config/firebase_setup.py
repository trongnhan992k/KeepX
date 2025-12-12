import os
import firebase_admin
from firebase_admin import credentials

def initialize_firebase(base_dir):
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred_path = os.path.join(base_dir, "serviceAccountKey.json")
    
    bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET", "keepx-note.firebasestorage.app")

    try:
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            app = firebase_admin.initialize_app(
                cred, {"storageBucket": bucket_name}
            )
            print(f"Firebase khởi tạo từ file Key: {cred_path} | Bucket: {bucket_name}")
        else:
            print(
                "Không tìm thấy serviceAccountKey.json, thử khởi tạo bằng Default Credentials (Cloud Run)..."
            )
            app = firebase_admin.initialize_app(
                options={"storageBucket": bucket_name}
            )
            print(f"Firebase khởi tạo thành công bằng Default Credentials. | Bucket: {bucket_name}")

        return app

    except Exception as e:
        print(f"Lỗi khởi tạo Firebase: {e}")
        raise e