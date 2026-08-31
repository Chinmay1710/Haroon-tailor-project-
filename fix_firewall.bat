@echo off
echo Adding Windows Firewall Exception for Tailor Shop Manager (Port 8000)...
netsh advfirewall firewall add rule name="TailorShop Port 8000" dir=in action=allow protocol=TCP localport=8000
echo.
echo Firewall rule added successfully! You can now close this window.
pause
