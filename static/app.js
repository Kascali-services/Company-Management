// Global state
let currentPage = 0;
let pageSize = 20;
let totalRecords = 0;
let currentSearch = '';
let currentSortBy = 'name';
let currentSortOrder = 'asc';
let currentUnternehmenId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUnternehmen();

    // Form submit handler
    document.getElementById('unternehmenForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveUnternehmen();
    });

    document.getElementById('personForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await savePerson();
    });
});

// Load unternehmen with pagination and filters
async function loadUnternehmen() {
    try {
        const skip = currentPage * pageSize;
        const params = new URLSearchParams({
            skip,
            limit: pageSize,
            sort_by: currentSortBy,
            sort_order: currentSortOrder
        });

        if (currentSearch) {
            params.append('search', currentSearch);
        }

        const response = await fetch(`/api/unternehmen?${params}`);
        const data = await response.json();

        totalRecords = data.total;
        renderTable(data.items);
        renderPagination();
        updateRecordInfo();
    } catch (error) {
        console.error('Error loading data:', error);
        showNotification('Fehler beim Laden der Daten', 'error');
    }
}

// Render table
function renderTable(unternehmen) {
    const tbody = document.getElementById('tableBody');

    if (unternehmen.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-12 text-center text-slate-500">
                    <i class="fas fa-inbox text-4xl mb-4"></i>
                    <p class="text-lg">Keine Unternehmen gefunden</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = unternehmen.map(u => `
        <tr class="hover:bg-slate-50 transition">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-slate-900">${escapeHtml(u.name)}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600">${escapeHtml(u.bundesland)}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600">${escapeHtml(u.stadt)}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600">${escapeHtml(u.plz)}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-slate-600">${escapeHtml(u.strasse)} ${escapeHtml(u.hausnummer)}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button onclick="viewDetails(${u.id})" class="text-blue-600 hover:text-blue-900 mr-3" title="Details">
                    <i class="fas fa-eye"></i>
                </button>
                <button onclick="editUnternehmen(${u.id})" class="text-indigo-600 hover:text-indigo-900 mr-3" title="Bearbeiten">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="deleteUnternehmen(${u.id})" class="text-red-600 hover:text-red-900" title="Löschen">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Render pagination
function renderPagination() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    const pagination = document.getElementById('pagination');

    let html = '';

    // Previous button
    html += `
        <button 
            onclick="previousPage()" 
            ${currentPage === 0 ? 'disabled' : ''}
            class="relative inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-medium rounded-l-md text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
            Zurück
        </button>
    `;

    // Page numbers
    const maxButtons = 5;
    let startPage = Math.max(0, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons);

    if (endPage - startPage < maxButtons) {
        startPage = Math.max(0, endPage - maxButtons);
    }

    for (let i = startPage; i < endPage; i++) {
        html += `
            <button 
                onclick="goToPage(${i})" 
                class="relative inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-medium ${
                    i === currentPage 
                        ? 'bg-blue-600 text-white border-blue-600 z-10' 
                        : 'text-slate-700 bg-white hover:bg-slate-50'
                }"
            >
                ${i + 1}
            </button>
        `;
    }

    // Next button
    html += `
        <button 
            onclick="nextPage()" 
            ${currentPage >= totalPages - 1 ? 'disabled' : ''}
            class="relative inline-flex items-center px-4 py-2 border border-slate-300 text-sm font-medium rounded-r-md text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
            Weiter
        </button>
    `;

    pagination.innerHTML = html;
}

// Update record info
function updateRecordInfo() {
    const from = currentPage * pageSize + 1;
    const to = Math.min((currentPage + 1) * pageSize, totalRecords);

    document.getElementById('showingFrom').textContent = totalRecords > 0 ? from : 0;
    document.getElementById('showingTo').textContent = to;
    document.getElementById('totalRecords').textContent = totalRecords;
}

// Pagination functions
function previousPage() {
    if (currentPage > 0) {
        currentPage--;
        loadUnternehmen();
    }
}

function nextPage() {
    const totalPages = Math.ceil(totalRecords / pageSize);
    if (currentPage < totalPages - 1) {
        currentPage++;
        loadUnternehmen();
    }
}

function goToPage(page) {
    currentPage = page;
    loadUnternehmen();
}

// Search function
let searchTimeout;
function searchUnternehmen() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentSearch = document.getElementById('searchInput').value;
        currentPage = 0;
        loadUnternehmen();
    }, 300);
}

// Sort function
function sortTable(column) {
    if (currentSortBy === column) {
        currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortBy = column;
        currentSortOrder = 'asc';
    }
    loadUnternehmen();
}

// Modal functions
function openCreateModal() {
    document.getElementById('modalTitle').textContent = 'Neues Unternehmen';
    document.getElementById('unternehmenForm').reset();
    document.getElementById('unternehmenId').value = '';
    document.getElementById('unternehmenModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('unternehmenModal').classList.add('hidden');
}

// Save unternehmen
async function saveUnternehmen() {
    const id = document.getElementById('unternehmenId').value;
    const data = {
        name: document.getElementById('name').value,
        bundesland: document.getElementById('bundesland').value,
        stadt: document.getElementById('stadt').value,
        plz: document.getElementById('plz').value,
        strasse: document.getElementById('strasse').value,
        hausnummer: document.getElementById('hausnummer').value,
        ansprechpartner_id: null
    };

    try {
        const url = id ? `/api/unternehmen/${id}` : '/api/unternehmen';
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Speichern');
        }

        closeModal();
        loadUnternehmen();
        showNotification(id ? 'Unternehmen aktualisiert' : 'Unternehmen erstellt', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

// Edit unternehmen
async function editUnternehmen(id) {
    try {
        const response = await fetch(`/api/unternehmen/${id}`);
        const data = await response.json();

        document.getElementById('modalTitle').textContent = 'Unternehmen bearbeiten';
        document.getElementById('unternehmenId').value = data.id;
        document.getElementById('name').value = data.name;
        document.getElementById('bundesland').value = data.bundesland;
        document.getElementById('stadt').value = data.stadt;
        document.getElementById('plz').value = data.plz;
        document.getElementById('strasse').value = data.strasse;
        document.getElementById('hausnummer').value = data.hausnummer;

        document.getElementById('unternehmenModal').classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Fehler beim Laden der Daten', 'error');
    }
}

// Delete unternehmen
async function deleteUnternehmen(id) {
    if (!confirm('Möchten Sie dieses Unternehmen wirklich löschen? Alle zugehörigen Personen werden ebenfalls gelöscht.')) {
        return;
    }

    try {
        const response = await fetch(`/api/unternehmen/${id}`, { method: 'DELETE' });

        if (!response.ok) {
            throw new Error('Fehler beim Löschen');
        }

        loadUnternehmen();
        showNotification('Unternehmen gelöscht', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

// View details
async function viewDetails(id) {
    try {
        const response = await fetch(`/api/unternehmen/${id}`);
        const data = await response.json();

        currentUnternehmenId = id;

        const ansprechpartner = data.ansprechpartner
            ? `${escapeHtml(data.ansprechpartner.vorname)} ${escapeHtml(data.ansprechpartner.nachname)}`
            : '<span class="text-slate-400 italic">Kein Ansprechpartner</span>';

        const empfehlerList = data.personen
            .filter(p => p.rolle === 'Empfehler')
            .map(p => `
                <div class="flex justify-between items-center p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition">
                    <div>
                        <div class="font-medium text-slate-900">${escapeHtml(p.vorname)} ${escapeHtml(p.nachname)}</div>
                        <div class="text-sm text-slate-600">${escapeHtml(p.funktion)}</div>
                        ${p.email ? `<div class="text-sm text-slate-500"><i class="fas fa-envelope mr-1"></i>${escapeHtml(p.email)}</div>` : ''}
                        ${p.telefon ? `<div class="text-sm text-slate-500"><i class="fas fa-phone mr-1"></i>${escapeHtml(p.telefon)}</div>` : ''}
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="editPerson(${p.id})" class="text-indigo-600 hover:text-indigo-900" title="Bearbeiten">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="deletePerson(${p.id})" class="text-red-600 hover:text-red-900" title="Löschen">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `).join('') || '<p class="text-slate-400 italic text-center py-8">Keine Empfehler vorhanden</p>';

        const content = `
            <div class="space-y-6">
                <!-- Company Info -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="text-sm font-medium text-slate-500 uppercase mb-2">Unternehmen</h3>
                        <p class="text-lg font-semibold text-slate-900">${escapeHtml(data.name)}</p>
                    </div>
                    <div>
                        <h3 class="text-sm font-medium text-slate-500 uppercase mb-2">Bundesland</h3>
                        <p class="text-lg text-slate-900">${escapeHtml(data.bundesland)}</p>
                    </div>
                    <div>
                        <h3 class="text-sm font-medium text-slate-500 uppercase mb-2">Adresse</h3>
                        <p class="text-lg text-slate-900">${escapeHtml(data.strasse)} ${escapeHtml(data.hausnummer)}</p>
                        <p class="text-sm text-slate-600">${escapeHtml(data.plz)} ${escapeHtml(data.stadt)}</p>
                    </div>
                </div>
                
                <hr class="border-slate-200">
                
                <!-- Ansprechpartner -->
                <div>
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-bold text-slate-800">Ansprechpartner</h3>
                        ${!data.ansprechpartner ? `
                            <button onclick="openPersonModal(${id}, 'Ansprechpartner')" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm">
                                <i class="fas fa-plus mr-2"></i>Hinzufügen
                            </button>
                        ` : ''}
                    </div>
                    ${data.ansprechpartner ? `
                        <div class="p-4 bg-blue-50 rounded-lg">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="font-medium text-slate-900">${escapeHtml(data.ansprechpartner.vorname)} ${escapeHtml(data.ansprechpartner.nachname)}</div>
                                    <div class="text-sm text-slate-600">${escapeHtml(data.ansprechpartner.funktion)}</div>
                                    ${data.ansprechpartner.email ? `<div class="text-sm text-slate-500"><i class="fas fa-envelope mr-1"></i>${escapeHtml(data.ansprechpartner.email)}</div>` : ''}
                                    ${data.ansprechpartner.telefon ? `<div class="text-sm text-slate-500"><i class="fas fa-phone mr-1"></i>${escapeHtml(data.ansprechpartner.telefon)}</div>` : ''}
                                </div>
                                <div class="flex space-x-2">
                                    <button onclick="editPerson(${data.ansprechpartner.id})" class="text-indigo-600 hover:text-indigo-900" title="Bearbeiten">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button onclick="deletePerson(${data.ansprechpartner.id})" class="text-red-600 hover:text-red-900" title="Löschen">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ` : `<p class="text-slate-400 italic text-center py-8">Kein Ansprechpartner zugewiesen</p>`}
                </div>
                
                <hr class="border-slate-200">
                
                <!-- Empfehler -->
                <div>
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-bold text-slate-800">Empfehler</h3>
                        <button onclick="openPersonModal(${id}, 'Empfehler')" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm">
                            <i class="fas fa-plus mr-2"></i>Hinzufügen
                        </button>
                    </div>
                    <div class="space-y-3">
                        ${empfehlerList}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('detailContent').innerHTML = content;
        document.getElementById('detailModal').classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Fehler beim Laden der Details', 'error');
    }
}

