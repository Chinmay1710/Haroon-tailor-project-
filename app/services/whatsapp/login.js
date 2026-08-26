const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const os = require('os');

console.log("🚀 Initializing WhatsApp connection...");

let chromePath = '';
const sysPaths = {
    darwin: ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'],
    win32: [
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
        'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
    ]
};
let possiblePaths = sysPaths[os.platform()] || [];
for (let p of possiblePaths) {
    if (fs.existsSync(p)) {
        chromePath = p;
        break;
    }
}
if (!chromePath) {
    try {
        const puppeteer = require('puppeteer');
        chromePath = puppeteer.executablePath();
    } catch(e) {}
}
console.log("Using browser:", chromePath);

const authPath = path.join(__dirname, '..', '..', '..', '.wwebjs_auth');

function createClient() {
    return new Client({
        authStrategy: new LocalAuth({ dataPath: authPath }),
        puppeteer: {
            executablePath: chromePath,
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--disable-extensions',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--single-process'
            ]
        }
    });
}

// Clear any zombie lock files
try {
    const lock1 = path.join(authPath, 'session', 'SingletonLock');
    const lock2 = path.join(authPath, 'session', 'SingletonCookie');
    const lock3 = path.join(authPath, 'session', 'SingletonSocket');
    if (fs.existsSync(lock1)) fs.unlinkSync(lock1);
    if (fs.existsSync(lock2)) fs.unlinkSync(lock2);
    if (fs.existsSync(lock3)) fs.unlinkSync(lock3);
} catch (e) {}

const MAX_RETRIES = 3;
let attempt = 0;

async function startClient() {
    attempt++;
    console.log(`Attempt ${attempt}/${MAX_RETRIES}...`);
    
    const client = createClient();
    
    client.on('qr', (qr) => {
        console.log("SCAN THIS QR CODE TO CONNECT WHATSAPP:");
        qrcode.generate(qr, { small: true });
    });

    client.on('ready', async () => {
        console.log('\n✅ Connection finished! WhatsApp is successfully linked.');
        console.log('You can close this window now.');
        try { await client.destroy(); } catch(e) {}
        setTimeout(() => process.exit(0), 2000);
    });

    client.on('auth_failure', async msg => {
        console.error('AUTHENTICATION FAILURE', msg);
        try { fs.rmSync(authPath, { recursive: true, force: true }); } catch (e) {}
        try { await client.destroy(); } catch(e) {}
        setTimeout(() => process.exit(1), 2000);
    });

    try {
        await client.initialize();
    } catch (err) {
        console.error(`❌ Initialization failed (attempt ${attempt}):`, err.message);
        
        try { await client.destroy(); } catch(e) {}
        
        if (attempt < MAX_RETRIES) {
            console.log(`⏳ Retrying in 5 seconds...\n`);
            await new Promise(resolve => setTimeout(resolve, 5000));
            return startClient();
        } else {
            console.error(`❌ Failed after ${MAX_RETRIES} attempts. Please try again later.`);
            process.exit(1);
        }
    }
}

startClient();
