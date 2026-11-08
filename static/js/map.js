// full-country view: mainland Denmark plus Bornholm
const DENMARK_VIEW = [56.1, 10.0];
const DENMARK_ZOOM = 7;

const map = L.map('map').setView(DENMARK_VIEW, DENMARK_ZOOM);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>-bidragydere',
    maxZoom: 18
}).addTo(map);

const panel = document.getElementById('filterPanel');
const filterButton = document.getElementById('filterButton');
const applyButton = document.getElementById('applyFilters');
const showAllButton = document.getElementById('showAll');
const countEl = document.getElementById('schoolCount');
const errorBox = document.getElementById('errorBox');
const errorEl = document.getElementById('errorMessage');
const retryButton = document.getElementById('retryButton');
const chipsEl = document.getElementById('activeFilters');
const loadingEl = document.getElementById('loading');
const modal = document.getElementById('schoolDetailsModal');
const modalTitle = document.getElementById('modalTitle');
const modalContent = document.getElementById('modalContent');
const closeButton = modal.querySelector('.close');
const searchInput = document.getElementById('schoolSearch');

const state = { types: [], kommuner: [], query: '', shown: 0 };
let markers = null;
let allSchools = null;
let lastFocused = null;

// ---- filter panel ----

function setPanel(open) {
    const hadFocus = panel.contains(document.activeElement);
    panel.hidden = !open;
    filterButton.setAttribute('aria-expanded', String(open));
    if (open) {
        panel.querySelector('.select2-search__field')?.focus();
    } else if (hadFocus) {
        filterButton.focus();
    }
}

filterButton.addEventListener('click', () => setPanel(panel.hidden));

function applyFilters() {
    state.types = $('#instTypeFilters').val() || [];
    state.kommuner = $('#kommuneFilters').val() || [];
    state.query = searchInput.value.trim();
    renderSchools();
    renderChips();
    renderStatus();
    setPanel(false);
}

function removeFilter(kind, value) {
    if (kind === 'query') {
        searchInput.value = '';
    } else {
        const $select = kind === 'type' ? $('#instTypeFilters') : $('#kommuneFilters');
        const remaining = ($select.val() || []).filter(v => v !== value);
        $select.val(remaining).trigger('change');
    }
    applyFilters();
    // the clicked chip is gone; keep keyboard users somewhere real
    (chipsEl.querySelector('.chip') || filterButton).focus();
}

function renderChips() {
    chipsEl.replaceChildren();
    const active = [
        ...state.types.map(value => ({ kind: 'type', value })),
        ...state.kommuner.map(value => ({ kind: 'kommune', value })),
        ...(state.query ? [{ kind: 'query', value: `Søgning: ${state.query}` }] : [])
    ];

    active.forEach(({ kind, value }) => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'chip';
        const label = document.createElement('span');
        label.className = 'chip-label';
        label.textContent = value;
        chip.append(label);
        const cross = document.createElement('span');
        cross.className = 'chip-x';
        cross.setAttribute('aria-hidden', 'true');
        cross.textContent = '×';
        chip.append(cross);
        chip.setAttribute('aria-label', `Fjern filter: ${value}`);
        chip.addEventListener('click', () => removeFilter(kind, value));
        chipsEl.append(chip);
    });

    showAllButton.hidden = active.length === 0;
}

applyButton.addEventListener('click', applyFilters);
searchInput.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        applyFilters();
    }
});
showAllButton.addEventListener('click', () => {
    $('#instTypeFilters').val(null).trigger('change');
    $('#kommuneFilters').val(null).trigger('change');
    searchInput.value = '';
    applyFilters();
});

// ---- map rendering ----

