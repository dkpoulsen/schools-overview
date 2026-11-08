const map = L.map('map').setView([56.2639, 9.5018], 7); // Center on Denmark
const loading = document.getElementById('loading');
const schoolCount = document.getElementById('schoolCount');
const filterButton = document.getElementById('filterButton');
const filterPopover = document.getElementById('filterPopover');
const applyFiltersButton = document.getElementById('applyFilters');
const modal = document.getElementById('schoolDetailsModal');
const modalTitle = document.getElementById('modalTitle');
const modalContent = document.getElementById('modalContent');

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let markers;
let allSchools;

filterButton.addEventListener('click', () => {
    filterPopover.style.display = filterPopover.style.display === 'none' ? 'block' : 'none';
});

function loadFilters() {
    return Promise.all([
        fetch('data/inst_types.json').then(response => response.json()),
        fetch('data/kommune_list.json').then(response => response.json()).then(values => values.filter(v => v !== null))
    ])
        .then(([types, kommuner]) => {
            $('#instTypeFilters').select2({
                data: types.map(type => ({ id: type.inst_type_navn, text: type.inst_type_navn })),
                placeholder: 'Select institution types',
                allowClear: true
            });

            $('#kommuneFilters').select2({
                data: kommuner.map(kommune => ({ id: kommune, text: kommune })),
                placeholder: 'Select kommuner',
                allowClear: true
            });

            const type1015 = types.find(type => type.inst_type_nr === '1015');
            if (type1015 != null) {
                $('#instTypeFilters').val(type1015.inst_type_navn).trigger('change');
            }
        })
        .catch(error => {
            console.error('Error loading filters:', error);
            const message = document.createElement('p');
            message.textContent = 'Error loading filters. Please try again later.';
            filterPopover.prepend(message);
        });
}

function loadSchools() {
    loading.style.display = 'block';
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
            schoolCount.textContent = 'Error loading school data';
        })
        .finally(() => {
            loading.style.display = 'none';
        });
}

function displayFilteredSchools(selectedTypes, selectedKommuner) {
    if (markers) {
        map.removeLayer(markers);
    }

    if (!allSchools) {
        return;
    }

    markers = L.markerClusterGroup();

    const filteredSchools = allSchools.filter(school => {
        const instTypeMatch = selectedTypes.length === 0 || selectedTypes.includes(school.inst_type_navn);
        const kommuneMatch = selectedKommuner.length === 0 || selectedKommuner.includes(school.adm_kommune_navn);
        return instTypeMatch && kommuneMatch;
    });

    filteredSchools.forEach(school => {
        const marker = L.marker([school.geo_bredde_grad, school.geo_laengde_grad]);
        marker.bindPopup(createPopupContent(school));
        markers.addLayer(marker);
    });
    map.addLayer(markers);
    schoolCount.textContent = `Total schools displayed: ${filteredSchools.length}`;
}

// popup() takes an HTML string, so CSV values must be escaped.
function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[char]);
}

function createPopupContent(school) {
    return `
        <div class="school-popup">
            <h3>${esc(school.inst_navn)}</h3>
            <p><strong>ID:</strong> ${esc(school.id)}</p>
            <p><strong>Type:</strong> ${esc(school.inst_type_navn)}</p>
            <p><strong>Kommune:</strong> ${esc(school.adm_kommune_navn)}</p>
            <button class="details-btn" data-school-id="${esc(school.id)}">More details</button>
        </div>
    `;
}

function closeModal() {
    modal.style.display = 'none';
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
        return 'N/A';
    }
    const link = document.createElement('a');
    link.href = ensureHttpPrefix(url);
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = url;
    return link;
}

function showSchoolDetails(schoolId) {
    const school = allSchools.find(s => String(s.id) === String(schoolId));
    if (!school) {
        console.error('School not found for id:', schoolId);
        return;
    }

    const address = [school.inst_adr, school.postnr, school.postdistrikt].filter(Boolean).join(', ');

    modalTitle.textContent = school.inst_navn;
    modalContent.replaceChildren(
        detailRow('ID', String(school.id)),
        detailRow('Type', school.inst_type_navn || 'N/A'),
        detailRow('Address', address || 'N/A'),
        detailRow('Phone', school.tlf_nr || 'N/A'),
        detailRow('Email', school.e_mail || 'N/A'),
        detailRow('Website', websiteLink(school.web_adr))
    );

    modal.style.display = 'block';
    modalContent.focus();
}

function ensureHttpPrefix(url) {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        return 'http://' + url;
    }
    return url;
}

function applyFilters() {
    const selectedInstTypes = $('#instTypeFilters').val() || [];
    const selectedKommuner = $('#kommuneFilters').val() || [];
    displayFilteredSchools(selectedInstTypes, selectedKommuner);
    filterPopover.style.display = 'none';
}

applyFiltersButton.addEventListener('click', () => {
    applyFilters();
});

modal.querySelector('.close').addEventListener('click', closeModal);
modal.addEventListener('click', event => {
    if (event.target === modal) {
        closeModal();
    }
});
document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
        closeModal();
    }
});

document.addEventListener('click', event => {
    const detailsButton = event.target.closest('.details-btn');
    if (detailsButton) {
        showSchoolDetails(detailsButton.dataset.schoolId);
        return;
    }
    if (!filterPopover.contains(event.target) && event.target !== filterButton) {
        filterPopover.style.display = 'none';
    }
});

Promise.all([loadSchools(), loadFilters()]).then(() => {
    displayFilteredSchools(
        $('#instTypeFilters').val() || [],
        $('#kommuneFilters').val() || []
    );
});
