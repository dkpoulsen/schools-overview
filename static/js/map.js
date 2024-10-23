const map = L.map('map').setView([56.2639, 9.5018], 7); // Center on Denmark
const loading = document.getElementById('loading');
const schoolCount = document.getElementById('schoolCount');
const filterButton = document.getElementById('filterButton');
const filterPopover = document.getElementById('filterPopover');
const instTypeFilters = document.getElementById('instTypeFilters');
const applyFiltersButton = document.getElementById('applyFilters');

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let markers;
let allSchools;

filterButton.addEventListener('click', () => {
    filterPopover.style.display = filterPopover.style.display === 'none' ? 'block' : 'none';
});

let instTypes = [];
let kommuneList = [];

function loadFilters() {
    Promise.all([
        fetch('/api/inst_types').then(response => response.json()),
        fetch('/api/kommune_list').then(response => response.json()).then(values => values.filter(v => v !== null))
    ])
        .then(([types, kommuner]) => {
            instTypes = types;
            kommuneList = kommuner;

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
        })
        .catch(error => {
            console.error('Error loading filters:', error);
            instTypeFilters.innerHTML = '<p>Error loading filters. Please try again later.</p>';
            kommuneFilters.innerHTML = '<p>Error loading filters. Please try again later.</p>';
        });
}

function loadSchools(filters = []) {
    f
    loading.style.display = 'block';
    fetch('/api/school_locations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(schools => {
            allSchools = schools;
            displayFilteredSchools(filters);
        })
        .catch(error => {
            console.error('Error fetching school locations:', error);
            schoolCount.textContent = 'Error loading school data';
        })
        .finally(() => {
            loading.style.display = 'none';
        });
}

function displayFilteredSchools(instTypeFilters, kommuneFilters) {
    if (markers) {
        map.removeLayer(markers);
    }
    markers = L.markerClusterGroup();

    const filteredSchools = allSchools.filter(school => {
        const instTypeMatch = instTypeFilters.length === 0 || instTypeFilters.includes(school.inst_type_navn);
        const kommuneMatch = kommuneFilters.length === 0 || kommuneFilters.includes(school.adm_kommune_navn);
        return instTypeMatch && kommuneMatch;
    });

    filteredSchools.forEach(school => {
        const marker = L.marker([school.geo_bredde_grad, school.geo_laengde_grad]);
        marker.bindPopup(createPopupContent(school));
        marker.on('click', () => {
            marker.openPopup();
        });
        markers.addLayer(marker);
    });
    map.addLayer(markers);
    schoolCount.textContent = `Total schools displayed: ${filteredSchools.length}`;

    console.log('Filtered schools:', filteredSchools);
    console.log('Applied inst_type filters:', instTypeFilters);
    console.log('Applied kommune filters:', kommuneFilters);
}

function createPopupContent(school) {
    return `
        <div class="school-popup">
            <h3>${school.inst_navn}</h3>
            <p><strong>ID:</strong> ${school.id}</p>
            <p><strong>Type:</strong> ${school.inst_type_navn}</p>
            <p><strong>Kommune:</strong> ${school.adm_kommune_navn}</p>
            <button onclick="showSchoolDetails(${school.id})">More details</button>
        </div>
    `;
}

function showSchoolDetails(schoolId) {
    fetch(`/api/school/${schoolId}`)
        .then(response => response.json())
        .then(school => {
            const modal = document.getElementById('schoolDetailsModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalContent = document.getElementById('modalContent');

            modalTitle.textContent = school.inst_navn;
            modalContent.innerHTML = `
                <p><strong>ID:</strong> ${school.id}</p>
                <p><strong>Type:</strong> ${school.inst_type_navn}</p>
                <p><strong>Address:</strong> ${school.inst_adr}, ${school.postnr} ${school.postdistrikt}</p>
                <p><strong>Phone:</strong> ${school.tlf_nr || 'N/A'}</p>
                <p><strong>Email:</strong> ${school.e_mail || 'N/A'}</p>
                <p><strong>Website:</strong> ${school.web_adr ? `<a href="${ensureHttpPrefix(school.web_adr)}" target="_blank" rel="noopener noreferrer">${school.web_adr}</a>` : 'N/A'}</p>
            `;

            modal.style.display = 'block';

            const closeBtn = modal.querySelector('.close');
            closeBtn.onclick = function () {
                modal.style.display = 'none';
            }

            window.onclick = function (event) {
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching school details:', error);
        });
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
    console.log('Selected inst_types:', selectedInstTypes);
    console.log('Selected kommuner:', selectedKommuner);
}

function loadSchools() {
    loading.style.display = 'block';
    fetch('/api/school_locations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(schools => {
            allSchools = schools;
            displayFilteredSchools([], []); // Display all schools initially
        })
        .catch(error => {
            console.error('Error fetching school locations:', error);
            schoolCount.textContent = 'Error loading school data';
        })
        .finally(() => {
            loading.style.display = 'none';
        });
}

function applyFilters(event) {
    const selectedInstTypes = $('#instTypeFilters').val();
    const selectedKommuner = $('#kommuneFilters').val();
    displayFilteredSchools(selectedInstTypes, selectedKommuner);
    filterPopover.style.display = 'none';
    console.log('Selected inst_types:', selectedInstTypes);
    console.log('Selected kommuner:', selectedKommuner);
}

function showSchoolDetails(schoolId) {
    fetch(`/api/school/${schoolId}`)
        .then(response => response.json())
        .then(school => {
            const modal = document.getElementById('schoolDetailsModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalContent = document.getElementById('modalContent');

            modalTitle.textContent = school.inst_navn;
            modalContent.innerHTML = `
                <p><strong>ID:</strong> ${school.id}</p>
                <p><strong>Type:</strong> ${school.inst_type_navn}</p>
                <p><strong>Address:</strong> ${school.inst_adr}, ${school.postnr} ${school.postdistrikt}</p>
                <p><strong>Phone:</strong> ${school.tlf_nr || 'N/A'}</p>
                <p><strong>Email:</strong> ${school.e_mail || 'N/A'}</p>
                <p><strong>Website:</strong> ${school.web_adr ? `<a href="${school.web_adr}" target="_blank">${school.web_adr}</a>` : 'N/A'}</p>
            `;

            modal.style.display = 'block';

            const closeBtn = modal.querySelector('.close');
            closeBtn.onclick = function () {
                modal.style.display = 'none';
            }

            window.onclick = function (event) {
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching school details:', error);
        });
}

applyFiltersButton.addEventListener('click', () => {
    applyFilters();
});

// Close popover when clicking outside
document.addEventListener('click', (event) => {
    if (!filterPopover.contains(event.target) && event.target !== filterButton) {
        filterPopover.style.display = 'none';
    }
});

loadFilters();
loadSchools();
