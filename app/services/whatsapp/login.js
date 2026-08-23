const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

console.log("🚀 Initializing WhatsApp connection...");

const os = require('os');
let chromePath = '';
if (os.platform() === 'darwin') {
    chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
} else if (os.platform() === 'win32') {
    const fs = require('fs');
    const winPath1 = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    const winPath2 = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';
    chromePath = fs.existsSync(winPath1) ? winPath1 : winPath2;
}

const path = require('path');
const authPath = path.join(__dirname, '..', '..', '..', '.wwebjs_auth');

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: authPath }),
    puppeteer: {
        executablePath: chromePath,
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Clear any zombie lock files
try {
    const lock1 = path.join(authPath, 'session', 'SingletonLock');
    const lock2 = path.join(authPath, 'session', 'SingletonCookie');
    const lock3 = path.join(authPath, 'session', 'SingletonSocket');
    if (fs.existsSync(lock1)) fs.unlinkSync(lock1);
    if (fs.existsSync(lock2)) fs.unlinkSync(lock2);
    if (fs.existsSync(lock3)) fs.unlinkSync(lock3);
} catch (e) {}

client.on('qr', (qr) => {
    console.log("SCAN THIS QR CODE TO CONNECT WHATSAPP:");
    qrcode.generate(qr, { small: true });
});

client.on('ready', async () => {
    console.log('\n✅ Connection finished! WhatsApp is successfully linked.');
    console.log('You can close this window now.');
    await client.destroy();
    setTimeout(() => process.exit(0), 2000);
});

client.on('auth_failure', async msg => {
    console.error('AUTHENTICATION FAILURE', msg);
    await client.destroy();
    setTimeout(() => process.exit(1), 2000);
});

client.initialize();