function renderSchools() {
    if (markers) {
        map.removeLayer(markers);
        markers = null;
    }
    if (!allSchools) {
        state.shown = 0;
        return;
    }

    markers = L.markerClusterGroup();

    const query = state.query.toLowerCase();
    const shown = allSchools.filter(school => {
        const typeMatch = state.types.length === 0 || state.types.includes(school.inst_type_navn);
        const kommuneMatch = state.kommuner.length === 0 || state.kommuner.includes(school.adm_kommune_navn);
        const queryMatch = !query || (school.inst_navn || '').toLowerCase().includes(query);
        return typeMatch && kommuneMatch && queryMatch;
    });
    state.shown = shown.length;

    shown.forEach(school => {
        const label = [school.inst_navn, school.inst_type_navn, school.adm_kommune_navn].filter(Boolean).join(', ');
        const marker = L.marker([school.geo_bredde_grad, school.geo_laengde_grad], { alt: label, title: label });
        marker.bindPopup(popupHtml(school));
        markers.addLayer(marker);
    });

    map.addLayer(markers);
    labelMapControls();

    if (!shown.length) {
        return;
    }
    const bounds = markers.getBounds();
    // getZoom() still reports the pre-animation value here, so ask for the target zoom
    const fitZoom = map.getBoundsZoom(bounds, false, [40, 40]);
    if (!state.types.length && !state.kommuner.length && !state.query) {
        map.setView(DENMARK_VIEW, DENMARK_ZOOM);
    } else if (fitZoom < DENMARK_ZOOM) {
        // a narrow screen would otherwise zoom out to half of Europe
        map.setView(DENMARK_VIEW, DENMARK_ZOOM);
    } else {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 11 });
    }
}

// clusters and markers are created without roles or accessible names
function labelMapControls() {
    document.querySelectorAll('.marker-cluster').forEach(el => {
        el.setAttribute('role', 'button');
        el.setAttribute('aria-label', `${el.textContent.trim()} skoler - zoom ind`);
    });
    document.querySelectorAll('.leaflet-marker-icon').forEach(el => {
        el.setAttribute('role', 'button');
    });
}

map.on('zoomend', labelMapControls);

function renderStatus() {
    if (!allSchools) {
        countEl.textContent = 'Kunne ikke indlæse skoledata';
        return;
    }
    if (state.shown === 0) {
        countEl.textContent = 'Ingen skoler matcher filtrene';
        return;
    }
    countEl.textContent = `Viser ${fmt(state.shown)} af ${fmt(allSchools.length)} skoler`;
}

const fmt = number => number.toLocaleString('da-DK');

// popup() takes an HTML string, so CSV values must be escaped.
function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[char]);
}

function popupHtml(school) {
    return `
        <div class="school-popup">
            <h3>${esc(school.inst_navn)}</h3>
            <p>${esc(school.inst_type_navn)}</p>
            <p>${esc(school.adm_kommune_navn || 'Kommune ikke oplyst')}</p>
            <button type="button" class="details-btn" data-school-id="${esc(school.id)}">Flere detaljer</button>
        </div>
    `;
}

// ---- details dialog ----

function closeModal() {
    modal.style.display = 'none';
    // the popup behind the dialog is closed, so its button may be gone
    const target = lastFocused && document.contains(lastFocused) ? lastFocused : filterButton;
    target.focus();
}

function detailRow(label, value) {
    const row = document.createElement('p');
    const name = document.createElement('strong');
    name.textContent = label + ':';
    row.append(name, ' ', value);
    return row;
}

function websiteLink(url) {
    if (!url) {
        return 'Ikke oplyst';
    }
    const link = document.createElement('a');
    link.href = websiteUrl(url);
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = url;
    return link;
}

function websiteUrl(url) {
    const trimmed = url.trim();
    return /^https?:\/\//i.test(trimmed) ? trimmed : 'https://' + trimmed;
}

function showSchoolDetails(schoolId) {
    const school = allSchools?.find(candidate => String(candidate.id) === String(schoolId));
    if (!school) {
        return;
    }

    map.closePopup();
    lastFocused = document.activeElement;
    modalTitle.textContent = school.inst_navn;

    const address = [school.inst_adr, school.postnr, school.postdistrikt].filter(Boolean).join(', ');

    modalContent.replaceChildren(
        detailRow('Type', school.inst_type_navn || 'Ikke oplyst'),
        detailRow('Kommune', school.adm_kommune_navn || 'Ikke oplyst'),
        detailRow('Adresse', address || 'Ikke oplyst'),
        detailRow('Telefon', school.tlf_nr || 'Ikke oplyst'),
        detailRow('E-mail', school.e_mail || 'Ikke oplyst'),
        detailRow('Hjemmeside', websiteLink(school.web_adr)),
        detailRow('Institutionsnr.', String(school.id))
    );

    modal.style.display = 'block';
    closeButton.focus();
}

