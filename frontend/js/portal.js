const API = 'https://hostel-care-api-7mvk.onrender.com/api';
const token=localStorage.getItem('hostelcare_token');
let meUser=JSON.parse(localStorage.getItem('hostelcare_user')||'null');
let activePage='dashboard'; let cache={};
const $=s=>document.querySelector(s);
if(!token||!meUser) location.href='index.html';
const iconMap={dashboard:'▦',admission:'＋',users:'♙',rooms:'⌂',allocate:'▤',maintenance:'⚒',requests:'▣',attendance:'◷',rest:'♥',outpass:'⇄',visitors:'♧',notices:'▤',reports:'▥',audit:'◉',profile:'◎'};
const titles={dashboard:'Dashboard',admission:'Student Admission',users:'Staff & Accounts',rooms:'Hostel Rooms',allocate:'Room Allocation',maintenance:'Maintenance Requests',requests:'My Requests',attendance:'Attendance',rest:'Sick / Rest Reports',outpass:'Outpass',visitors:'Visitor Register',notices:'Notices & Announcements',reports:'Reports & Analytics',audit:'Activity Log',profile:'My Profile'};
const menus={student:[['OVERVIEW',['dashboard','Dashboard']],['MY HOSTEL',['maintenance','Submit Request'],['attendance','My Attendance'],['rest','Sick / Rest Report'],['outpass','Leave / Outpass'],['notices','Notices'],['profile','My Profile']]],staff:[['WORKSPACE',['dashboard','Dashboard'],['maintenance','Assigned Maintenance'],['attendance','Attendance'],['rest','Sick / Rest Reports'],['outpass','Outpass Approvals'],['visitors','Visitor Register'],['notices','Notices']]],admin:[['ADMINISTRATION',['dashboard','Dashboard'],['admission','Student Admission'],['users','Staff & Accounts'],['rooms','Hostel Rooms'],['allocate','Room Allocation']],['HOSTEL OPERATIONS',['attendance','Attendance'],['rest','Sick / Rest Reports'],['maintenance','Maintenance Requests'],['outpass','Outpass'],['visitors','Visitor Register'],['notices','Notices & Announcements']],['REPORTS',['reports','Reports & Analytics'],['audit','Activity Log']]]};
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function dateText(v){if(!v)return '—';let d=new Date(v);return Number.isNaN(d.getTime())?esc(v):d.toLocaleString();}
function dateInput(v=new Date()){const d=new Date(v);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function badge(status){let cls=['Resolved','Present','Returned','Approved'].includes(status)?'green':['Absent','Rejected'].includes(status)?'red':['In Progress','Resting','Pending','Submitted'].includes(status)?'amber':'blue';return `<span class="badge ${cls}">${esc(status||'—')}</span>`;}
function toast(text,error=false){const t=$('#toast');t.textContent=text;t.className='toast'+(error?' error':'');setTimeout(()=>t.classList.add('hidden'),3800);}
async function api(path,opts={}){const r=await fetch(API+path,{...opts,headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json',...(opts.headers||{})}});let data;if(r.status===204)data={};else data=await r.json().catch(()=>({detail:'Invalid response from server'}));if(!r.ok)throw new Error(data.detail||data.message||`Request failed (${r.status})`);return data;}
function go(page){activePage=page;document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active',n.dataset.page===page));$('#page-title').textContent=titles[page]||page;renderPage(page).catch(e=>{ $('#page-content').innerHTML=`<div class="panel"><h2>Could not load this page</h2><p class="muted">${esc(e.message)}</p><button class="btn secondary" onclick="go('${page}')">Retry</button></div>`;});}
function renderNav(){const nav=$('#sidebar-nav');nav.innerHTML=(menus[meUser.role]||menus.student).map(group=>`<div class="nav-label">${group[0]}</div>`+group.slice(1).map(([id,label])=>`<button class="nav-item ${id===activePage?'active':''}" data-page="${id}"><span class="nav-icon">${iconMap[id]||'•'}</span>${label}</button>`).join('')).join('');nav.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.page)));}
$('#side-name').textContent=meUser.name;$('#side-role').textContent=meUser.role;$('#top-name').textContent=meUser.name;$('#avatar').textContent=(meUser.name||'HC').split(' ').map(s=>s[0]).slice(0,2).join('').toUpperCase();
$('#logout-btn').addEventListener('click',()=>{localStorage.removeItem('hostelcare_token');localStorage.removeItem('hostelcare_user');location.href='index.html';});
function stat(label,value,ico){return `<div class="stat-card"><span class="stat-icon">${ico}</span><div class="stat-label">${label}</div><div class="stat-value">${value??0}</div></div>`;}
function panel(title,body,subtitle=''){return `<section class="panel"><div class="panel-header"><div><h2>${title}</h2>${subtitle?`<p class="muted tiny">${subtitle}</p>`:''}</div></div>${body}</section>`;}
function table(headers,rows,empty='No records found yet.'){return `<div class="table-wrap"><table><thead><tr>${headers.map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${rows||`<tr><td colspan="${headers.length}" class="empty">${empty}</td></tr>`}</tbody></table></div>`;}
function field(label,name,type='text',required=true,placeholder='',value=''){return `<label>${label}<input name="${name}" type="${type}" ${required?'required':''} placeholder="${placeholder}" value="${esc(value)}"></label>`;}
function selectField(label,name,options,required=true){return `<label>${label}<select name="${name}" ${required?'required':''}>${options.map(o=>`<option value="${esc(o[0])}">${esc(o[1])}</option>`).join('')}</select></label>`;}
function form(id,content,button='Save'){return `<form id="${id}" class="panel form-layout">${content}<div class="wide form-actions"><button class="btn primary" type="submit">${button}</button></div></form>`;}
async function renderPage(page){const root=$('#page-content');root.innerHTML='<div class="loading">Loading…</div>';if(page==='dashboard')return dashboard(root);if(page==='admission')return admission(root);if(page==='users')return usersPage(root);if(page==='rooms')return roomsPage(root);if(page==='allocate')return allocatePage(root);if(page==='maintenance'||page==='requests')return maintenancePage(root);if(page==='attendance')return attendancePage(root);if(page==='rest')return restPage(root);if(page==='outpass')return outpassPage(root);if(page==='visitors')return visitorsPage(root);if(page==='notices')return noticesPage(root);if(page==='reports')return reportsPage(root);if(page==='audit')return auditPage(root);if(page==='profile')return profilePage(root);root.innerHTML='<div class="panel">Page not found.</div>';}
async function dashboard(root){const d=await api('/dashboard');let heading=meUser.role==='student'?`Welcome back, ${esc(meUser.name)}!`:'Welcome, '+esc(meUser.name)+'!';let cards=meUser.role==='admin'?[stat('Students',d.students,'♙'),stat('Staff',d.staff,'♧'),stat('Open maintenance',d.requests_open,'⚒'),stat('Currently resting',d.resting_now,'♥')]:meUser.role==='staff'?[stat('Assigned jobs',d.assigned_total,'⚒'),stat('Open jobs',d.open,'◷'),stat('Resolved',d.resolved,'✓')]:[stat('My requests',d.requests_total,'▣'),stat('Open requests',d.requests_open,'◷'),stat('Resolved',d.requests_resolved,'✓'),stat('Active rest report',d.active_rest_reports,'♥')];
let quick=meUser.role==='student'?[['maintenance','⚒','Submit a request','Report room or facility issues'],['requests','▣','Track my requests','View status and resolution'],['attendance','◷','My attendance','View morning/evening records'],['rest','♥','Sick / rest report','Inform hostel staff']]:meUser.role==='staff'?[['maintenance','⚒','Assigned maintenance','Update progress'],['attendance','◷','Mark attendance','Room-wise morning/evening'],['rest','♥','Rest reports','Check student welfare'],['visitors','♧','Visitor register','Record entry and exit']]:[['admission','＋','Admit student','Create student account'],['rooms','⌂','Manage rooms','Room capacity and occupancy'],['attendance','◷','Attendance','Mark by room and session'],['reports','▥','Reports','Occupancy and maintenance summary']];
root.innerHTML=`<div class="welcome"><div><p class="eyebrow">YOUR HOSTEL, IN ONE PLACE</p><h2>${heading}</h2><p>${meUser.role==='student'?'Manage your requests, hostel attendance and welfare reports.':'Keep student welfare and hostel operations organized from one dashboard.'}</p></div><div class="welcome-art">🏢</div></div><div class="stats-grid">${cards.join('')}</div><div class="section-heading"><div><h2>Quick actions</h2><p>Jump to the tasks you use most.</p></div></div><div class="quick-grid">${quick.map(([id,ic,t,sub])=>`<button class="quick-card" data-quick="${id}"><div class="qicon">${ic}</div><b>${t}</b><small>${sub}</small></button>`).join('')}</div>`;root.querySelectorAll('[data-quick]').forEach(b=>b.onclick=()=>go(b.dataset.quick));}
async function admission(root){root.innerHTML=`<div class="section-heading"><div><h2>New student admission</h2><p>Create the student account and profile. Room assignment is done separately.</p></div></div>${form('admission-form',field('Full name','name')+field('Student number','student_number')+field('Email','email','email')+field('Temporary password (min 8 chars)','password','password')+field('Phone','phone','tel',false)+field('Department','department')+field('Admission year','admission_year','number',true,'e.g. 2026',new Date().getFullYear())+field('Study year','study_year','number',true,'1','1')+field('Guardian name','guardian_name','text',false)+field('Guardian phone','guardian_phone','tel',false),'Create student')}`;$('#admission-form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));['admission_year','study_year'].forEach(k=>f[k]=Number(f[k]));try{await api('/admin/students',{method:'POST',body:JSON.stringify(f)});toast('Student admission created');e.currentTarget.reset();}catch(err){toast(err.message,true);}};}
async function usersPage(root){const [staff,students]=await Promise.all([api('/users?role=staff'),api('/students')]);root.innerHTML=`${form('staff-form',field('Staff full name','name')+field('Email','email','email')+field('Temporary password','password','password')+field('Phone','phone','tel',false)+field('Department / duty','department','text',false)+selectField('Account role','role',[['staff','Staff'],['admin','Admin']]),'Create account')}<div class="section-heading"><div><h2>Staff accounts</h2><p>Only admin can create staff and admin accounts.</p></div></div>${panel('Staff directory',table(['Name','Email','Department','Status'],staff.map(s=>`<tr><td>${esc(s.name)}</td><td>${esc(s.email)}</td><td>${esc(s.department||'—')}</td><td>${badge(s.is_active?'Active':'Inactive')}</td></tr>`).join('')))}${panel('Student directory',table(['Student ID','Name','Study year','Room','Email'],students.map(s=>`<tr><td>${esc(s.student_number)}</td><td>${esc(s.name)}</td><td>${esc(s.study_year||'—')}</td><td>${esc(s.room?.room_number||'Not allocated')}</td><td>${esc(s.email)}</td></tr>`).join('')) )}`;$('#staff-form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));try{await api('/admin/users',{method:'POST',body:JSON.stringify(f)});toast('Account created');usersPage(root);}catch(err){toast(err.message,true);}};}
async function roomsPage(root){const rooms=await api('/rooms');root.innerHTML=`${form('room-form',field('Hostel name','hostel_name','text',true,'Main Hostel')+field('Block','block','text',true,'A')+field('Room number','room_number')+field('Floor','floor','number',true,'1','1')+field('Capacity (beds)','capacity','number',true,'4','4'),'Add room')}<div class="section-heading"><div><h2>Rooms & occupancy</h2><p>Capacity is checked before a student is allocated.</p></div></div>${panel('Room directory',table(['Hostel','Block','Room','Floor','Capacity','Occupied','Available'],rooms.map(r=>`<tr><td>${esc(r.hostel_name)}</td><td>${esc(r.block)}</td><td>${esc(r.room_number)}</td><td>${r.floor}</td><td>${r.capacity}</td><td>${r.occupied}</td><td>${r.available}</td></tr>`).join('')) )}`;$('#room-form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));f.floor=Number(f.floor);f.capacity=Number(f.capacity);try{await api('/rooms',{method:'POST',body:JSON.stringify(f)});toast('Room created');roomsPage(root);}catch(err){toast(err.message,true);}};}
async function allocatePage(root){const [students,rooms,allocs]=await Promise.all([api('/students'),api('/rooms'),api('/allocations')]);const roomOptions=rooms.map(r=>[r.id,`${r.block}-${r.room_number} · ${r.available} beds free`]);const studentOptions=students.map(s=>[s.id,`${s.student_number} — ${s.name} (Year ${s.study_year||1})`]);root.innerHTML=`${form('allocate-form',selectField('Student','student_user_id',studentOptions)+selectField('Room','room_id',roomOptions)+field('Academic year','academic_year','text',true,'2026-2027','2026-2027')+field('Bed number','bed_number','text',false,'e.g. B1')+field('Study year','study_year','number',true,'1','1'),'Allocate / transfer room')}<p class="small-note">Reallocating a student closes their previous allocation and preserves the history.</p>${panel('Room allocation history',table(['Student','Student ID','Study year','Room','Academic year','Bed','Current'],allocs.map(a=>`<tr><td>${esc(a.student_name)}</td><td>${esc(a.student_number)}</td><td>${esc(a.study_year)}</td><td>${esc(a.block)}-${esc(a.room_number)}</td><td>${esc(a.academic_year)}</td><td>${esc(a.bed_number||'—')}</td><td>${badge(a.is_current?'Current':'Previous')}</td></tr>`).join('')) )}`;$('#allocate-form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));f.student_user_id=Number(f.student_user_id);f.room_id=Number(f.room_id);f.study_year=Number(f.study_year);try{await api('/rooms/allocate',{method:'POST',body:JSON.stringify(f)});toast('Room allocated');allocatePage(root);}catch(err){toast(err.message,true);}};}
async function maintenancePage(root){const reqs=await api('/maintenance');const staff=meUser.role==='admin'?await api('/users?role=staff'):[];let rows=reqs.map(r=>`<tr><td>#${r.id}<br><small>${dateText(r.created_at)}</small></td><td><b>${esc(r.title)}</b><br><small>${esc(r.category)} · ${esc(r.priority)}</small><br>${esc(r.description)}</td><td>${esc(r.student_name)}</td><td>${esc(r.assigned_staff_name||'Unassigned')}</td><td>${badge(r.status)}</td><td>${meUser.role==='admin'?`<div class="inline-form"><select data-assign="${r.id}"><option value="">Unassigned</option>${staff.map(s=>`<option value="${s.id}" ${s.id===r.assigned_staff_id?'selected':''}>${esc(s.name)}</option>`).join('')}</select><button class="btn secondary" data-save-assign="${r.id}">Assign</button></div>`:''}${meUser.role!=='student'?`<div class="inline-form" style="margin-top:7px"><select data-status="${r.id}">${['Submitted','Assigned','In Progress','Resolved'].map(s=>`<option ${r.status===s?'selected':''}>${s}</option>`).join('')}</select><input data-note="${r.id}" placeholder="Progress / resolution note" value="${esc(r.resolution_note||'')}"><button class="btn primary" data-save-status="${r.id}">Update</button></div>`:`<small>${esc(r.resolution_note||'No staff note yet')}</small><br><button class="btn secondary" data-history="${r.id}">View history</button>`}</td></tr>`).join('');let studentForm=meUser.role==='student'?form('maintenance-form',selectField('Category','category',[['Plumbing','Plumbing'],['Electrical','Electrical'],['Cleaning','Cleaning'],['Furniture','Furniture'],['Water','Water supply'],['Internet','Internet'],['Other','Other']])+field('Issue title','title')+selectField('Priority','priority',[['Normal','Normal'],['High','High'],['Urgent','Urgent']])+`<label class="wide">Description<textarea name="description" required></textarea></label>`,'Submit maintenance request'):'';root.innerHTML=`${studentForm}<div class="section-heading"><div><h2>${meUser.role==='student'?'My maintenance requests':meUser.role==='staff'?'Requests assigned to me':'All maintenance requests'}</h2><p>Requests progress from Submitted → Assigned → In Progress → Resolved.</p></div></div>${panel('Request list',table(['Request','Reported by','Assigned staff','Status','Actions'],rows))}`;
if(meUser.role==='student')$('#maintenance-form').onsubmit=async e=>{e.preventDefault();try{await api('/maintenance',{method:'POST',body:JSON.stringify(Object.fromEntries(new FormData(e.currentTarget)))});toast('Maintenance request submitted');maintenancePage(root);}catch(err){toast(err.message,true);}};
root.querySelectorAll('[data-save-assign]').forEach(b=>b.onclick=async()=>{const id=b.dataset.saveAssign;const value=$(`[data-assign="${id}"]`).value;try{await api(`/maintenance/${id}`,{method:'PATCH',body:JSON.stringify({assigned_staff_id:value?Number(value):null,status:value?'Assigned':'Submitted',note:'Assigned by admin'})});toast('Staff assignment saved');maintenancePage(root);}catch(err){toast(err.message,true);}});
root.querySelectorAll('[data-save-status]').forEach(b=>b.onclick=async()=>{const id=b.dataset.saveStatus;try{await api(`/maintenance/${id}`,{method:'PATCH',body:JSON.stringify({status:$(`[data-status="${id}"]`).value,resolution_note:$(`[data-note="${id}"]`).value})});toast('Request updated');maintenancePage(root);}catch(err){toast(err.message,true);}});
root.querySelectorAll('[data-history]').forEach(b=>b.onclick=async()=>{try{const h=await api(`/maintenance/${b.dataset.history}/history`);alert(h.map(x=>`${dateText(x.created_at)} — ${x.status} by ${x.changed_by}${x.note?'\n'+x.note:''}`).join('\n\n')||'No history yet');}catch(err){toast(err.message,true);}});}
async function attendancePage(root){const [students,rooms,records]=await Promise.all([api(meUser.role==='student'?'/auth/me':'/students'),api('/rooms'),api('/attendance')]);const d=dateInput();if(meUser.role==='student'){root.innerHTML=`<div class="welcome"><div><h2>My attendance</h2><p>Hostel presence is separate from college class attendance.</p></div><div>◷</div></div>${panel('Recent attendance',table(['Date','Session','Status','Note'],records.map(a=>`<tr><td>${esc(a.date)}</td><td>${esc(a.session)}</td><td>${badge(a.status)}</td><td>${esc(a.note||'—')}</td></tr>`).join('')) )}`;return;}
const studentList=students;root.innerHTML=`<div class="panel"><h2>Mark room-wise attendance</h2><p class="muted tiny">Choose date, session and room. Mark every listed student, then save. Existing same-date/session records are updated instead of duplicated.</p><form id="attendance-filter" class="filter-row"><label>Date<input type="date" name="date" value="${d}" required></label><label>Session<select name="session"><option>Morning</option><option>Evening</option></select></label><label>Room<select name="room_id"><option value="all">All rooms</option>${rooms.map(r=>`<option value="${r.id}">${esc(r.block)}-${esc(r.room_number)}</option>`).join('')}</select></label><button class="btn secondary" type="submit">Load students</button></form><div id="attendance-list"></div></div>${panel('Saved attendance records',table(['Date','Session','Student ID','Student','Year','Status','Marked by'],records.map(a=>`<tr><td>${esc(a.date)}</td><td>${esc(a.session)}</td><td>${esc(a.student_number)}</td><td>${esc(a.student_name)}</td><td>${esc(a.study_year||'')}</td><td>${badge(a.status)}</td><td>${esc(a.marked_by||'')}</td></tr>`).join('')))}<a class="btn secondary" href="${API}/reports/attendance.csv" id="download-attendance">Download CSV (login required)</a>`;
async function loadList(date,session,room){let list=studentList;if(room!=='all')list=list.filter(s=>s.room&&String(s.room.id)===String(room));const saved=await api(`/attendance?attendance_date=${date}&session=${session}`);const sm=new Map(saved.map(a=>[a.student_user_id,a.status]));
$('#attendance-list').innerHTML = table(
    ['Student', 'Student ID', 'Year', 'Room', 'Attendance status'],
    list.map(s => {
        const current = sm.get(s.id) === 'Absent' ? 'Absent' : 'Present';

        return `
            <tr>
                <td>${esc(s.name)}</td>
                <td>${esc(s.student_number || s.student?.student_number || '')}</td>
                <td>${esc(s.study_year || s.student?.study_year || '')}</td>
                <td>${esc(s.room?.room_number || 'Unallocated')}</td>
                <td>
                    <div class="inline-form">
                        <button
                            type="button"
                            class="btn ${current === 'Present' ? 'success' : 'secondary'}"
                            data-att-present="${s.id}">
                            Present
                        </button>
                        <button
                            type="button"
                            class="btn ${current === 'Absent' ? 'danger' : 'secondary'}"
                            data-att-absent="${s.id}">
                            Absent
                        </button>
                        <input type="hidden" data-att="${s.id}" value="${current}">
                    </div>
                </td>
            </tr>`;
    }).join('')
);

const setAttendanceStatus = (id, status) => {
    const hidden = $(`[data-att="${id}"]`);
    if (!hidden) return;

    hidden.value = status;

    const presentButton = $(`[data-att-present="${id}"]`);
    const absentButton = $(`[data-att-absent="${id}"]`);

    presentButton.className =
        `btn ${status === 'Present' ? 'success' : 'secondary'}`;

    absentButton.className =
        `btn ${status === 'Absent' ? 'danger' : 'secondary'}`;
};

$('#attendance-list')
    .querySelectorAll('[data-att-present]')
    .forEach(button => {
        button.onclick = () =>
            setAttendanceStatus(button.dataset.attPresent, 'Present');
    });

$('#attendance-list')
    .querySelectorAll('[data-att-absent]')
    .forEach(button => {
        button.onclick = () =>
            setAttendanceStatus(button.dataset.attAbsent, 'Absent');
    });

$('#attendance-list').insertAdjacentHTML('beforeend',`<button id="save-attendance" class="btn primary" style="margin-top:12px">Save ${session} attendance</button>`);$('#save-attendance').onclick=async()=>{const recs=[...$('#attendance-list').querySelectorAll('[data-att]')].map(s=>({student_user_id:Number(s.dataset.att),status:s.value}));try{await api('/attendance/mark',{method:'POST',body:JSON.stringify({date,session,records:recs})});toast('Attendance saved');attendancePage(root);}catch(err){toast(err.message,true);}};}
$('#attendance-filter').onsubmit=e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));loadList(f.date,f.session,f.room_id).catch(err=>toast(err.message,true));};await loadList(d,'Morning','all');const link=$('#download-attendance');link.onclick=async e=>{e.preventDefault();try{const res=await fetch(API+'/reports/attendance.csv',{headers:{Authorization:`Bearer ${token}`}});if(!res.ok)throw new Error('Could not export report');const blob=await res.blob();const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='hostel_attendance.csv';a.click();URL.revokeObjectURL(a.href);}catch(err){toast(err.message,true);}};}

async function restPage(root) {
    const reports = await api('/rest-reports');

    const rows = reports.map(r => `
        <tr>
            <td>
                ${esc(r.student_name)}
                <br><small>${esc(r.student_number)}</small>
            </td>
            <td>${esc(r.room?.room_number || 'Not allocated')}</td>
            <td>
                ${esc(r.reason)}
                <br><small>${esc(r.note || '')}</small>
            </td>
            <td>${dateText(r.reported_at)}</td>
            <td>${badge(r.status)}</td>
            <td>
                ${r.status === 'Resting'
                    ? `<button class="btn success" data-return="${r.id}">Mark returned</button>`
                    : '—'}
            </td>
        </tr>
    `).join('');

    const defaultReportingTime = new Date(
        Date.now() - new Date().getTimezoneOffset() * 60000
    ).toISOString().slice(0, 16);

    const create = meUser.role === 'student'
        ? form(
            'rest-form',
            selectField('Reason', 'reason', [
                ['Not feeling well', 'Not feeling well'],
                ['Fever', 'Fever'],
                ['Headache', 'Headache'],
                ['Other', 'Other']
            ]) +
            field(
                'Reporting on',
                'reported_at',
                'datetime-local',
                true,
                '',
                defaultReportingTime
            ) +
            `<label class="wide">
                Optional note
                <textarea name="note" placeholder="Brief note for the warden"></textarea>
            </label>`,
            'Report sick / rest'
        )
        : '';

    root.innerHTML = `
        ${create}
        <div class="section-heading">
            <div>
                <h2>${meUser.role === 'student'
                    ? 'My rest reports'
                    : 'Student sick / rest reports'}</h2>
                <p>Share only the information needed by hostel staff.</p>
            </div>
        </div>
        ${panel(
            'Rest report register',
            table(
                ['Student', 'Room', 'Reason / note', 'Reported at', 'Status', 'Action'],
                rows
            )
        )}
    `;

    if (meUser.role === 'student') {
        $('#rest-form').onsubmit = async e => {
            e.preventDefault();

            const f = Object.fromEntries(new FormData(e.currentTarget));

            if (f.reported_at) {
                f.reported_at = new Date(f.reported_at).toISOString();
            }

            try {
                await api('/rest-reports', {
                    method: 'POST',
                    body: JSON.stringify(f)
                });

                toast('Rest report sent to hostel staff');
                restPage(root);
            } catch (err) {
                toast(err.message, true);
            }
        };
    }

    root.querySelectorAll('[data-return]').forEach(b => {
        b.onclick = async () => {
            try {
                await api(`/rest-reports/${b.dataset.return}/return`, {
                    method: 'PATCH'
                });

                toast('Return status updated');
                restPage(root);
            } catch (err) {
                toast(err.message, true);
            }
        };
    });
}
async function outpassPage(root){const rows=await api('/outpasses');const content=meUser.role==='student'?form('outpass-form',field('Destination','destination')+field('Reason','reason')+field('Departure date/time','leave_at','datetime-local')+field('Expected return','expected_return','datetime-local'),'Request outpass'):'';root.innerHTML=`${content}${panel(meUser.role==='student'?'My outpass requests':'Student outpass requests',table(['Student','Destination','Reason','Departure','Expected return','Status','Action'],rows.map(o=>`<tr><td>${esc(o.student_name)}</td><td>${esc(o.destination)}</td><td>${esc(o.reason)}</td><td>${dateText(o.leave_at)}</td><td>${dateText(o.expected_return)}</td><td>${badge(o.status)}</td><td>${meUser.role!=='student'&&o.status==='Pending'?`<button class="btn success" data-pass="${o.id}" data-val="Approved">Approve</button> <button class="btn danger" data-pass="${o.id}" data-val="Rejected">Reject</button>`:'—'}</td></tr>`).join('')) )}`;if(meUser.role==='student')$('#outpass-form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));f.leave_at=new Date(f.leave_at).toISOString();f.expected_return=new Date(f.expected_return).toISOString();try{await api('/outpasses',{method:'POST',body:JSON.stringify(f)});toast('Outpass request submitted');outpassPage(root);}catch(err){toast(err.message,true);}};root.querySelectorAll('[data-pass]').forEach(b=>b.onclick=async()=>{try{await api(`/outpasses/${b.dataset.pass}`,{method:'PATCH',body:JSON.stringify({status:b.dataset.val})});toast('Outpass updated');outpassPage(root);}catch(err){toast(err.message,true);}});}
async function visitorsPage(root){const rows=await api('/visitors');const students=await api('/students');root.innerHTML=`${form('visitor-form',field('Visitor name','visitor_name')+field('Phone','phone','tel',false)+selectField('Visiting student','student_user_id',[['','Not linked'],...students.map(s=>[s.id,`${s.student_number} — ${s.name}`])],false)+field('Purpose','purpose'),'Record visitor entry')}${panel('Visitor log',table(['Visitor','Phone','Student','Purpose','Entry time','Exit time','Action'],rows.map(v=>`<tr><td>${esc(v.visitor_name)}</td><td>${esc(v.phone||'—')}</td><td>${esc(v.student_name||'—')}</td><td>${esc(v.purpose)}</td><td>${dateText(v.entry_at)}</td><td>${dateText(v.exit_at)}</td><td>${v.exit_at?'Checked out':`<button class="btn secondary" data-checkout="${v.id}">Check out</button>`}</td></tr>`).join('')) )}`;$('#visitor-form').onsubmit=async e=>{e.preventDefault();const f=Object.fromEntries(new FormData(e.currentTarget));if(f.student_user_id)f.student_user_id=Number(f.student_user_id);else f.student_user_id=null;try{await api('/visitors',{method:'POST',body:JSON.stringify(f)});toast('Visitor recorded');visitorsPage(root);}catch(err){toast(err.message,true);}};root.querySelectorAll('[data-checkout]').forEach(b=>b.onclick=async()=>{try{await api(`/visitors/${b.dataset.checkout}/checkout`,{method:'PATCH'});toast('Visitor checked out');visitorsPage(root);}catch(err){toast(err.message,true);}});}
async function noticesPage(root){const rows=await api('/notices');const create=meUser.role==='admin'?form('notice-form',field('Notice title','title')+selectField('Audience','audience',[['all','Everyone'],['student','Students'],['staff','Staff'],['admin','Admins']])+`<label class="wide">Message<textarea name="message" required></textarea></label>`,'Publish notice'):'';root.innerHTML=`${create}<div class="section-heading"><div><h2>Notices & announcements</h2><p>Hostel circulars and important updates.</p></div></div>${rows.map(n=>`<div class="notice"><b>${esc(n.title)}</b><p>${esc(n.message)}</p><small>${esc(n.author)} · ${dateText(n.created_at)} · ${esc(n.audience)}</small></div>`).join('')||'<div class="panel empty">No notices have been published.</div>'}`;if(meUser.role==='admin')$('#notice-form').onsubmit=async e=>{e.preventDefault();try{await api('/notices',{method:'POST',body:JSON.stringify(Object.fromEntries(new FormData(e.currentTarget)))});toast('Notice published');noticesPage(root);}catch(err){toast(err.message,true);}};}
async function reportsPage(root){const d=await api('/reports/summary');root.innerHTML=`<div class="stats-grid">${stat('Students',d.student_count,'♙')}${stat('Rooms',d.room_count,'⌂')}${stat('Allocated students',d.allocated_students,'▤')}${stat('Unallocated students',d.unallocated_students,'!')}${stat('Open maintenance',d.maintenance.open,'⚒')}${stat('Resolved maintenance',d.maintenance.resolved,'✓')}${stat('Attendance records',d.attendance_records,'◷')}${stat('Currently resting',d.resting_now,'♥')}</div>${panel('Room occupancy',table(['Hostel','Block','Room','Capacity','Occupied','Available'],d.room_occupancy.map(r=>`<tr><td>${esc(r.hostel_name)}</td><td>${esc(r.block)}</td><td>${esc(r.room_number)}</td><td>${r.capacity}</td><td>${r.occupied}</td><td>${r.available}</td></tr>`).join('')))}<button class="btn primary" id="export-csv">Export attendance CSV</button><p class="small-note">This CSV contains hostel attendance records. Treat exports as confidential student information.</p>`;$('#export-csv').onclick=async()=>{try{const res=await fetch(API+'/reports/attendance.csv',{headers:{Authorization:`Bearer ${token}`}});if(!res.ok)throw new Error('Export failed');const blob=await res.blob();const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='hostel_attendance.csv';a.click();URL.revokeObjectURL(a.href);}catch(err){toast(err.message,true);}};}
async function auditPage(root){const logs=await api('/audit-logs');root.innerHTML=panel('Recent administrative activity',table(['Time','User','Action','Details'],logs.map(a=>`<tr><td>${dateText(a.created_at)}</td><td>${esc(a.actor)}</td><td>${esc(a.action)}</td><td>${esc(a.details||'')}</td></tr>`).join('')));}
async function profilePage(root){const u=await api('/auth/me');const p=u.student||{};root.innerHTML=`<div class="panel"><div class="avatar">${esc((u.name||'HC').slice(0,2).toUpperCase())}</div><h2 style="margin-top:15px">${esc(u.name)}</h2><p class="muted">${esc(u.email)} · ${esc(u.role)}</p>${panel('Account information',table(['Field','Value'],[['Name',u.name],['Email',u.email],['Phone',u.phone||'—'],['Department',p.department||u.department||'—'],['Student number',p.student_number||'—'],['Admission year',p.admission_year||'—'],['Study year',p.study_year||'—'],['Guardian',p.guardian_name||'—'],['Guardian phone',p.guardian_phone||'—']].map(([a,b])=>`<tr><td>${esc(a)}</td><td>${esc(b)}</td></tr>`).join('')))}</div>`;}
renderNav();go('dashboard');