function closeDetailModal() {
    document.getElementById('detailModal').classList.add('hidden');
    currentUnternehmenId = null;
}

// Person modal functions
function openPersonModal(firmaId, rolle = null) {
    document.getElementById('personModalTitle').textContent = 'Person hinzufügen';
    document.getElementById('personForm').reset();
    document.getElementById('personId').value = '';
    document.getElementById('personFirmaId').value = firmaId;

    if (rolle) {
        document.getElementById('personRolle').value = rolle;
        document.getElementById('personRolle').disabled = true;
    } else {
        document.getElementById('personRolle').disabled = false;
    }

    document.getElementById('personModal').classList.remove('hidden');
}

function closePersonModal() {
    document.getElementById('personModal').classList.add('hidden');
}

async function savePerson() {
    const id = document.getElementById('personId').value;
    const firmaId = document.getElementById('personFirmaId').value;
    const data = {
        vorname: document.getElementById('personVorname').value,
        nachname: document.getElementById('personNachname').value,
        email: document.getElementById('personEmail').value || null,
        telefon: document.getElementById('personTelefon').value || null,
        funktion: document.getElementById('personFunktion').value,
        rolle: document.getElementById('personRolle').value
    };

    try {
        let response;
        if (id) {
            response = await fetch(`/api/personen/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch(`/api/unternehmen/${firmaId}/personen`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Fehler beim Speichern');
        }

        closePersonModal();
        if (currentUnternehmenId) {
            viewDetails(currentUnternehmenId);
        }
        showNotification(id ? 'Person aktualisiert' : 'Person erstellt', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

async function editPerson(id) {
    try {
        const response = await fetch(`/api/unternehmen/${currentUnternehmenId}`);
        const unternehmen = await response.json();
        const person = unternehmen.personen.find(p => p.id === id) || unternehmen.ansprechpartner;

        if (!person) {
            throw new Error('Person nicht gefunden');
        }

        document.getElementById('personModalTitle').textContent = 'Person bearbeiten';
        document.getElementById('personId').value = person.id;
        document.getElementById('personFirmaId').value = person.firma_id;
        document.getElementById('personVorname').value = person.vorname;
        document.getElementById('personNachname').value = person.nachname;
        document.getElementById('personEmail').value = person.email || '';
        document.getElementById('personTelefon').value = person.telefon || '';
        document.getElementById('personFunktion').value = person.funktion;
        document.getElementById('personRolle').value = person.rolle;
        document.getElementById('personRolle').disabled = false;

        document.getElementById('personModal').classList.remove('hidden');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Fehler beim Laden der Person', 'error');
    }
}

async function deletePerson(id) {
    if (!confirm('Möchten Sie diese Person wirklich löschen?')) {
        return;
    }

    try {
        const response = await fetch(`/api/personen/${id}`, { method: 'DELETE' });

        if (!response.ok) {
            throw new Error('Fehler beim Löschen');
        }

        if (currentUnternehmenId) {
            viewDetails(currentUnternehmenId);
        }
        showNotification('Person gelöscht', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message, 'error');
    }
}

// Export functions
async function exportData(format) {
    try {
        const url = format === 'csv' ? '/api/export/csv' : '/api/export/excel';
        window.location.href = url;
        showNotification(`${format.toUpperCase()} Export gestartet`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Fehler beim Export', 'error');
    }
}

// Utility functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.toString().replace(/[&<>"']/g, m => map[m]) : '';
}

function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-300`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}