import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';

const api = axios.create({ baseURL: 'http://127.0.0.1:8000' });

type Project = { id:number; name:string; query:string; source:string; year_range?:string };

function App() {
  const [tab, setTab] = useState('dashboard');
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<number|undefined>();
  const [runId, setRunId] = useState<number|undefined>();
  const [runStatus, setRunStatus] = useState<any>();
  const [papers, setPapers] = useState<any[]>([]);
  const [evidence, setEvidence] = useState<any[]>([]);
  const [drafts, setDrafts] = useState<any[]>([]);

  const loadProjects = async () => setProjects((await api.get('/api/projects')).data);
  useEffect(()=>{loadProjects()},[]);
  useEffect(()=>{
    if (!runId) return;
    const timer = setInterval(async ()=> setRunStatus((await api.get(`/api/runs/${runId}/status`)).data), 2500);
    return ()=>clearInterval(timer);
  }, [runId]);

  const createProject = async (e:any)=>{
    e.preventDefault();
    const f = new FormData(e.target);
    await api.post('/api/projects', {
      name:f.get('name'), query:f.get('query'), source:f.get('source'), year_range:f.get('year'), export_format:'ris', allowlist:['*.webofscience.com','*.scopus.com']
    });
    e.target.reset(); loadProjects();
  }

  const startRun = async ()=>{
    if(!activeProject) return;
    const r = await api.post(`/api/runs/${activeProject}/start`);
    setRunId(r.data.run_id); setTab('console');
  }

  const loadData = async ()=>{
    if(!activeProject) return;
    setPapers((await api.get(`/api/papers/${activeProject}`)).data);
    setEvidence((await api.get(`/api/evidence/${activeProject}`)).data);
    setDrafts((await api.get(`/api/drafts/${activeProject}`)).data);
  }

  return <div style={{fontFamily:'sans-serif', padding:16}}>
    <h2>LitReviewAgent MVP</h2>
    <div>{['dashboard','console','papers','evidence','drafts','settings'].map(t=><button key={t} onClick={()=>{setTab(t); loadData();}}>{t}</button>)}</div>
    {tab==='dashboard' && <div>
      <h3>Project Dashboard</h3>
      <form onSubmit={createProject}><input name='name' placeholder='name'/><input name='query' placeholder='query'/><select name='source'><option value='wos'>WoS</option><option value='scopus'>Scopus</option></select><input name='year' placeholder='2020-2024'/><button>create</button></form>
      <ul>{projects.map(p=><li key={p.id}><label><input type='radio' name='p' onChange={()=>setActiveProject(p.id)}/>{p.name} ({p.source})</label></li>)}</ul>
      <button onClick={startRun}>Start Run</button>
    </div>}
    {tab==='console' && <div>
      <h3>Run Console</h3>
      <pre>{JSON.stringify(runStatus, null, 2)}</pre>
      {runStatus?.latest_screenshot && <img src={`http://127.0.0.1:8000/api/runs/${runId}/latest_screenshot`} style={{maxWidth:500}}/>}
      {runStatus?.status==='NEED_TAKEOVER' && <button onClick={()=>api.post(`/api/runs/${runId}/approve_takeover`)}>继续(approve takeover)</button>}
    </div>}
    {tab==='papers' && <div><h3>Papers</h3><div>count: {papers.length}</div><pre>{JSON.stringify(papers.slice(0,5), null, 2)}</pre></div>}
    {tab==='evidence' && <div><h3>Evidence</h3><div>count: {evidence.length}</div><pre>{JSON.stringify(evidence.slice(0,5), null, 2)}</pre></div>}
    {tab==='drafts' && <div><h3>Drafts</h3><button onClick={async()=>{if(activeProject){await api.post('/api/drafts/generate',{project_id:activeProject,title:'Weekly Review'}); loadData();}}}>Generate Word Draft</button><pre>{JSON.stringify(drafts,null,2)}</pre></div>}
    {tab==='settings' && <div><h3>Settings</h3><p>Allowlist / download limit / model config are from .env.</p></div>}
  </div>
}

createRoot(document.getElementById('root')!).render(<App/>);
