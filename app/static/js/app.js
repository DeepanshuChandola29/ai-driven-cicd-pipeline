const form=document.getElementById('pipelineForm');
const toast=document.getElementById('toast');
function notify(msg){toast.textContent=msg;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2800)}
document.querySelectorAll('input[type=range]').forEach(el=>el.addEventListener('input',()=>{document.getElementById(el.dataset.output).textContent=el.value+(el.dataset.suffix||'')}));
function statusClass(s){return s.toLowerCase().replaceAll(' ','-')}
function addRun(run){
 const body=document.getElementById('historyBody');
 const empty=body.querySelector('.empty-row');if(empty)empty.remove();
 const tr=document.createElement('tr');
 const values=[run.version,run.created_at,run.risk_score+'%',run.status,run.reasons[0]||'—'];
 values.forEach((v,i)=>{const td=document.createElement('td');if(i===0){const b=document.createElement('b');b.textContent=v;td.appendChild(b)}else if(i===3){const s=document.createElement('span');s.className='result '+statusClass(v);s.textContent=v;td.appendChild(s)}else td.textContent=v;tr.appendChild(td)});
 body.prepend(tr);
}
form.addEventListener('submit',async e=>{
 e.preventDefault();const btn=document.getElementById('runBtn');btn.disabled=true;btn.innerHTML='<span>◌</span> Analyzing pipeline...';
 const payload=Object.fromEntries(new FormData(form).entries());
 payload.simulate_health_failure=document.getElementById('healthFail').checked?'yes':'no';
 for(const k of ['changed_files','test_failures','previous_failures','build_duration','cpu_usage','coverage'])payload[k]=Number(payload[k]);
 try{
  const response=await fetch('/api/pipeline/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!response.ok)throw new Error('Pipeline request failed');
  const data=await response.json(),r=data.run;addRun(r);
  document.getElementById('riskNumber').textContent=r.risk_score+'%';
  document.getElementById('riskLevel').textContent=r.risk_level+' RISK';
  document.getElementById('riskSummary').textContent=r.status==='DEPLOYED'?'Risk gate passed. Release deployed successfully.':r.status==='ROLLED BACK'?'Health check failed. Stable release restored.':'Release blocked by risk or test gate.';
  const ring=document.getElementById('riskRing');const color=r.risk_score>=70?'#ff7d91':r.risk_score>=35?'#f4c66b':'#63e6d2';ring.style.background=`conic-gradient(${color} ${r.risk_score*3.6}deg,#29364e 0deg)`;
  const ul=document.getElementById('reasons');ul.replaceChildren();r.reasons.forEach(reason=>{const li=document.createElement('li');li.textContent=reason;ul.appendChild(li)});
  document.getElementById('activeVersion').textContent=data.active_version||'No active release';
  await refreshStats();notify('Pipeline completed: '+r.status);
 }catch(err){notify(err.message)}finally{btn.disabled=false;btn.innerHTML='<span>✦</span> Analyze & run pipeline <b>→</b>'}
});
async function refreshStats(){const d=await (await fetch('/api/overview')).json();document.getElementById('total').textContent=d.total;document.getElementById('deployed').textContent=d.success;document.getElementById('blocked').textContent=d.blocked;const risks=d.runs.map(r=>r.risk_score);document.getElementById('avgRisk').textContent=risks.length?Math.round(risks.reduce((a,b)=>a+b,0)/risks.length):0}
document.getElementById('resetBtn').addEventListener('click',async()=>{if(!confirm('Clear all demo runs and release state?'))return;await fetch('/api/reset',{method:'POST'});location.reload()});
