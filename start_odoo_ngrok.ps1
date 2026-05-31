# Script khoi dong Odoo 19 va Ngrok su dung .NET Process Start
# Duoc tao boi Antigravity AI agent

Write-Host "==============================================" -ForegroundColor DarkCyan
Write-Host "     KHOI DONG HE THONG ODOO 19 & NGROK       " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor DarkCyan

# 1. Stop existing processes
Write-Host "[1/4] Dang dung cac tien trinh Odoo/Ngrok cu..." -ForegroundColor Yellow
$killedPython = Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue -PassThru
$killedNgrok = Stop-Process -Name "ngrok" -Force -ErrorAction SilentlyContinue -PassThru

if ($killedPython) { Write-Host "  -> Da tat $($killedPython.Count) tien trinh Python." -ForegroundColor Gray }
if ($killedNgrok) { Write-Host "  -> Da tat $($killedNgrok.Count) tien trinh Ngrok." -ForegroundColor Gray }

Start-Sleep -Seconds 2

# 2. Start Odoo using .NET Process Start to breakaway from Job Object
Write-Host "[2/4] Dang khoi dong Odoo 19..." -ForegroundColor Cyan
$env:PATH += ";C:\Program Files\Git\cmd;C:\Users\PhucHoang\AppData\Local\Programs\Python\Python312;C:\Users\PhucHoang\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\PostgreSQL\18\bin;C:\Program Files\nodejs"

$odooPsi = New-Object System.Diagnostics.ProcessStartInfo
$odooPsi.FileName = "d:\Odoo 19\venv\Scripts\python.exe"
$odooPsi.Arguments = "odoo-bin -c ..\odoo.conf"
$odooPsi.WorkingDirectory = "d:\Odoo 19\odoo"
$odooPsi.UseShellExecute = $true
$odooPsi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized
[System.Diagnostics.Process]::Start($odooPsi) | Out-Null

# 3. Start Ngrok using .NET Process Start to breakaway from Job Object
Write-Host "[3/4] Dang khoi dong Ngrok tunnel..." -ForegroundColor Cyan
$ngrokPsi = New-Object System.Diagnostics.ProcessStartInfo
$ngrokPsi.FileName = "ngrok"
$ngrokPsi.Arguments = "http 8069 --domain=buckskin-foil-procedure.ngrok-free.dev"
$ngrokPsi.UseShellExecute = $true
$ngrokPsi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized
[System.Diagnostics.Process]::Start($ngrokPsi) | Out-Null

# 4. Wait & Check
Write-Host "[4/4] Dang cho Odoo va Ngrok thiet lap trang thai..." -ForegroundColor Yellow
for ($i = 5; $i -gt 0; $i--) {
    Write-Host "  -> Con $i giay..." -ForegroundColor Gray
    Start-Sleep -Seconds 1
}

# Retrieve ngrok tunnel info
try {
    $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5
    if ($tunnels -and $tunnels.tunnels) {
        Write-Host "`n==============================================" -ForegroundColor Green
        Write-Host "       KHOI DONG THANH CONG! CHAO MUNG       " -ForegroundColor Green
        Write-Host "==============================================" -ForegroundColor Green
        foreach ($tunnel in $tunnels.tunnels) {
            Write-Host "  + Tunnel Name: $($tunnel.name)" -ForegroundColor White
            Write-Host "  + Public URL : $($tunnel.public_url)" -ForegroundColor Green
            Write-Host "  + Local URL  : $($tunnel.config.addr)" -ForegroundColor Gray
            Write-Host "----------------------------------------------" -ForegroundColor Gray
        }
    } else {
        Write-Warning "Khong tim thay tunnel nao dang hoat dong tu Ngrok API."
    }
} catch {
    Write-Warning "Khong the ket noi den Ngrok Local API (port 4040). Vui long kiem tra cua so Ngrok de xem chi tiet loi."
}
