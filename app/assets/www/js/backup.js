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
