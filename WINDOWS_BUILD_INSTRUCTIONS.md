# Haroon Tailor — Windows Build & Deployment Instructions

Follow these exact steps to build the application natively on the target Windows 10/11 x64 machine.

## Prerequisites
Ensure the following are installed on the Windows PC:
1. **Python 3.11 (64-bit)**
   - Download from python.org. Ensure you check **"Add Python to PATH"** during installation.
2. **Node.js (v18+ LTS)**
   - Download from nodejs.org. Required for WhatsApp background services.
3. **Visual C++ Redistributable (2015-2022)**
   - Download from Microsoft.

---

## 1. Project Setup
Open PowerShell or Command Prompt, navigate to the project directory, and run the following commands:

```cmd
# Create a fresh virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Upgrade pip (Best practice)
python -m pip install --upgrade pip

# Install Python requirements
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller

# Install Node.js requirements (WhatsApp integration)
npm install
```

---

## 2. Build the Application
Ensure your virtual environment is still activated (`(venv)` should be visible in the prompt). Run the following commands to ensure a clean build:

```cmd
# Remove any leftover build artifacts
rmdir /S /Q build
rmdir /S /Q dist

# Build the executable using the production spec file
pyinstaller --clean --noconfirm HaroonTailor.spec
```

---

## 3. Deployment & Execution
The PyInstaller process will create the final application in the `dist/` directory.

1. **Locate the EXE:** 
   Navigate to `dist\Haroon Tailor\`. The executable is `Haroon Tailor.exe`.
2. **Launch:** 
   Double-click `Haroon Tailor.exe` to run the application. No console window should appear.
3. **Important Note:** 
   The `node_modules` folder MUST be present in the same directory as the executable (or one level up depending on where you place the final folder) for WhatsApp to function. The easiest deployment is to deploy the entire `dist\Haroon Tailor\` folder and place the `node_modules` directory inside it.

---

## 4. Application Data Security
This application is designed to be fully decoupled from its executable directory:
- **Database, Uploads, Logs, and Backups** will be automatically created in:
  `%APPDATA%\TailorShopManager\` (Typically `C:\Users\<YourUsername>\AppData\Roaming\TailorShopManager\`).
- If you need to uninstall or update the application executable in the future, deleting the `dist\Haroon Tailor` folder will **NOT** delete the client's business data.

---

## Troubleshooting
- **Missing Module Error on Startup:** Ensure `pip install -r requirements.txt` completed successfully in the virtual environment before building.
- **WhatsApp fails to connect:** Ensure Node.js is installed globally and accessible from the command line (`node -v`), and that `npm install` was run.
- **Blank Screen / UI not loading:** Ensure the `HaroonTailor.spec` file is used, as it contains the correct path mapping for the HTML/CSS/Font assets.
