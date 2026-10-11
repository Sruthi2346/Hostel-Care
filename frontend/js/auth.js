const API = 'http://127.0.0.1:8000/api';
const msg = document.getElementById('message');
function showMessage(text, type='error') { msg.textContent=text; msg.className='message '+type; }
function setTab(tab) {
  document.querySelectorAll('[data-auth-tab]').forEach(b=>b.classList.toggle('active',b.dataset.authTab===tab));
  document.getElementById('login-form').classList.toggle('hidden',tab!=='login');
  document.getElementById('register-form').classList.toggle('hidden',tab!=='register');
  msg.className='message hidden';
}
document.querySelectorAll('[data-auth-tab]').forEach(b=>b.addEventListener('click',()=>setTab(b.dataset.authTab)));
async function api(path, options={}) {
  const response=await fetch(API+path,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});
  const data=await response.json().catch(()=>({detail:'Server returned a non-JSON response'}));
  if(!response.ok) throw new Error(data.detail||data.message||'Request failed');
  return data;
}
document.getElementById('login-form').addEventListener('submit',async e=>{
  e.preventDefault(); const f=new FormData(e.currentTarget); const button=e.currentTarget.querySelector('button[type=submit]'); button.disabled=true; button.textContent='Signing in…';
  try { const result=await api('/auth/login',{method:'POST',body:JSON.stringify({email:f.get('email'),password:f.get('password')})}); localStorage.setItem('hostelcare_token',result.access_token); localStorage.setItem('hostelcare_user',JSON.stringify(result.user)); location.href='portal.html'; }
  catch(err){showMessage(err.message+' — check that FastAPI is running at http://127.0.0.1:8000');}
  finally{button.disabled=false;button.textContent='Login';}
});
document.getElementById('register-form').addEventListener('submit',async e=>{
  e.preventDefault(); const f=new FormData(e.currentTarget); const data=Object.fromEntries(f.entries()); data.admission_year=Number(data.admission_year); data.study_year=Number(data.study_year); if(!data.phone)data.phone=null;if(!data.guardian_name)data.guardian_name=null;if(!data.guardian_phone)data.guardian_phone=null;
  const button=e.currentTarget.querySelector('button[type=submit]'); button.disabled=true;button.textContent='Creating account…';
  try { await api('/auth/register',{method:'POST',body:JSON.stringify(data)}); showMessage('Registration successful. Login using your email and password.','ok'); setTab('login'); document.querySelector('#login-form [name=email]').value=data.email; }
  catch(err){showMessage(err.message+' — check the backend terminal if this looks like a connection error.');}
  finally{button.disabled=false;button.textContent='Create student account';}
});
