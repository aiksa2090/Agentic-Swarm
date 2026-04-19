# Require Admin Rights
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "يرجى تشغيل هذا السكربت كمسؤول (Run as Administrator) لكي يتمكن من تعديل مساحة الذاكرة."
    Write-Warning "قم بفتح PowerShell كمسؤول ثم نفذ هذا السجل."
    Pause
    Exit
}

Write-Host ">>> جاري تعديل الذاكرة الافتراضية (Paging File) في Windows لتفادي خطأ 1455..." -ForegroundColor Cyan

# Disable Automatic Management
$sys = Get-WmiObject Win32_ComputerSystem -EnableAllPrivileges
$sys.AutomaticManagedPagefile = $False
$sys.Put() | Out-Null

Write-Host "[x] تم تعطيل الإدارة التلقائية للويندوز." -ForegroundColor Green

# Set Page File for C: drive to 100GB (102400 MB)
$PageFile = Get-WmiObject Win32_PageFileSetting | Where-Object { $_.Name -like "C:*" }

if (-not $PageFile) {
    Set-WmiInstance -Class Win32_PageFileSetting -Arguments @{Name="C:\pagefile.sys"} | Out-Null
    $PageFile = Get-WmiObject Win32_PageFileSetting | Where-Object { $_.Name -like "C:*" }
}

$PageFile.InitialSize = 102400   # 100 GB
$PageFile.MaximumSize = 131072   # 128 GB
$PageFile.Put() | Out-Null

Write-Host "[x] تم تطبيق 100 جيجابايت כحجم ثابت للذاكرة الوهمية بنجاح!" -ForegroundColor Green

Write-Host ""
Write-Host ">>> عملية الترقية انتهت بنجاح. قد يطلب Windows إعادة تشغيل الكمبيوتر لتطبيق هذه المساحة الضخمة." -ForegroundColor Yellow
Write-Host ">>> بعد إعادة التشغيل، لن تواجه رسالة الخطأ 1455 إطلاقاً." -ForegroundColor Yellow
Pause
