/**
 * backup.js - Data binding for Backup & Restore
 */

window.handleBackup = async () => {
    try {
        window.API.toast("Creating backup...", "info");
        const res = await window.API.request('create_backup');
        alert("Backup created successfully!\n\nSaved at:\n" + res.path);
    } catch (e) {
        if (e.toString().includes('cancelled')) {
            window.API.toast("Backup cancelled", "info");
        } else {
            window.API.toast("Backup failed: " + e, "error");
        }
    }
};

window.handleRestore = async () => {
    if (confirm("Are you sure you want to restore the database? This will overwrite current data and requires a restart.")) {
        try {
            window.API.toast("Restoring database...", "info");
            await window.API.request('restore_backup');
            alert("Restore complete!\n\nPlease restart the application to load the recovered data.");
        } catch (e) {
            if (e.toString().includes('cancelled')) {
                window.API.toast("Restore cancelled", "info");
            } else {
                window.API.toast("Restore failed: " + e, "error");
            }
        }
    }
};

window.handleEraseData = async () => {
    if (confirm("🚨 WARNING: Are you sure you want to completely erase ALL data (Customers, Orders, Measurements)?\n\nMake sure you have created a backup first!\n\nThis action CANNOT be undone. Press OK to proceed.")) {
        if (confirm("Final Confirmation: All your data will be permanently deleted now. Type 'yes' in your mind, then press OK.")) {
            try {
                window.API.toast("Erasing all data...", "info");
                await window.API.request('erase_all_data');
                alert("Data erased successfully. The application will now restart with an empty database.");
                // Simply navigate to dashboard to reflect changes, though a hard restart is recommended
                window.API.request('navigate_to', {page: 'dashboard'});
            } catch (e) {
                window.API.toast("Failed to erase data: " + e, "error");
            }
        }
    }
};
