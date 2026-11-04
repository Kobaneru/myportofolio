// Shared AJAX and rendering helpers. Django URLs stay in each page's template.
window.PortfolioUI = (() => {
    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(';').map(value => value.trim())
            .find(value => value.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function escapeHtml(value) {
        return String(value ?? '').replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;').replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;').replaceAll("'", '&#39;');
    }

    function formatDate(value) {
        return value ? new Date(`${value}T00:00:00`).toLocaleDateString('en-US', {
            month: 'long', year: 'numeric',
        }) : '';
    }

    function endpoint(pattern, id) {
        return pattern.replace('00000000-0000-0000-0000-000000000000', id);
    }

    function pageSections() {
        const sections = ['loading', 'error', 'empty', 'grid'].map(id => document.getElementById(id));
        return ({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) => {
            [showLoading, showError, showEmpty, showGrid].forEach((show, index) => {
                sections[index].classList.toggle('hide', !show);
            });
        };
    }

    function clearFormErrors(form) {
        form.querySelectorAll('[data-error-for]').forEach(element => {
            element.textContent = '';
            element.hidden = true;
        });
    }

    function showFormErrors(form, data = {}) {
        let firstInvalidField;
        form.querySelectorAll('[data-error-for]').forEach(element => {
            const messages = data?.[element.dataset.errorFor];
            if (!messages) return;
            element.textContent = Array.isArray(messages) ? messages.join(' ') : String(messages);
            element.hidden = false;
            firstInvalidField ??= form.elements.namedItem(element.dataset.errorFor);
        });
        firstInvalidField?.focus();
    }

    function starButton(item, isAuthenticated, loginUrl) {
        const icon = '<span aria-hidden="true">&#9733;</span>';
        const count = `<span class="star-count">${escapeHtml(item.star_count)}</span>`;
        if (!isAuthenticated) {
            return `<a href="${escapeHtml(loginUrl)}" class="button button-star">${icon} Login to star ${count}</a>`;
        }
        return `<button type="button" class="button button-star${item.is_starred ? ' is-starred' : ''}"
            data-action="star" data-id="${escapeHtml(item.id)}" aria-pressed="${Boolean(item.is_starred)}"
            title="${escapeHtml(item.starred_by_names || 'Jadilah yang pertama memberi star')}">
            ${icon} ${item.is_starred ? 'Unstar' : 'Star'} ${count}</button>`;
    }

    function actionButton(action, id, label, name = '') {
        const variant = action === 'delete' ? 'danger' : 'secondary';
        return `<button type="button" class="button button-${variant}" data-action="${escapeHtml(action)}"
            data-id="${escapeHtml(id)}" data-name="${escapeHtml(name)}">${escapeHtml(label)}</button>`;
    }

    async function writeJSON(url, method, payload) {
        const response = await fetch(url, {
            method,
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        // DELETE returns no body; parsing JSON here would incorrectly report failure.
        if (response.status === 204) return null;
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const messages = Object.values(data ?? {}).flat().filter(value => typeof value === 'string');
            const error = new Error(messages.join(' ') || `Request failed (HTTP ${response.status}).`);
            error.data = data;
            throw error;
        }
        return data;
    }

    return {
        getCookie, escapeHtml, formatDate, endpoint, pageSections,
        clearFormErrors, showFormErrors, starButton, actionButton, writeJSON,
    };
})();
