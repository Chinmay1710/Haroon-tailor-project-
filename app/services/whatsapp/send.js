const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const fs = require('fs');

const args = process.argv.slice(2);
if (args.length < 2) {
    console.error("Usage: node send.js <phone_number> <message> [pdf_path]");
    process.exit(1);
}

const phoneNumber = args[0];
const message = args[1];
const pdfPath = args[2];

const os = require('os');
let chromePath = '';
if (os.platform() === 'darwin') {
    chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
} else if (os.platform() === 'win32') {
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
        
        try {
            if (client.pupBrowser) {
                const pid = client.pupBrowser.process().pid;
                process.kill(pid, 'SIGKILL');
            }
        } catch(e) {}
        setTimeout(() => process.exit(0), 1000);
    } catch (error) {
        console.error("Failed to send message:", error);
        try {
            if (client.pupBrowser) {
                const pid = client.pupBrowser.process().pid;
                process.kill(pid, 'SIGKILL');
            }
        } catch(e) {}
        setTimeout(() => process.exit(1), 1000);
    }
});

client.on('qr', async () => {
    console.error('Session invalid, QR code requested. Please login again.');
    await client.destroy();
    setTimeout(() => process.exit(1), 2000);
});

client.on('auth_failure', async msg => {
    console.error('AUTHENTICATION FAILURE', msg);
    await client.destroy();
    setTimeout(() => process.exit(1), 2000);
    try { await client.destroy(); } catch(e) {}
});

// Timeout after 120 seconds if it can't connect
setTimeout(async () => {
    console.error('Connection timed out');
    try {
        if (client.pupBrowser) {
            const pid = client.pupBrowser.process().pid;
            process.kill(pid, 'SIGKILL');
        }
    } catch(e) {}
    setTimeout(() => process.exit(1), 1000);
}, 120000);

client.initialize().catch(err => {
    console.error('Initialization error:', err);
    try {
        if (client.pupBrowser) {
            const pid = client.pupBrowser.process().pid;
            process.kill(pid, 'SIGKILL');
        }
    } catch(e) {}
    setTimeout(() => process.exit(1), 1000);
});
