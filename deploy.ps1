# --- CẤU HÌNH ---
$SERVICE_NAME = "keepx-backend"             
$REGION = "asia-southeast1"         
$ENV_FILE = "env.yaml"              

# --- BẮT ĐẦU ---
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀  BẮT ĐẦU QUY TRÌNH DEPLOY KEEPX" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Kiểm tra file môi trường
if (-not (Test-Path $ENV_FILE)) {
    Write-Error "❌ Lỗi: Không tìm thấy file '$ENV_FILE'. Hãy tạo nó trước khi deploy."
    exit 1
}

# 2. Deploy Backend (Cloud Run)
Write-Host "`n📦 [1/2] Đang build và deploy Backend lên Google Cloud Run..." -ForegroundColor Yellow
# Lệnh này sẽ build Dockerfile, đẩy lên GCR, và update service với biến môi trường từ env.yaml
gcloud run deploy $SERVICE_NAME `
    --source . `
    --region $REGION `
    --allow-unauthenticated `
    --env-vars-file $ENV_FILE

# Kiểm tra nếu lệnh gcloud thất bại thì dừng luôn
if ($LASTEXITCODE -ne 0) {
    Write-Error "`n❌ Lỗi: Deploy Backend thất bại. Đã hủy deploy Hosting."
    exit 1
}

# 3. Deploy Frontend (Firebase Hosting)
Write-Host "`n🌐 [2/2] Đang deploy Firebase Hosting..." -ForegroundColor Yellow
firebase deploy --only hosting

# Kiểm tra kết quả
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅  HOÀN TẤT! Ứng dụng đã được cập nhật thành công." -ForegroundColor Green
    Write-Host "👉  Truy cập tại: https://keepx-project.web.app" -ForegroundColor Green
} else {
    Write-Error "`n❌ Lỗi: Deploy Hosting thất bại."
}