// PlaceTrack - Async Application Status Updater
// Handles inline status updates for placement admins using vanilla fetch API

document.addEventListener('DOMContentLoaded', function () {
    const statusSelects = document.querySelectorAll('.applicant-status-select');

    statusSelects.forEach(select => {
        select.addEventListener('change', async function () {
            const appId = this.getAttribute('data-app-id');
            const newStatus = this.value;
            const statusIndicator = document.getElementById(`status-feedback-${appId}`);

            // Provide visual loading state
            this.disabled = true;
            if (statusIndicator) {
                statusIndicator.textContent = 'Saving...';
                statusIndicator.style.color = '#64748b';
            }

            // Retrieve CSRF token from page cookie or hidden input
            const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            try {
                const response = await fetch(`/jobs/applications/${appId}/status/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ status: newStatus })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    if (statusIndicator) {
                        statusIndicator.textContent = '✓ Saved';
                        statusIndicator.style.color = '#16a34a';
                        setTimeout(() => {
                            statusIndicator.textContent = '';
                        }, 2500);
                    }
                } else {
                    alert(`Error updating status: ${data.error || 'Server rejected request'}`);
                    if (statusIndicator) {
                        statusIndicator.textContent = '✗ Failed';
                        statusIndicator.style.color = '#dc2626';
                    }
                }
            } catch (error) {
                console.error('Fetch error:', error);
                alert('Network error while updating status. Please try again.');
                if (statusIndicator) {
                    statusIndicator.textContent = '✗ Network Error';
                    statusIndicator.style.color = '#dc2626';
                }
            } finally {
                this.disabled = false;
            }
        });
    });
});

// Helper function to read CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