closeButton.addEventListener('click', closeModal);
modal.addEventListener('click', event => {
    if (event.target === modal) {
        closeModal();
    }
});

// keep Tab inside the dialog while it is open
modal.addEventListener('keydown', event => {
    if (event.key !== 'Tab') {
        return;
    }
    const focusable = [...modal.querySelectorAll('button, a[href]')];
    if (!focusable.length) {
        return;
    }
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
    }
});

// capture phase: select2 stops keydown propagation from its search field
document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') {
        return;
    }
    if (modal.style.display === 'block') {
        closeModal();
    } else if (!panel.hidden) {
        setPanel(false);
    }
}, true);

document.addEventListener('click', event => {
    const detailsButton = event.target.closest('.details-btn');
    if (detailsButton) {
        showSchoolDetails(detailsButton.dataset.schoolId);
    }
});

// ---- data loading ----

function showError(message) {
    errorEl.textContent = message;
    errorBox.hidden = false;
}

// a failed JSON fetch cannot be retried in place: select2 never initialised
retryButton.addEventListener('click', () => window.location.reload());

function countBy(list, key) {
    const counts = new Map();
    (list || []).forEach(item => {
        const value = item[key];
        if (value) {
            counts.set(value, (counts.get(value) || 0) + 1);
        }
    });
    return counts;
}

function loadSchools() {
    loadingEl.style.display = 'block';
    return fetch('data/schools.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(schools => {
            allSchools = schools;
        })
        .catch(error => {
            console.error('Error fetching school locations:', error);
            countEl.hidden = true;  // the error box says the same thing, once
            showError('Kunne ikke indlæse skoledata.');
        })
        .finally(() => {
            loadingEl.style.display = 'none';
        });
}

// select2 ships English strings for its own controls
const SELECT2_DANISH = {
    noResults: () => 'Ingen resultater',
    searching: () => 'Søger …',
    removeItem: () => 'Fjern',
    removeAllItems: () => 'Ryd alle'
};

function loadFilters() {
    return Promise.all([
        fetch('data/inst_types.json').then(response => response.json()),
        fetch('data/kommune_list.json').then(response => response.json()).then(values => values.filter(Boolean))
    ])
        .then(([types, kommuner]) => {
            const typeCounts = countBy(allSchools, 'inst_type_navn');
            const kommuneCounts = countBy(allSchools, 'adm_kommune_navn');

            $('#instTypeFilters').select2({
                data: types.map(type => ({ id: type.inst_type_navn, text: type.inst_type_navn })),
                placeholder: 'Vælg institutionstyper',
                allowClear: true,
                language: SELECT2_DANISH,
                templateResult: option => option.id
                    ? $('<span>').text(`${option.text} (${typeCounts.get(option.id) || 0})`)
                    : option.text,
                templateSelection: option => option.text
            });

            $('#kommuneFilters').select2({
                data: kommuner.map(kommune => ({ id: kommune, text: kommune })),
                placeholder: 'Vælg kommuner',
                allowClear: true,
                language: SELECT2_DANISH,
                templateResult: option => option.id
                    ? $('<span>').text(`${option.text} (${kommuneCounts.get(option.id) || 0})`)
                    : option.text,
                templateSelection: option => option.text
            });

            const defaultType = types.find(type => type.inst_type_nr === '1015');
            if (defaultType) {
                $('#instTypeFilters').val(defaultType.inst_type_navn).trigger('change');
            }
        })
        .catch(error => {
            console.error('Error loading filters:', error);
            showError('Kunne ikke indlæse filtre.');
        });
}

loadSchools()
    .then(loadFilters)
    .then(applyFilters);
