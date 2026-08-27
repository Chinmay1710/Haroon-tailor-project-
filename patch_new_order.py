import re

file_path = r'app/assets/www/js/new_order.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace currentImageBase64 with currentImagesBase64 declaration
content = content.replace('let currentImageBase64 = null;', 'let currentImagesBase64 = [];')

# In openAddItemModal:
def replace_open_modal(match):
    return '''    currentImagesBase64 = [];
    renderPhotoPreviews();
    clearPhotoCapture();'''
content = re.sub(r'    currentImageBase64 = null;\s+clearPhotoCapture\(\);', replace_open_modal, content)

# In edit mode
def replace_edit_image(match):
    return '''        if (item.image_base64) {
            currentImagesBase64 = Array.isArray(item.image_base64) ? [...item.image_base64] : (item.image_base64 ? [item.image_base64] : []);
            if(window.renderPhotoPreviews) renderPhotoPreviews();
        }'''
content = re.sub(r'        if \(item\.image_base64\) \{.*?document\.getElementById\(\'modal-photo-preview-container\'\)\.classList\.remove\(\'hidden\'\);\s+\}', replace_edit_image, content, flags=re.DOTALL)

# In saveModalItem
content = content.replace('image_base64: currentImageBase64', 'image_base64: [...currentImagesBase64]')

# In handleFileUpload
def replace_upload(match):
    return '''    const reader = new FileReader();
    reader.onload = function(e) {
        currentImagesBase64.push(e.target.result);
        if(window.renderPhotoPreviews) renderPhotoPreviews();
    };
    reader.readAsDataURL(file);'''
content = re.sub(r'    const reader = new FileReader\(\);\s+reader\.onload = function\(e\) \{.*?reader\.readAsDataURL\(file\);', replace_upload, content, flags=re.DOTALL)

# In capturePhoto
def replace_capture(match):
    return '''    // Convert to base64 jpeg
    const imgData = canvas.toDataURL('image/jpeg', 0.8);
    currentImagesBase64.push(imgData);
    
    // Stop camera and show preview
    stopCamera();
    if(window.renderPhotoPreviews) renderPhotoPreviews();'''
content = re.sub(r'    // Convert to base64 jpeg.*?document\.getElementById\(\'modal-photo-preview-container\'\)\.classList\.remove\(\'hidden\'\);', replace_capture, content, flags=re.DOTALL)

# In clearPhotoCapture
def replace_clear(match):
    return '''window.clearPhotoCapture = function() {
    currentImagesBase64 = [];
    document.getElementById('modal-item-photo').value = '';
    if(window.renderPhotoPreviews) renderPhotoPreviews();
    stopCamera();
};'''
content = re.sub(r'window\.clearPhotoCapture = function\(\) \{.*?stopCamera\(\);\s+\};', replace_clear, content, flags=re.DOTALL)

# Add renderPhotoPreviews and removePhoto functions, and update quantity listener
additions = '''
window.renderPhotoPreviews = function() {
    const list = document.getElementById('modal-photo-preview-list');
    const badge = document.getElementById('photo-count-badge');
    const qty = parseInt(document.getElementById('modal-item-qty').value) || 1;
    
    if (badge) {
        badge.textContent = `${currentImagesBase64.length} / ${qty}`;
        if (currentImagesBase64.length < qty) {
            badge.classList.remove('bg-green-100', 'text-green-800');
            badge.classList.add('bg-primary-container', 'text-on-primary-container');
        } else {
            badge.classList.remove('bg-primary-container', 'text-on-primary-container');
            badge.classList.add('bg-green-100', 'text-green-800');
        }
    }
    
    if (!list) return;
    
    list.innerHTML = '';
    currentImagesBase64.forEach((src, idx) => {
        const div = document.createElement('div');
        div.className = 'relative border border-outline rounded-lg overflow-hidden bg-surface-container-lowest h-16 w-16 shadow-sm flex-shrink-0';
        div.innerHTML = `
            <img src=\"${src}\" class=\"w-full h-full object-cover cursor-pointer hover:opacity-80\" onclick=\"openImageModal('${src}')\">
            <button type=\"button\" onclick=\"removePhoto(${idx})\" class=\"absolute -top-2 -right-2 w-6 h-6 bg-error text-on-error rounded-full flex items-center justify-center shadow-sm z-10\">
                <span class=\"material-symbols-outlined text-[14px]\" data-icon=\"close\">close</span>
            </button>
        `;
        list.appendChild(div);
    });
};

window.removePhoto = function(idx) {
    currentImagesBase64.splice(idx, 1);
    renderPhotoPreviews();
};

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const qtyInput = document.getElementById('modal-item-qty');
        if (qtyInput) {
            qtyInput.addEventListener('input', () => {
                if(window.renderPhotoPreviews) window.renderPhotoPreviews();
            });
        }
    }, 500);
});
'''

content += additions

# Fix renderOrderItems photo Html
def replace_render_items(match):
    return '''        let photoHtml = '';
        if (item.image_base64 && item.image_base64.length > 0) {
            const arr = Array.isArray(item.image_base64) ? item.image_base64 : [item.image_base64];
            photoHtml = '<div class=\"flex gap-1 flex-wrap\">';
            arr.forEach(imgSrc => {
                if (imgSrc) {
                    photoHtml += `<div class=\"w-10 h-10 rounded overflow-hidden flex-shrink-0 border border-outline cursor-pointer hover:opacity-80\" onclick=\"openImageModal('${imgSrc}')\"><img src=\"${imgSrc}\" class=\"w-full h-full object-cover\"></div>`;
                }
            });
            photoHtml += '</div>';
        } else if (item.image_path) {
            const arr = item.image_path.split(',').filter(p=>p.trim());
            photoHtml = '<div class=\"flex gap-1 flex-wrap\">';
            arr.forEach(imgSrc => {
                if (imgSrc) {
                    photoHtml += `<div class=\"w-10 h-10 rounded overflow-hidden flex-shrink-0 border border-outline cursor-pointer hover:opacity-80\" onclick=\"openImageModal('${imgSrc}')\"><img src=\"${imgSrc}\" class=\"w-full h-full object-cover\"></div>`;
                }
            });
            photoHtml += '</div>';
        }'''
content = re.sub(r'        let photoHtml = \'\';\s+if \(item\.image_base64 \|\| item\.image_path\) \{.*?photoHtml = `<div class="w-12 h-12 rounded overflow-hidden flex-shrink-0 border border-outline"><img src="\$\{imgSrc\}" class="w-full h-full object-cover"></div>`;\s+\}', replace_render_items, content, flags=re.DOTALL)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated new_order.js')
