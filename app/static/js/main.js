document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF Token from meta tag or cookie
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    // Setup global Favorite toggling
    document.querySelectorAll('.favorite-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const propertyId = this.dataset.propertyId;
            if (!propertyId) return;

            fetch(`/api/favoritar/${propertyId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.require_login) {
                    window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }
                if (data.success) {
                    const icon = this.querySelector('i');
                    if (data.is_favorite) {
                        this.classList.add('active');
                        if (icon) icon.className = 'fas fa-heart text-danger';
                    } else {
                        this.classList.remove('active');
                        if (icon) icon.className = 'far fa-heart';
                    }
                    showToast(data.message, 'success');
                }
            })
            .catch(err => {
                console.error(err);
                showToast('Erro ao processar solicitação de favorito.', 'danger');
            });
        });
    });

    // Image Upload Previews
    const imageInput = document.getElementById('images');
    const previewContainer = document.getElementById('image-preview-container');
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            if (this.files) {
                Array.from(this.files).forEach((file, idx) => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const col = document.createElement('div');
                        col.className = 'col-4 col-md-3 mb-2';
                        col.innerHTML = `
                            <div class="card card-brutalist p-1 text-center">
                                <img src="${e.target.result}" class="img-fluid rounded" style="height: 90px; object-fit: cover;">
                                <small class="text-muted mt-1 text-truncate">${file.name}</small>
                                ${idx === 0 ? '<span class="badge bg-warning text-dark mt-1">Capa Principal</span>' : ''}
                            </div>
                        `;
                        previewContainer.appendChild(col);
                    };
                    reader.readAsDataURL(file);
                });
            }
        });
    }

    // Helper Toast Notification
    window.showToast = function(message, type = 'info') {
        let toastBox = document.getElementById('toast-container');
        if (!toastBox) {
            toastBox = document.createElement('div');
            toastBox.id = 'toast-container';
            toastBox.style.position = 'fixed';
            toastBox.style.bottom = '20px';
            toastBox.style.right = '20px';
            toastBox.style.zIndex = '9999';
            document.body.appendChild(toastBox);
        }

        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show card-brutalist mb-2 shadow`;
        toast.style.minWidth = '280px';
        toast.innerHTML = `
            <strong>Notification:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        toastBox.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4000);
    };
});
