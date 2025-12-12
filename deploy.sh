#!/bin/bash

# Dừng script ngay nếu có lệnh bị lỗi
set -e

SERVICE_NAME="keepx-backend"
REGION="asia-southeast1"
ENV_FILE="env.yaml"

echo -e "\033[1;36m==========================================\033[0m"
echo -e "\033[1;36m🚀  BẮT ĐẦU QUY TRÌNH DEPLOY KEEPX\033[0m"
echo -e "\033[1;36m==========================================\033[0m"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "\033[1;31m❌ Lỗi: Không tìm thấy file $ENV_FILE\033[0m"
    exit 1
fi

echo -e "\n\033[1;33m📦 [1/2] Đang build và deploy Backend lên Cloud Run...\033[0m"
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --env-vars-file $ENV_FILE

echo -e "\n\033[1;33m🌐 [2/2] Đang deploy Firebase Hosting...\033[0m"
firebase deploy --only hosting

echo -e "\n\033[1;32m✅  HOÀN TẤT! Ứng dụng đã được cập nhật thành công.\033[0m"