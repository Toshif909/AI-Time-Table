/* ═══════════════════════════════════════════════════════════
   AI TIMETABLE GENERATOR — Complete Frontend Application
   SPA Router, API Client, Page Renderers, Timetable Grid
   ═══════════════════════════════════════════════════════════ */

// ── Configuration ──
const API = '/api';
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const TIME_SLOTS = [
    '10:00 - 11:00', '11:00 - 12:00', '12:00 - 01:00',
    '02:00 - 03:00', '03:00 - 04:00', '04:00 - 05:00', '05:00 - 06:00'
];
const SUBJECT_COLORS = [
    '#667eea', '#06b6d4', '#8b5cf6', '#10b981',
    '#f59e0b', '#ec4899', '#ef4444', '#22d3ee',
    '#a78bfa', '#34d399', '#fb923c', '#f472b6'
];

// ── State ──
let state = {
    page: 'dashboard',
    faculty: [],
    subjects: [],
    rooms: [],
    classes: [],
    timetables: [],
    currentTimetable: null,
    facultySubjects: [],
    classSubjects: [],
    stats: {},
    dataTab: 'faculty'
};


/* ═══════════════════════════════════════════════════════════
   API CLIENT
   ═══════════════════════════════════════════════════════════ */

async function api(endpoint, options = {}) {
    const url = `${API}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }
    try {
        const res = await fetch(url, config);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'Request failed');
        }
        return await res.json();
    } catch (e) {
        console.error(`API Error [${endpoint}]:`, e);
        throw e;
    }
}

const API_METHODS = {
    getStats: () => api('/stats'),
    getFaculty: () => api('/faculty'),
    createFaculty: (data) => api('/faculty', { method: 'POST', body: data }),
    updateFaculty: (id, data) => api(`/faculty/${id}`, { method: 'PUT', body: data }),
    deleteFaculty: (id) => api(`/faculty/${id}`, { method: 'DELETE' }),
    getSubjects: () => api('/subjects'),
    createSubject: (data) => api('/subjects', { method: 'POST', body: data }),
    updateSubject: (id, data) => api(`/subjects/${id}`, { method: 'PUT', body: data }),
    deleteSubject: (id) => api(`/subjects/${id}`, { method: 'DELETE' }),
    getRooms: () => api('/rooms'),
    createRoom: (data) => api('/rooms', { method: 'POST', body: data }),
    updateRoom: (id, data) => api(`/rooms/${id}`, { method: 'PUT', body: data }),
    deleteRoom: (id) => api(`/rooms/${id}`, { method: 'DELETE' }),
    getClasses: () => api('/classes'),
    createClass: (data) => api('/classes', { method: 'POST', body: data }),
    updateClass: (id, data) => api(`/classes/${id}`, { method: 'PUT', body: data }),
    deleteClass: (id) => api(`/classes/${id}`, { method: 'DELETE' }),
    getFacultySubjects: () => api('/faculty-subjects'),
    createFacultySubject: (data) => api('/faculty-subjects', { method: 'POST', body: data }),
    deleteFacultySubject: (id) => api(`/faculty-subjects/${id}`, { method: 'DELETE' }),
    getClassSubjects: () => api('/class-subjects'),
    createClassSubject: (data) => api('/class-subjects', { method: 'POST', body: data }),
    deleteClassSubject: (id) => api(`/class-subjects/${id}`, { method: 'DELETE' }),
    generateTimetable: (data) => api('/generate', { method: 'POST', body: data }),
    getTimetables: () => api('/timetables'),
    getTimetable: (id) => api(`/timetables/${id}`),
    deleteTimetable: (id) => api(`/timetables/${id}`, { method: 'DELETE' }),
    getConflicts: (id) => api(`/timetables/${id}/conflicts`),
};


/* ═══════════════════════════════════════════════════════════
   ROUTER
   ═══════════════════════════════════════════════════════════ */

function navigateTo(page) {
    state.page = page;
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });
    renderPage(page);
}

async function renderPage(page) {
    const container = document.getElementById('page-container');
    container.innerHTML = '<div class="page-loader"><div class="loader-spinner"></div><p>Loading...</p></div>';
    container.style.animation = 'none';
    void container.offsetHeight;
    container.style.animation = 'fadeInUp 0.4s ease';

    try {
        switch (page) {
            case 'dashboard': await renderDashboard(container); break;
            case 'data': await renderDataManagement(container); break;
            case 'generate': await renderGenerate(container); break;
            case 'timetable': await renderTimetable(container); break;
            case 'conflicts': await renderConflicts(container); break;
            case 'export': await renderExport(container); break;
            default: container.innerHTML = '<p>Page not found</p>';
        }
    } catch (e) {
        container.innerHTML = `<div class="empty-state"><p>Error loading page: ${e.message}</p><button class="btn btn-secondary mt-2" onclick="renderPage('${page}')">Retry</button></div>`;
    }
}


/* ═══════════════════════════════════════════════════════════
   DASHBOARD PAGE
   ═══════════════════════════════════════════════════════════ */

async function renderDashboard(container) {
    const [stats, timetables] = await Promise.all([
        API_METHODS.getStats(),
        API_METHODS.getTimetables()
    ]);
    state.stats = stats;
    state.timetables = timetables;

    container.innerHTML = `
        <div class="page-header">
            <h2>📊 Dashboard</h2>
            <p>AI Timetable Generation System — Overview & Quick Actions</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card indigo">
                <div class="stat-icon">👨‍🏫</div>
                <div class="stat-value">${stats.total_faculty}</div>
                <div class="stat-label">Faculty Members</div>
            </div>
            <div class="stat-card cyan">
                <div class="stat-icon">📚</div>
                <div class="stat-value">${stats.total_subjects}</div>
                <div class="stat-label">Subjects</div>
            </div>
            <div class="stat-card emerald">
                <div class="stat-icon">🏫</div>
                <div class="stat-value">${stats.total_rooms}</div>
                <div class="stat-label">Rooms</div>
            </div>
            <div class="stat-card amber">
                <div class="stat-icon">🎓</div>
                <div class="stat-value">${stats.total_classes}</div>
                <div class="stat-label">Classes</div>
            </div>
            <div class="stat-card rose">
                <div class="stat-icon">📋</div>
                <div class="stat-value">${stats.total_timetables}</div>
                <div class="stat-label">Generated Timetables</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-icon">🔗</div>
                <div class="stat-value">${stats.total_assignments}</div>
                <div class="stat-label">Assignments</div>
            </div>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <h3>⚡ Quick Actions</h3>
                </div>
                <div class="card-body">
                    <button class="btn btn-primary btn-lg w-full mb-2" onclick="navigateTo('generate')" id="quick-generate-btn">
                        🧠 Generate New Timetable
                    </button>
                    <button class="btn btn-secondary w-full mb-2" onclick="navigateTo('data')">
                        📝 Manage Data
                    </button>
                    <button class="btn btn-secondary w-full" onclick="navigateTo('timetable')">
                        📅 View Timetables
                    </button>
                </div>
            </div>
            <div class="card">
                <div class="card-header">
                    <h3>📋 Recent Timetables</h3>
                </div>
                <div class="card-body">
                    ${timetables.length === 0 ? `
                        <div class="empty-state" style="padding: 24px 0;">
                            <p>No timetables generated yet</p>
                            <p class="text-sm text-muted">Click "Generate" to create your first timetable</p>
                        </div>
                    ` : timetables.slice(0, 5).map(tt => `
                        <div class="recent-item" style="cursor:pointer;" onclick="viewTimetableById(${tt.id})">
                            <div class="recent-info">
                                <h4>${escapeHtml(tt.name)}</h4>
                                <p>${tt.created_at} • ${tt.entry_count} entries</p>
                            </div>
                            <div class="recent-score">${tt.fitness_score.toFixed(1)}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        <div class="card mt-3">
            <div class="card-header">
                <h3>ℹ️ System Information</h3>
            </div>
            <div class="card-body">
                <div class="form-row" style="grid-template-columns: repeat(3, 1fr);">
                    <div>
                        <p class="text-sm text-muted">Theory Subjects</p>
                        <p style="font-weight:600;">${stats.theory_subjects}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted">Lab / Project Subjects</p>
                        <p style="font-weight:600;">${stats.lab_subjects}</p>
                    </div>
                    <div>
                        <p class="text-sm text-muted">Lab Rooms</p>
                        <p style="font-weight:600;">${stats.lab_rooms}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function viewTimetableById(id) {
    state.currentTimetable = await API_METHODS.getTimetable(id);
    navigateTo('timetable');
}


/* ═══════════════════════════════════════════════════════════
   DATA MANAGEMENT PAGE
   ═══════════════════════════════════════════════════════════ */

async function renderDataManagement(container) {
    const [faculty, subjects, rooms, classes, fs, cs] = await Promise.all([
        API_METHODS.getFaculty(),
        API_METHODS.getSubjects(),
        API_METHODS.getRooms(),
        API_METHODS.getClasses(),
        API_METHODS.getFacultySubjects(),
        API_METHODS.getClassSubjects(),
    ]);
    state.faculty = faculty;
    state.subjects = subjects;
    state.rooms = rooms;
    state.classes = classes;
    state.facultySubjects = fs;
    state.classSubjects = cs;

    container.innerHTML = `
        <div class="page-header">
            <h2>📝 Data Management</h2>
            <p>Manage faculty, subjects, rooms, classes, and their assignments</p>
        </div>

        <div class="tabs" id="data-tabs">
            <button class="tab-btn ${state.dataTab === 'faculty' ? 'active' : ''}" onclick="switchDataTab('faculty')">👨‍🏫 Faculty (${faculty.length})</button>
            <button class="tab-btn ${state.dataTab === 'subjects' ? 'active' : ''}" onclick="switchDataTab('subjects')">📚 Subjects (${subjects.length})</button>
            <button class="tab-btn ${state.dataTab === 'rooms' ? 'active' : ''}" onclick="switchDataTab('rooms')">🏫 Rooms (${rooms.length})</button>
            <button class="tab-btn ${state.dataTab === 'classes' ? 'active' : ''}" onclick="switchDataTab('classes')">🎓 Classes (${classes.length})</button>
            <button class="tab-btn ${state.dataTab === 'faculty-subjects' ? 'active' : ''}" onclick="switchDataTab('faculty-subjects')">🔗 Faculty–Subject (${fs.length})</button>
            <button class="tab-btn ${state.dataTab === 'class-subjects' ? 'active' : ''}" onclick="switchDataTab('class-subjects')">📎 Class–Subject (${cs.length})</button>
        </div>

        <div id="data-tab-content"></div>
    `;

    switchDataTab(state.dataTab);
}

function switchDataTab(tab) {
    state.dataTab = tab;
    document.querySelectorAll('.tab-btn').forEach((btn, i) => {
        const tabs = ['faculty', 'subjects', 'rooms', 'classes', 'faculty-subjects', 'class-subjects'];
        btn.classList.toggle('active', tabs[i] === tab);
    });
    const content = document.getElementById('data-tab-content');
    if (!content) return;

    switch (tab) {
        case 'faculty': renderFacultyTab(content); break;
        case 'subjects': renderSubjectsTab(content); break;
        case 'rooms': renderRoomsTab(content); break;
        case 'classes': renderClassesTab(content); break;
        case 'faculty-subjects': renderFacultySubjectsTab(content); break;
        case 'class-subjects': renderClassSubjectsTab(content); break;
    }
}

// ── Faculty Tab ──
function renderFacultyTab(el) {
    el.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>Faculty Members</h3>
                <button class="btn btn-primary btn-sm" onclick="openFacultyModal()">+ Add Faculty</button>
            </div>
            <div class="card-body">
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr><th>Code</th><th>Name</th><th>Department</th><th>Designation</th><th>Max Hrs/Day</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${state.faculty.map(f => `
                                <tr>
                                    <td><strong>${escapeHtml(f.code)}</strong></td>
                                    <td>${escapeHtml(f.name)}</td>
                                    <td>${escapeHtml(f.department)}</td>
                                    <td>${escapeHtml(f.designation)}</td>
                                    <td>${f.max_hours_per_day}</td>
                                    <td class="action-btns">
                                        <button class="btn btn-ghost btn-sm" onclick="openFacultyModal(${f.id})">✏️</button>
                                        <button class="btn btn-ghost btn-sm" onclick="deleteEntity('faculty', ${f.id}, '${escapeHtml(f.name)}')">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${state.faculty.length === 0 ? '<div class="empty-state"><p>No faculty added yet</p></div>' : ''}
                </div>
            </div>
        </div>
    `;
}

// ── Subjects Tab ──
function renderSubjectsTab(el) {
    el.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>Subjects / Courses</h3>
                <button class="btn btn-primary btn-sm" onclick="openSubjectModal()">+ Add Subject</button>
            </div>
            <div class="card-body">
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr><th>Code</th><th>Name</th><th>Type</th><th>Hrs/Week</th><th>Color</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${state.subjects.map(s => `
                                <tr>
                                    <td><strong>${escapeHtml(s.code)}</strong></td>
                                    <td>${escapeHtml(s.name)}</td>
                                    <td><span class="badge badge-${s.subject_type}">${s.subject_type}</span></td>
                                    <td>${s.hours_per_week}</td>
                                    <td><span class="color-dot" style="background:${s.color};"></span>${s.color}</td>
                                    <td class="action-btns">
                                        <button class="btn btn-ghost btn-sm" onclick="openSubjectModal(${s.id})">✏️</button>
                                        <button class="btn btn-ghost btn-sm" onclick="deleteEntity('subjects', ${s.id}, '${escapeHtml(s.name)}')">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${state.subjects.length === 0 ? '<div class="empty-state"><p>No subjects added yet</p></div>' : ''}
                </div>
            </div>
        </div>
    `;
}

// ── Rooms Tab ──
function renderRoomsTab(el) {
    el.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>Rooms & Labs</h3>
                <button class="btn btn-primary btn-sm" onclick="openRoomModal()">+ Add Room</button>
            </div>
            <div class="card-body">
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr><th>Name</th><th>Building</th><th>Capacity</th><th>Type</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${state.rooms.map(r => `
                                <tr>
                                    <td><strong>${escapeHtml(r.name)}</strong></td>
                                    <td>${escapeHtml(r.building)}</td>
                                    <td>${r.capacity}</td>
                                    <td><span class="badge ${r.is_lab ? 'badge-lab' : 'badge-theory'}">${r.is_lab ? 'Lab' : 'Classroom'}</span></td>
                                    <td class="action-btns">
                                        <button class="btn btn-ghost btn-sm" onclick="openRoomModal(${r.id})">✏️</button>
                                        <button class="btn btn-ghost btn-sm" onclick="deleteEntity('rooms', ${r.id}, '${escapeHtml(r.name)}')">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${state.rooms.length === 0 ? '<div class="empty-state"><p>No rooms added yet</p></div>' : ''}
                </div>
            </div>
        </div>
    `;
}

// ── Classes Tab ──
function renderClassesTab(el) {
    el.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>Classes / Sections</h3>
                <button class="btn btn-primary btn-sm" onclick="openClassModal()">+ Add Class</button>
            </div>
            <div class="card-body">
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr><th>Name</th><th>Branch</th><th>Semester</th><th>Students</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${state.classes.map(c => `
                                <tr>
                                    <td><strong>${escapeHtml(c.name)}</strong></td>
                                    <td>${escapeHtml(c.branch)}</td>
                                    <td>${c.semester}</td>
                                    <td>${c.student_count}</td>
                                    <td class="action-btns">
                                        <button class="btn btn-ghost btn-sm" onclick="openClassModal(${c.id})">✏️</button>
                                        <button class="btn btn-ghost btn-sm" onclick="deleteEntity('classes', ${c.id}, '${escapeHtml(c.name)}')">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${state.classes.length === 0 ? '<div class="empty-state"><p>No classes added yet</p></div>' : ''}
                </div>
            </div>
        </div>
    `;
}

// ── Faculty-Subject Assignments Tab ──
function renderFacultySubjectsTab(el) {
    el.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>Faculty ↔ Subject Assignments</h3>
                <button class="btn btn-primary btn-sm" onclick="openFacultySubjectModal()">+ Assign Faculty</button>
            </div>
            <div class="card-body">
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr><th>Faculty</th><th>Code</th><th>Subject</th><th>Subject Code</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${state.facultySubjects.map(a => `
                                <tr>
                                    <td>${escapeHtml(a.faculty_name || '')}</td>
                                    <td><strong>${escapeHtml(a.faculty_code || '')}</strong></td>
                                    <td>${escapeHtml(a.subject_name || '')}</td>
                                    <td>${escapeHtml(a.subject_code || '')}</td>
                                    <td>
                                        <button class="btn btn-ghost btn-sm" onclick="deleteFacultySubject(${a.id})">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${state.facultySubjects.length === 0 ? '<div class="empty-state"><p>No assignments yet</p></div>' : ''}
                </div>
            </div>
        </div>
    `;
}

// ── Class-Subject Assignments Tab ──
function renderClassSubjectsTab(el) {
    el.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>Class ↔ Subject Assignments</h3>
                <button class="btn btn-primary btn-sm" onclick="openClassSubjectModal()">+ Assign Subject</button>
            </div>
            <div class="card-body">
                <div class="data-table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr><th>Class</th><th>Subject</th><th>Code</th><th>Hrs/Week</th><th>Actions</th></tr>
                        </thead>
                        <tbody>
                            ${state.classSubjects.map(a => `
                                <tr>
                                    <td><strong>${escapeHtml(a.class_name || '')}</strong></td>
                                    <td>${escapeHtml(a.subject_name || '')}</td>
                                    <td>${escapeHtml(a.subject_code || '')}</td>
                                    <td>${a.hours_per_week}</td>
                                    <td>
                                        <button class="btn btn-ghost btn-sm" onclick="deleteClassSubject(${a.id})">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                    ${state.classSubjects.length === 0 ? '<div class="empty-state"><p>No assignments yet</p></div>' : ''}
                </div>
            </div>
        </div>
    `;
}


/* ═══════════════════════════════════════════════════════════
   MODALS — CRUD FORMS
   ═══════════════════════════════════════════════════════════ */

function openModal(title, bodyHtml) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ── Faculty Modal ──
function openFacultyModal(id) {
    const f = id ? state.faculty.find(x => x.id === id) : null;
    openModal(f ? 'Edit Faculty' : 'Add Faculty', `
        <form onsubmit="saveFaculty(event, ${id || 'null'})">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input class="form-input" id="f-name" value="${f ? escapeHtml(f.name) : ''}" required placeholder="Dr. John Smith">
                </div>
                <div class="form-group">
                    <label class="form-label">Code *</label>
                    <input class="form-input" id="f-code" value="${f ? escapeHtml(f.code) : ''}" required placeholder="JS" maxlength="10">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Department</label>
                    <input class="form-input" id="f-dept" value="${f ? escapeHtml(f.department) : 'Centre for AI'}" placeholder="Centre for AI">
                </div>
                <div class="form-group">
                    <label class="form-label">Designation</label>
                    <input class="form-input" id="f-desig" value="${f ? escapeHtml(f.designation) : 'Assistant Professor'}" placeholder="Assistant Professor">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Max Hours/Day</label>
                    <input class="form-input" type="number" id="f-maxhrs" value="${f ? f.max_hours_per_day : 6}" min="1" max="10">
                </div>
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input class="form-input" type="email" id="f-email" value="${f ? escapeHtml(f.email) : ''}" placeholder="email@university.edu">
                </div>
            </div>
            <div class="flex justify-between mt-2">
                <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">${f ? 'Update' : 'Add'} Faculty</button>
            </div>
        </form>
    `);
}

async function saveFaculty(e, id) {
    e.preventDefault();
    const data = {
        name: document.getElementById('f-name').value,
        code: document.getElementById('f-code').value.toUpperCase(),
        department: document.getElementById('f-dept').value,
        designation: document.getElementById('f-desig').value,
        max_hours_per_day: parseInt(document.getElementById('f-maxhrs').value),
        email: document.getElementById('f-email').value,
    };
    try {
        if (id) await API_METHODS.updateFaculty(id, data);
        else await API_METHODS.createFaculty(data);
        closeModal();
        showToast(id ? 'Faculty updated' : 'Faculty added', 'success');
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

// ── Subject Modal ──
function openSubjectModal(id) {
    const s = id ? state.subjects.find(x => x.id === id) : null;
    openModal(s ? 'Edit Subject' : 'Add Subject', `
        <form onsubmit="saveSubject(event, ${id || 'null'})">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input class="form-input" id="s-name" value="${s ? escapeHtml(s.name) : ''}" required placeholder="Machine Learning">
                </div>
                <div class="form-group">
                    <label class="form-label">Code *</label>
                    <input class="form-input" id="s-code" value="${s ? escapeHtml(s.code) : ''}" required placeholder="CS401">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Type</label>
                    <select class="form-select" id="s-type">
                        <option value="theory" ${s?.subject_type === 'theory' ? 'selected' : ''}>Theory</option>
                        <option value="lab" ${s?.subject_type === 'lab' ? 'selected' : ''}>Lab</option>
                        <option value="project" ${s?.subject_type === 'project' ? 'selected' : ''}>Project</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Hours/Week</label>
                    <input class="form-input" type="number" id="s-hrs" value="${s ? s.hours_per_week : 3}" min="1" max="10">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Color</label>
                <div class="color-picker-wrapper">
                    <input type="color" id="s-color" value="${s ? s.color : SUBJECT_COLORS[Math.floor(Math.random() * SUBJECT_COLORS.length)]}">
                    <span class="text-sm text-muted">Pick a display color for the timetable grid</span>
                </div>
            </div>
            <div class="flex justify-between mt-2">
                <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">${s ? 'Update' : 'Add'} Subject</button>
            </div>
        </form>
    `);
}

async function saveSubject(e, id) {
    e.preventDefault();
    const data = {
        name: document.getElementById('s-name').value,
        code: document.getElementById('s-code').value,
        subject_type: document.getElementById('s-type').value,
        hours_per_week: parseInt(document.getElementById('s-hrs').value),
        color: document.getElementById('s-color').value,
    };
    try {
        if (id) await API_METHODS.updateSubject(id, data);
        else await API_METHODS.createSubject(data);
        closeModal();
        showToast(id ? 'Subject updated' : 'Subject added', 'success');
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

// ── Room Modal ──
function openRoomModal(id) {
    const r = id ? state.rooms.find(x => x.id === id) : null;
    openModal(r ? 'Edit Room' : 'Add Room', `
        <form onsubmit="saveRoom(event, ${id || 'null'})">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input class="form-input" id="r-name" value="${r ? escapeHtml(r.name) : ''}" required placeholder="M101">
                </div>
                <div class="form-group">
                    <label class="form-label">Building</label>
                    <input class="form-input" id="r-building" value="${r ? escapeHtml(r.building) : 'New Academic Block'}" placeholder="Main Block">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Capacity</label>
                    <input class="form-input" type="number" id="r-cap" value="${r ? r.capacity : 60}" min="1">
                </div>
                <div class="form-group" style="display:flex;align-items:flex-end;">
                    <label class="form-check">
                        <input type="checkbox" id="r-lab" ${r?.is_lab ? 'checked' : ''}>
                        <span>This is a Lab</span>
                    </label>
                </div>
            </div>
            <div class="flex justify-between mt-2">
                <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">${r ? 'Update' : 'Add'} Room</button>
            </div>
        </form>
    `);
}

async function saveRoom(e, id) {
    e.preventDefault();
    const data = {
        name: document.getElementById('r-name').value,
        capacity: parseInt(document.getElementById('r-cap').value),
        is_lab: document.getElementById('r-lab').checked,
        building: document.getElementById('r-building').value,
    };
    try {
        if (id) await API_METHODS.updateRoom(id, data);
        else await API_METHODS.createRoom(data);
        closeModal();
        showToast(id ? 'Room updated' : 'Room added', 'success');
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

// ── Class Modal ──
function openClassModal(id) {
    const c = id ? state.classes.find(x => x.id === id) : null;
    openModal(c ? 'Edit Class' : 'Add Class', `
        <form onsubmit="saveClass(event, ${id || 'null'})">
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input class="form-input" id="c-name" value="${c ? escapeHtml(c.name) : ''}" required placeholder="CS-VI">
                </div>
                <div class="form-group">
                    <label class="form-label">Branch *</label>
                    <input class="form-input" id="c-branch" value="${c ? escapeHtml(c.branch) : ''}" required placeholder="Computer Science">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Semester</label>
                    <input class="form-input" type="number" id="c-sem" value="${c ? c.semester : 6}" min="1" max="8">
                </div>
                <div class="form-group">
                    <label class="form-label">Student Count</label>
                    <input class="form-input" type="number" id="c-students" value="${c ? c.student_count : 60}" min="1">
                </div>
            </div>
            <div class="flex justify-between mt-2">
                <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">${c ? 'Update' : 'Add'} Class</button>
            </div>
        </form>
    `);
}

async function saveClass(e, id) {
    e.preventDefault();
    const data = {
        name: document.getElementById('c-name').value,
        branch: document.getElementById('c-branch').value,
        semester: parseInt(document.getElementById('c-sem').value),
        student_count: parseInt(document.getElementById('c-students').value),
    };
    try {
        if (id) await API_METHODS.updateClass(id, data);
        else await API_METHODS.createClass(data);
        closeModal();
        showToast(id ? 'Class updated' : 'Class added', 'success');
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

// ── Faculty-Subject Assignment Modal ──
function openFacultySubjectModal() {
    openModal('Assign Faculty to Subject', `
        <form onsubmit="saveFacultySubject(event)">
            <div class="form-group">
                <label class="form-label">Faculty *</label>
                <select class="form-select" id="fs-faculty" required>
                    <option value="">Select Faculty...</option>
                    ${state.faculty.map(f => `<option value="${f.id}">${f.name} (${f.code})</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Subject *</label>
                <select class="form-select" id="fs-subject" required>
                    <option value="">Select Subject...</option>
                    ${state.subjects.map(s => `<option value="${s.id}">${s.name} (${s.code})</option>`).join('')}
                </select>
            </div>
            <div class="flex justify-between mt-2">
                <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Assign</button>
            </div>
        </form>
    `);
}

async function saveFacultySubject(e) {
    e.preventDefault();
    try {
        await API_METHODS.createFacultySubject({
            faculty_id: parseInt(document.getElementById('fs-faculty').value),
            subject_id: parseInt(document.getElementById('fs-subject').value),
        });
        closeModal();
        showToast('Faculty-Subject assigned', 'success');
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

async function deleteFacultySubject(id) {
    if (!confirm('Remove this assignment?')) return;
    try {
        await API_METHODS.deleteFacultySubject(id);
        showToast('Assignment removed', 'success');
        state.dataTab = 'faculty-subjects';
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

// ── Class-Subject Assignment Modal ──
function openClassSubjectModal() {
    openModal('Assign Subject to Class', `
        <form onsubmit="saveClassSubject(event)">
            <div class="form-group">
                <label class="form-label">Class *</label>
                <select class="form-select" id="cs-class" required>
                    <option value="">Select Class...</option>
                    ${state.classes.map(c => `<option value="${c.id}">${c.name} — ${c.branch}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Subject *</label>
                <select class="form-select" id="cs-subject" required>
                    <option value="">Select Subject...</option>
                    ${state.subjects.map(s => `<option value="${s.id}">${s.name} (${s.code})</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Hours per Week</label>
                <input class="form-input" type="number" id="cs-hrs" value="3" min="1" max="10">
            </div>
            <div class="flex justify-between mt-2">
                <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Assign</button>
            </div>
        </form>
    `);
}

async function saveClassSubject(e) {
    e.preventDefault();
    try {
        await API_METHODS.createClassSubject({
            class_id: parseInt(document.getElementById('cs-class').value),
            subject_id: parseInt(document.getElementById('cs-subject').value),
            hours_per_week: parseInt(document.getElementById('cs-hrs').value),
        });
        closeModal();
        showToast('Class-Subject assigned', 'success');
        state.dataTab = 'class-subjects';
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

async function deleteClassSubject(id) {
    if (!confirm('Remove this assignment?')) return;
    try {
        await API_METHODS.deleteClassSubject(id);
        showToast('Assignment removed', 'success');
        state.dataTab = 'class-subjects';
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}

// ── Generic Delete ──
async function deleteEntity(type, id, name) {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;
    try {
        const methods = {
            faculty: API_METHODS.deleteFaculty,
            subjects: API_METHODS.deleteSubject,
            rooms: API_METHODS.deleteRoom,
            classes: API_METHODS.deleteClass,
        };
        await methods[type](id);
        showToast(`${name} deleted`, 'success');
        state.dataTab = type;
        await renderDataManagement(document.getElementById('page-container'));
    } catch (err) { showToast(err.message, 'error'); }
}


/* ═══════════════════════════════════════════════════════════
   GENERATE TIMETABLE PAGE
   ═══════════════════════════════════════════════════════════ */

async function renderGenerate(container) {
    const classes = await API_METHODS.getClasses();
    state.classes = classes;

    container.innerHTML = `
        <div class="page-header">
            <h2>🧠 Generate Timetable</h2>
            <p>AI-powered scheduling using Constraint Satisfaction Problem (CSP) solver</p>
        </div>

        <div class="generate-container">
            <div class="card generate-card">
                <div class="card-body" id="generate-form-area">
                    <div class="form-group">
                        <label class="form-label">Timetable Name</label>
                        <input class="form-input" id="gen-name" value="6th Semester Timetable — ${new Date().toLocaleDateString()}" placeholder="Enter timetable name">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Select Classes (leave empty for all)</label>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            ${classes.map(c => `
                                <label class="form-check">
                                    <input type="checkbox" value="${c.id}" class="gen-class-check" checked>
                                    <span>${c.name} — ${c.branch} (Sem ${c.semester})</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">AI Optimization Iterations</label>
                            <select class="form-select" id="gen-iterations">
                                <option value="1000">1000 (Fast)</option>
                                <option value="2000" selected>2000 (Balanced)</option>
                                <option value="5000">5000 (High Quality)</option>
                                <option value="10000">10000 (Maximum)</option>
                            </select>
                        </div>
                    </div>

                    <div class="card" style="background: rgba(99,102,241,0.06); border-color: rgba(99,102,241,0.15); margin: 16px 0;">
                        <div class="card-body" style="padding:16px;">
                            <h4 style="font-size:0.88rem; margin-bottom:8px;">🔬 AI Algorithm Details</h4>
                            <ul style="font-size:0.82rem; color: var(--text-secondary); list-style: none; padding:0;">
                                <li style="margin-bottom:4px;">✅ <strong>Hard Constraints:</strong> No teacher/room/class overlaps</li>
                                <li style="margin-bottom:4px;">⚡ <strong>Soft Constraints:</strong> Balanced load, minimal gaps, lab preferences</li>
                                <li style="margin-bottom:4px;">🧬 <strong>Method:</strong> Greedy Construction + Hill Climbing Optimization</li>
                                <li>📊 <strong>Output:</strong> Fitness score (0-100%) with conflict analysis</li>
                            </ul>
                        </div>
                    </div>

                    <button class="btn btn-primary btn-lg w-full" onclick="startGeneration()" id="generate-btn">
                        🚀 Generate Optimized Timetable
                    </button>
                </div>

                <div class="generate-progress" id="generate-progress">
                    <div class="ai-loader">
                        <div class="ring"></div>
                        <div class="ring"></div>
                        <div class="ring"></div>
                        <div class="core"></div>
                    </div>
                    <h3>AI Engine Processing...</h3>
                    <p id="progress-text">Analyzing constraints and generating optimal schedule</p>
                </div>
            </div>

            <div id="generate-result" class="mt-3"></div>
        </div>
    `;
}

async function startGeneration() {
    const name = document.getElementById('gen-name').value || 'Generated Timetable';
    const checkboxes = document.querySelectorAll('.gen-class-check:checked');
    const classIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    const iterations = parseInt(document.getElementById('gen-iterations').value);

    // Show progress
    document.getElementById('generate-form-area').style.display = 'none';
    document.getElementById('generate-progress').classList.add('active');

    const progressTexts = [
        'Initializing 3D scheduling matrix...',
        'Loading constraint framework...',
        'Running greedy construction algorithm...',
        'Evaluating hard constraints (C1, C2, C3)...',
        'Optimizing soft constraints via hill climbing...',
        'Calculating fitness score...',
        'Finalizing optimized schedule...',
    ];

    let textIdx = 0;
    const progressInterval = setInterval(() => {
        textIdx = (textIdx + 1) % progressTexts.length;
        const el = document.getElementById('progress-text');
        if (el) el.textContent = progressTexts[textIdx];
    }, 1500);

    try {
        const result = await API_METHODS.generateTimetable({
            name: name,
            class_ids: classIds.length > 0 ? classIds : null,
            max_iterations: iterations,
        });

        clearInterval(progressInterval);
        document.getElementById('generate-progress').classList.remove('active');
        document.getElementById('generate-form-area').style.display = 'block';

        state.currentTimetable = result;

        // Show result
        document.getElementById('generate-result').innerHTML = `
            <div class="card" style="border-color: var(--accent-emerald); border-width: 1px;">
                <div class="card-body">
                    <h3 style="color: var(--accent-emerald); margin-bottom: 16px;">✅ Timetable Generated Successfully!</h3>

                    <div class="score-display">
                        <div class="score-item primary">
                            <div class="score-value">${result.fitness_score.toFixed(1)}%</div>
                            <div class="score-label">Fitness Score</div>
                        </div>
                        <div class="score-item ${result.hard_violations === 0 ? 'success' : 'warning'}">
                            <div class="score-value">${result.hard_violations}</div>
                            <div class="score-label">Hard Violations</div>
                        </div>
                        <div class="score-item info">
                            <div class="score-value">${result.soft_score.toFixed(1)}</div>
                            <div class="score-label">Soft Score</div>
                        </div>
                        <div class="score-item warning">
                            <div class="score-value">${result.generation_time.toFixed(2)}s</div>
                            <div class="score-label">Generation Time</div>
                        </div>
                    </div>

                    <p class="text-sm text-muted mb-2">Total entries: ${result.total_entries} | Conflicts: ${result.conflicts ? result.conflicts.length : 0}</p>

                    <div class="flex gap-2 flex-wrap">
                        <button class="btn btn-primary" onclick="viewTimetableById(${result.id})">📅 View Timetable</button>
                        <button class="btn btn-secondary" onclick="navigateTo('conflicts')">🔍 Analyze Conflicts</button>
                        <button class="btn btn-secondary" onclick="navigateTo('export')">📥 Export</button>
                    </div>
                </div>
            </div>
        `;

        showToast(`Timetable generated with ${result.fitness_score.toFixed(1)}% fitness!`, 'success');
    } catch (err) {
        clearInterval(progressInterval);
        document.getElementById('generate-progress').classList.remove('active');
        document.getElementById('generate-form-area').style.display = 'block';
        document.getElementById('generate-result').innerHTML = `
            <div class="card" style="border-color: var(--accent-red);">
                <div class="card-body">
                    <h3 style="color: var(--accent-red);">❌ Generation Failed</h3>
                    <p class="text-muted mt-1">${escapeHtml(err.message)}</p>
                    <p class="text-sm text-muted mt-1">Make sure you have faculty-subject and class-subject assignments configured.</p>
                </div>
            </div>
        `;
        showToast('Generation failed: ' + err.message, 'error');
    }
}


/* ═══════════════════════════════════════════════════════════
   VIEW TIMETABLE PAGE
   ═══════════════════════════════════════════════════════════ */

async function renderTimetable(container) {
    const timetables = await API_METHODS.getTimetables();
    state.timetables = timetables;

    if (!state.currentTimetable && timetables.length > 0) {
        state.currentTimetable = await API_METHODS.getTimetable(timetables[0].id);
    }

    container.innerHTML = `
        <div class="page-header page-header-flex">
            <div>
                <h2>📅 View Timetable</h2>
                <p>Interactive schedule grid with conflict highlighting</p>
            </div>
            <div class="flex gap-2">
                <button class="btn btn-secondary" onclick="window.print()">🖨️ Print</button>
            </div>
        </div>

        ${timetables.length === 0 ? `
            <div class="card">
                <div class="card-body empty-state">
                    <p style="font-size:1.1rem;">No timetables generated yet</p>
                    <p class="text-muted">Generate your first timetable to see it here</p>
                    <button class="btn btn-primary mt-2" onclick="navigateTo('generate')">🧠 Generate Now</button>
                </div>
            </div>
        ` : `
            <div class="timetable-controls">
                <div class="form-group" style="margin-bottom:0; min-width:250px;">
                    <select class="form-select" id="tt-selector" onchange="onTimetableSelect(this.value)">
                        ${timetables.map(tt => `
                            <option value="${tt.id}" ${state.currentTimetable?.id === tt.id ? 'selected' : ''}>
                                ${escapeHtml(tt.name)} (${tt.fitness_score.toFixed(1)}%)
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div class="form-group" style="margin-bottom:0; min-width:180px;">
                    <select class="form-select" id="tt-class-filter" onchange="onClassFilter(this.value)">
                        <option value="all">All Classes</option>
                        ${getUniqueClasses().map(c => `
                            <option value="${c.id}">${escapeHtml(c.name)}</option>
                        `).join('')}
                    </select>
                </div>
                <button class="btn btn-danger btn-sm" onclick="deleteTimetableFromView()">🗑️ Delete</button>
            </div>

            <div id="timetable-grid-area"></div>
        `}
    `;

    if (state.currentTimetable) {
        renderTimetableGrid('all');
    }
}

function getUniqueClasses() {
    if (!state.currentTimetable?.entries) return [];
    const seen = new Map();
    state.currentTimetable.entries.forEach(e => {
        if (!seen.has(e.class_id)) {
            seen.set(e.class_id, { id: e.class_id, name: e.class_name });
        }
    });
    return Array.from(seen.values());
}

async function onTimetableSelect(id) {
    state.currentTimetable = await API_METHODS.getTimetable(parseInt(id));
    // Re-render class filter options
    const filter = document.getElementById('tt-class-filter');
    if (filter) {
        const classes = getUniqueClasses();
        filter.innerHTML = `<option value="all">All Classes</option>` +
            classes.map(c => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('');
    }
    renderTimetableGrid('all');
}

function onClassFilter(val) {
    renderTimetableGrid(val);
}

function renderTimetableGrid(classFilter) {
    const area = document.getElementById('timetable-grid-area');
    if (!area || !state.currentTimetable) return;

    let entries = state.currentTimetable.entries || [];
    if (classFilter !== 'all') {
        entries = entries.filter(e => e.class_id === parseInt(classFilter));
    }

    // Group entries by class for separate grids
    const classesSeen = new Map();
    entries.forEach(e => {
        if (!classesSeen.has(e.class_id)) {
            classesSeen.set(e.class_id, { name: e.class_name, entries: [] });
        }
        classesSeen.get(e.class_id).entries.push(e);
    });

    let html = '';

    // Score bar
    html += `
        <div class="score-display mb-2">
            <div class="score-item primary">
                <div class="score-value">${state.currentTimetable.fitness_score.toFixed(1)}%</div>
                <div class="score-label">Fitness</div>
            </div>
            <div class="score-item ${state.currentTimetable.hard_violations === 0 ? 'success' : 'warning'}">
                <div class="score-value">${state.currentTimetable.hard_violations}</div>
                <div class="score-label">Violations</div>
            </div>
            <div class="score-item info">
                <div class="score-value">${state.currentTimetable.generation_time.toFixed(2)}s</div>
                <div class="score-label">Gen. Time</div>
            </div>
        </div>
    `;

    classesSeen.forEach((data, classId) => {
        html += `<div class="card mb-2">
            <div class="card-header">
                <h3>📋 ${escapeHtml(data.name)}</h3>
                <span class="badge badge-theory">${data.entries.length} entries</span>
            </div>
            <div class="card-body" style="padding:12px;">
                ${buildGridHTML(data.entries)}
            </div>
        </div>`;
    });

    if (classesSeen.size === 0) {
        html = '<div class="card"><div class="card-body empty-state"><p>No entries for this filter</p></div></div>';
    }

    area.innerHTML = html;
}

function buildGridHTML(entries) {
    // Build a 2D map: [slot][day] -> entry
    const grid = {};
    entries.forEach(e => {
        const key = `${e.time_slot}-${e.day}`;
        if (!grid[key]) grid[key] = [];
        grid[key].push(e);
    });

    let html = `<div class="timetable-grid-wrapper"><table class="timetable-grid">`;

    // Header row
    html += `<thead><tr><th class="time-header">Time / Day</th>`;
    DAYS.forEach(d => { html += `<th class="day-header">${d}</th>`; });
    html += `</tr></thead><tbody>`;

    // Rows
    for (let slot = 0; slot < TIME_SLOTS.length; slot++) {
        // Add lunch break after slot 2 (12:00-01:00)
        if (slot === 3) {
            html += `<tr class="break-row"><td class="time-cell" style="color:var(--accent-amber);">01:00 - 02:00</td>`;
            for (let d = 0; d < DAYS.length; d++) {
                html += `<td class="break-cell">🍽️ Lunch Break</td>`;
            }
            html += `</tr>`;
        }

        html += `<tr><td class="time-cell">${TIME_SLOTS[slot]}</td>`;
        for (let day = 0; day < DAYS.length; day++) {
            const key = `${slot}-${day}`;
            const cellEntries = grid[key] || [];

            if (cellEntries.length === 0) {
                html += `<td></td>`;
            } else if (cellEntries.length === 1) {
                const e = cellEntries[0];
                const bgColor = e.subject_color || '#667eea';
                html += `<td>
                    <div class="tt-cell" style="background:${hexToRgba(bgColor, 0.2)}; border-left-color:${bgColor};">
                        <span class="tt-subject"style="color:${bgColor};">${escapeHtml(e.subject_name)}</span>
                        <span class="tt-faculty" style="color:var(--text-primary);">${escapeHtml(e.faculty_code || e.faculty_name)}</span>
                        <span class="tt-room" style="color:var(--text-secondary);">📍 ${escapeHtml(e.room_name)}</span>
                    </div>
                </td>`;
            } else {
                // Conflict! Multiple entries in same slot
                html += `<td>`;
                cellEntries.forEach(e => {
                    const bgColor = e.subject_color || '#667eea';
                    html += `<div class="tt-cell conflict" style="background:${hexToRgba(bgColor, 0.15)}; border-left-color:${bgColor}; margin-bottom:4px;">
                        <span class="tt-subject" style="color:${bgColor};">${escapeHtml(e.subject_name)}</span>
                        <span class="tt-faculty" style="color:var(--text-primary);">${escapeHtml(e.faculty_code || e.faculty_name)} ⚠️</span>
                        <span class="tt-room" style="color:var(--text-secondary);">📍 ${escapeHtml(e.room_name)}</span>
                    </div>`;
                });
                html += `</td>`;
            }
        }
        html += `</tr>`;
    }

    html += `</tbody></table></div>`;
    return html;
}

async function deleteTimetableFromView() {
    if (!state.currentTimetable) return;
    if (!confirm(`Delete "${state.currentTimetable.name}"?`)) return;
    try {
        await API_METHODS.deleteTimetable(state.currentTimetable.id);
        state.currentTimetable = null;
        showToast('Timetable deleted', 'success');
        navigateTo('timetable');
    } catch (err) { showToast(err.message, 'error'); }
}


/* ═══════════════════════════════════════════════════════════
   CONFLICT ANALYSIS PAGE
   ═══════════════════════════════════════════════════════════ */

async function renderConflicts(container) {
    const timetables = await API_METHODS.getTimetables();
    state.timetables = timetables;

    container.innerHTML = `
        <div class="page-header">
            <h2>⚠️ Conflict Analysis</h2>
            <p>Detect and analyze scheduling conflicts in generated timetables</p>
        </div>

        ${timetables.length === 0 ? `
            <div class="card"><div class="card-body empty-state">
                <p>No timetables to analyze</p>
                <button class="btn btn-primary mt-2" onclick="navigateTo('generate')">Generate First</button>
            </div></div>
        ` : `
            <div class="form-group" style="max-width:400px; margin-bottom:20px;">
                <label class="form-label">Select Timetable</label>
                <select class="form-select" id="conflict-tt-select" onchange="analyzeConflicts(this.value)">
                    <option value="">Choose a timetable...</option>
                    ${timetables.map(tt => `
                        <option value="${tt.id}" ${state.currentTimetable?.id === tt.id ? 'selected' : ''}>
                            ${escapeHtml(tt.name)} (${tt.fitness_score.toFixed(1)}%)
                        </option>
                    `).join('')}
                </select>
            </div>
            <div id="conflict-results"></div>
        `}
    `;

    if (state.currentTimetable) {
        analyzeConflicts(state.currentTimetable.id);
    }
}

async function analyzeConflicts(id) {
    if (!id) return;
    const results = document.getElementById('conflict-results');
    results.innerHTML = '<div class="page-loader" style="min-height:200px;"><div class="loader-spinner"></div></div>';

    try {
        const data = await API_METHODS.getConflicts(parseInt(id));
        const conflicts = data.conflicts || [];

        if (conflicts.length === 0) {
            results.innerHTML = `
                <div class="card">
                    <div class="card-body" style="text-align:center; padding:48px;">
                        <div style="font-size:3rem; margin-bottom:16px;">✅</div>
                        <h3 style="color: var(--accent-emerald); margin-bottom:8px;">No Conflicts Detected!</h3>
                        <p class="text-muted">This timetable has zero hard constraint violations. All faculty, room, and class assignments are conflict-free.</p>
                    </div>
                </div>
            `;
        } else {
            results.innerHTML = `
                <div class="card mb-2" style="border-left: 3px solid var(--accent-red);">
                    <div class="card-body">
                        <h3 style="color: var(--accent-red);">${conflicts.length} Conflict${conflicts.length > 1 ? 's' : ''} Found</h3>
                        <p class="text-muted text-sm">These need to be resolved for an optimal timetable.</p>
                    </div>
                </div>
                ${conflicts.map((c, i) => `
                    <div class="conflict-item severity-${c.severity}">
                        <div class="conflict-icon">⚠️</div>
                        <div class="conflict-details">
                            <h4>${escapeHtml(c.type)}</h4>
                            <p>${escapeHtml(c.description)}</p>
                        </div>
                    </div>
                `).join('')}
            `;
        }
    } catch (err) {
        results.innerHTML = `<div class="card"><div class="card-body text-muted">Error: ${err.message}</div></div>`;
    }
}


/* ═══════════════════════════════════════════════════════════
   EXPORT PAGE
   ═══════════════════════════════════════════════════════════ */

async function renderExport(container) {
    const timetables = await API_METHODS.getTimetables();

    container.innerHTML = `
        <div class="page-header">
            <h2>📥 Export & Download</h2>
            <p>Download generated timetables in various formats</p>
        </div>

        ${timetables.length === 0 ? `
            <div class="card"><div class="card-body empty-state">
                <p>No timetables to export</p>
                <button class="btn btn-primary mt-2" onclick="navigateTo('generate')">Generate First</button>
            </div></div>
        ` : `
            <div class="form-group" style="max-width:400px; margin-bottom:24px;">
                <label class="form-label">Select Timetable</label>
                <select class="form-select" id="export-tt-select">
                    ${timetables.map(tt => `
                        <option value="${tt.id}" ${state.currentTimetable?.id === tt.id ? 'selected' : ''}>
                            ${escapeHtml(tt.name)} (${tt.fitness_score.toFixed(1)}%)
                        </option>
                    `).join('')}
                </select>
            </div>

            <div class="export-grid">
                <div class="export-option card" onclick="exportCSV()">
                    <div class="export-icon">📄</div>
                    <h4>CSV Download</h4>
                    <p>Spreadsheet-compatible format for Excel/Sheets</p>
                </div>
                <div class="export-option card" onclick="exportPrint()">
                    <div class="export-icon">🖨️</div>
                    <h4>Print Timetable</h4>
                    <p>Print-friendly layout optimized for paper</p>
                </div>
                <div class="export-option card" onclick="exportJSON()">
                    <div class="export-icon">🔧</div>
                    <h4>JSON Data</h4>
                    <p>Raw JSON data for integration with other systems</p>
                </div>
            </div>
        `}
    `;
}

function exportCSV() {
    const ttId = document.getElementById('export-tt-select')?.value;
    if (!ttId) return showToast('Select a timetable first', 'warning');
    window.open(`${API}/timetables/${ttId}/export/csv`, '_blank');
    showToast('CSV download started', 'success');
}

function exportPrint() {
    const ttId = document.getElementById('export-tt-select')?.value;
    if (!ttId) return showToast('Select a timetable first', 'warning');
    viewTimetableById(parseInt(ttId)).then(() => {
        setTimeout(() => window.print(), 500);
    });
}

async function exportJSON() {
    const ttId = document.getElementById('export-tt-select')?.value;
    if (!ttId) return showToast('Select a timetable first', 'warning');
    try {
        const data = await API_METHODS.getTimetable(parseInt(ttId));
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `timetable_${ttId}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('JSON download started', 'success');
    } catch (err) {
        showToast('Export failed: ' + err.message, 'error');
    }
}


/* ═══════════════════════════════════════════════════════════
   UTILITY FUNCTIONS
   ═══════════════════════════════════════════════════════════ */

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function hexToRgba(hex, alpha) {
    if (!hex) return `rgba(102, 126, 234, ${alpha})`;
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}


/* ═══════════════════════════════════════════════════════════
   INITIALIZATION
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    navigateTo('dashboard');
});
