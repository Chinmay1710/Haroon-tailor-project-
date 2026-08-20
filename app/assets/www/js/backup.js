/**
 * backup.js - Data binding for Backup & Restore
 */

document.addEventListener("DOMContentLoaded", function() {
    const btnBackup = document.getElementById('btn-backup');
    const btnRestore = document.getElementById('btn-restore');
    
    if (btnBackup) {
        btnBackup.addEventListener('click', async () => {
            try {
                window.API.toast("Creating backup...", "info");
                const res = await window.API.request('create_backup');
                window.API.toast("Backup created successfully at " + res.path, "success");
            } catch (e) {
                window.API.toast("Backup failed: " + e, "error");
            }
        });
    }
    
    if (btnRestore) {
        btnRestore.addEventListener('click', async () => {
            if (confirm("Are you sure you want to restore the database? This will overwrite current data and requires a restart.")) {
                try {
                    window.API.toast("Restoring database...", "info");
                    await window.API.request('restore_backup');
                    window.API.toast("Restore complete. Please restart application.", "success");
                } catch (e) {
                    window.API.toast("Restore failed: " + e, "error");
                }
            }
        });
    }
});
