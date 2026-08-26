const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const fs = require('fs');
const path = require('path');
const os = require('os');

const args = process.argv.slice(2);
if (args.length < 2) {
    console.error("Usage: node send.js <phone_number> <message> [pdf_path]");
    process.exit(1);
}

const phoneNumber = args[0];
const message = args[1];
const pdfPath = args[2];

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
    
    const client = createClient();

    client.on('ready', async () => {
        try {
            const chatId = `${phoneNumber}@c.us`;
            
            if (pdfPath && fs.existsSync(pdfPath)) {
                console.log("Preparing PDF: " + pdfPath);
                const media = MessageMedia.fromFilePath(pdfPath);
                console.log("Sending PDF...");
                await client.sendMessage(chatId, media, { caption: message, sendMediaAsDocument: true });
                console.log("PDF sent successfully via wwebjs!");
            } else {
                console.log("Sending text only...");
                await client.sendMessage(chatId, message);
            }
            console.log("Message sent successfully!");
            
            // Wait 5 seconds to ensure the browser finishes transmitting to WhatsApp servers
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            try { await client.destroy(); } catch(e) {}
            setTimeout(() => process.exit(0), 1000);
        } catch (error) {
            console.error("Failed to send message:", error);
            try { await client.destroy(); } catch(e) {}
            setTimeout(() => process.exit(1), 1000);
        }
    });

    client.on('qr', async () => {
        console.error('Session invalid, QR code requested. Please login again.');
        try { fs.rmSync(authPath, { recursive: true, force: true }); } catch (e) {}
        try { await client.destroy(); } catch(e) {}
        setTimeout(() => process.exit(1), 2000);
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
        console.error(`❌ Initialization failed (attempt ${attempt}/${MAX_RETRIES}):`, err.message);
        
        try { await client.destroy(); } catch(e) {}
        
        if (attempt < MAX_RETRIES) {
            console.log(`⏳ Retrying in 5 seconds...`);
            await new Promise(resolve => setTimeout(resolve, 5000));
            return startClient();
        } else {
            console.error(`❌ Failed after ${MAX_RETRIES} attempts.`);
            process.exit(1);
        }
    }
}

// Timeout after 120 seconds if it can't connect
setTimeout(async () => {
    console.error('Connection timed out');
    process.exit(1);
}, 120000);

startClient();
