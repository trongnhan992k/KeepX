import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.core.cache import cache

try:
    cache.clear()
    print("Đã xóa cache thành công!")
except Exception as e:
    print(f"Có lỗi xảy ra: {e}")