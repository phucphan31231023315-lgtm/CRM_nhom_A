@echo off
echo Dang khoi dong Odoo 19...
set PATH=%PATH%;C:\Program Files\Git\cmd;C:\Users\PhucHoang\AppData\Local\Programs\Python\Python312;C:\Users\PhucHoang\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\PostgreSQL\18\bin;C:\Program Files\nodejs
cd /d "d:\Odoo 19\odoo"
..\venv\Scripts\python.exe odoo-bin -c ..\odoo.conf
pause
