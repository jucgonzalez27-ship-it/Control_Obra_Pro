import { useState, useCallback, useRef } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

// ─── CONSTANTES ──────────────────────────────────────────────────────────
const SUPERVISORES  = ["Juan G.", "Carlos M.", "Pedro A.", "María S."];
const ESPECIALIDADES= ["Carpintería","Instalaciones Eléctricas","Instalaciones Sanitarias","Terminaciones","Pintura","Revestimientos","Hormigón","Fierro","Moldaje","Andamios"];
const PROBLEMAS = [
  {key:"Falta material",    icon:"📦",color:"#3B82F6",desc:"Stock, bodega, proveedor"},
  {key:"Interferencia",     icon:"⚡",color:"#A855F7",desc:"Otro subcontrato en zona"},
  {key:"Error ejecución",   icon:"🔧",color:"#F59E0B",desc:"Retrabajo necesario"},
  {key:"Falta información", icon:"📋",color:"#06B6D4",desc:"Planos, especificaciones"},
  {key:"Seguridad",         icon:"🚨",color:"#EF4444",desc:"Riesgo en terreno"},
];
const TOWERS = [
  {id:"A",name:"Torre A",stage:"Terminaciones Finas",  sc:"#A855F7",sb:"#1A1033",
   floors:[{l:"P6",u:["51","52"]},{l:"P5",u:["41","42"]},{l:"P4",u:["31","32"]},{l:"P3",u:["21","22"]},{l:"P2",u:["11","12"]},{l:"P1",u:["01","02"]}]},
  {id:"B",name:"Torre B",stage:"Terminaciones Gruesas",sc:"#38BDF8",sb:"#0B1E2D",
   floors:[{l:"P5",u:["53","54","55","56","57","58","59"]},{l:"P4",u:["43","44","45","46","47","48","49"]},{l:"P3",u:["33","34","35","36","37","38","39"]},{l:"P2",u:["23","24","25","26","27","28","29"]},{l:"P1",u:["13","14","15","16","17","18"]},{l:"N-1",u:["03","04","05","06","07"]}]},
  {id:"C",name:"Torre C",stage:"Obra Gruesa",          sc:"#FB923C",sb:"#1C1005",
   floors:[{l:"N4",u:["C4-A","C4-B","C4-C","C4-D"]},{l:"N3",u:["C3-A","C3-B","C3-C","C3-D"]},{l:"N2",u:["C2-A","C2-B","C2-C","C2-D"]},{l:"N1",u:["C1-A","C1-B","C1-C","C1-D"]}]},
];

// ─── DEMO DATA ───────────────────────────────────────────────────────────
const ago  = d => new Date(Date.now()-d*86400000).toISOString();
const fwd  = d => new Date(Date.now()+d*86400000).toISOString().split("T")[0];
const prev = d => new Date(Date.now()-d*86400000).toISOString().split("T")[0];

const DEMO_BLOCKS = {
  "31":[{id:1,problema:"Falta material",   detalle:"Porcelanato 60×60 sin stock en bodega",             supervisor:"Carlos M.",ts:ago(3),fotos:[]}],
  "22":[{id:2,problema:"Error ejecución",  detalle:"Nivelación de piso fuera de tolerancia ±5mm",       supervisor:"Pedro A.", ts:ago(3),fotos:[]}],
  "52":[{id:3,problema:"Interferencia",    detalle:"Instalación eléctrica sin terminar, bloquea pintura",supervisor:"Juan G.",  ts:ago(1),fotos:[]}],
  "45":[{id:4,problema:"Seguridad",        detalle:"Andamio sin revisión técnica — área clausurada",     supervisor:"Juan G.",  ts:ago(0),fotos:[]}],
  "13":[{id:5,problema:"Error ejecución",  detalle:"Tabique mal posicionado — demolición parcial",       supervisor:"Pedro A.", ts:ago(4),fotos:[]}],
};
const DEMO_ACTIVITIES = [
  {id:1, uid:"01",esp:"Terminaciones",           desc:"Instalación piso flotante dormitorios",      resp:"Carlos M.",fecha:prev(3),estado:"completado",    razon:"",fotos:[]},
  {id:2, uid:"02",esp:"Pintura",                 desc:"Segunda mano pintura dormitorio principal",  resp:"Pedro A.", fecha:prev(2),estado:"no_completado", razon:"Sin material (pintura base)",fotos:[]},
  {id:3, uid:"11",esp:"Carpintería",             desc:"Instalación puerta principal y closets",     resp:"Juan G.",  fecha:prev(1),estado:"en_ejecucion",  razon:"",fotos:[]},
  {id:4, uid:"12",esp:"Instalaciones Eléctricas",desc:"Enchufes y llaves de luz sector living",    resp:"María S.", fecha:prev(1),estado:"completado",    razon:"",fotos:[]},
  {id:5, uid:"21",esp:"Revestimientos",          desc:"Cerámica baño principal 30×30",              resp:"Carlos M.",fecha:prev(0),estado:"en_ejecucion",  razon:"",fotos:[]},
  {id:6, uid:"22",esp:"Pintura",                 desc:"Primera mano comedor y living",              resp:"Pedro A.", fecha:prev(0),estado:"programado",    razon:"",fotos:[]},
  {id:7, uid:"41",esp:"Carpintería",             desc:"Remate de marcos ventanas exterior",         resp:"Juan G.",  fecha:fwd(1), estado:"programado",    razon:"",fotos:[]},
  {id:8, uid:"C1-A",esp:"Fierro",               desc:"Habilitación armaduras losa N1",              resp:"Juan G.",  fecha:prev(4),estado:"completado",    razon:"",fotos:[]},
  {id:9, uid:"C2-B",esp:"Hormigón",             desc:"Hormigonado muro eje 3-4",                    resp:"Pedro A.", fecha:prev(2),estado:"no_completado", razon:"ITO no aprobó armadura",fotos:[]},
  {id:10,uid:"33", esp:"Revestimientos",         desc:"Cerámica cocina 20×20",                       resp:"Carlos M.",fecha:prev(1),estado:"en_ejecucion",  razon:"",fotos:[]},
  {id:11,uid:"43", esp:"Pintura",                desc:"Preparación de superficies estuco",           resp:"María S.", fecha:fwd(2), estado:"programado",    razon:"",fotos:[]},
];

// ─── UTILS ───────────────────────────────────────────────────────────────
const diasAgo   = ts => Math.floor((Date.now()-new Date(ts).getTime())/86400000);
const today0    = () => { const d=new Date(); d.setHours(0,0,0,0); return d; };
const parseDate = s  => { const d=new Date(s); d.setHours(0,0,0,0); return d; };
const DIAS      = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"];

function actDiasVencida(act){
  if(act.estado==="completado"||act.estado==="no_completado") return 0;
  const diff=today0()-parseDate(act.fecha);
  return diff>0?Math.floor(diff/86400000):0;
}
function getStatus(uid,blocks,activities){
  const b=blocks[uid]||[];
  const acts=activities.filter(a=>a.uid===uid);
  const critBlock=b.some(x=>x.problema==="Seguridad"||diasAgo(x.ts)>=2);
  const anyBlock=b.length>0;
  const vencidas=acts.filter(a=>actDiasVencida(a)>0);
  const critAct=vencidas.some(a=>actDiasVencida(a)>=2);
  if(critBlock||critAct) return "red";
  if(anyBlock||vencidas.length>0) return "yellow";
  return "green";
}
const ST={
  green: {color:"#22C55E",bg:"#052E16",glow:"0 0 12px #22C55E44",label:"Avanzando"},
  yellow:{color:"#F59E0B",bg:"#1C1500",glow:"0 0 12px #F59E0B44",label:"Cuello de botella"},
  red:   {color:"#EF4444",bg:"#1C0404",glow:"0 0 12px #EF444444",label:"Paralizado"},
};
const C={bg:"#070B14",surface:"#0D1321",elevated:"#111B2E",border:"#1E2E47",borderL:"#243652",
         textP:"#E8EFF8",textS:"#8EA3BE",textM:"#4A6280",blue:"#3B82F6",blueDim:"#0F2347"};

function computePPC(activities){
  const t0=today0();
  const due=activities.filter(a=>parseDate(a.fecha)<=t0);
  if(!due.length) return null;
  const done=due.filter(a=>a.estado==="completado").length;
  return {ppc:Math.round((done/due.length)*100),done,total:due.length};
}
function computeStats(blocks,activities){
  let total=0,g=0,y=0,r=0;
  const all=Object.values(blocks).flat();
  const crit=all.filter(b=>b.problema==="Seguridad"||diasAgo(b.ts)>=2);
  const byP={},byS={};
  all.forEach(b=>{byP[b.problema]=(byP[b.problema]||0)+1;byS[b.supervisor]=(byS[b.supervisor]||0)+1;});
  TOWERS.forEach(tw=>tw.floors.forEach(fl=>fl.u.forEach(uid=>{
    total++;const s=getStatus(uid,blocks,activities);
    if(s==="green")g++;else if(s==="yellow")y++;else r++;
  })));
  const avg=all.length>0?(all.reduce((a,b)=>a+diasAgo(b.ts),0)/all.length).toFixed(1):0;
  return {total,g,y,r,all,crit,byP,byS,avg,ppcData:computePPC(activities)};
}

// ─── FOTO UTILS ──────────────────────────────────────────────────────────
function readFileAsBase64(file){
  return new Promise((res,rej)=>{
    const r=new FileReader();
    r.onload=()=>res(r.result);
    r.onerror=rej;
    r.readAsDataURL(file);
  });
}

// ─── FOTO UPLOADER ───────────────────────────────────────────────────────
function FotoUploader({fotos=[],onAdd,compact=false}){
  const ref=useRef();
  const handle=async(e)=>{
    const files=Array.from(e.target.files||[]);
    for(const f of files){
      if(!f.type.startsWith("image/")) continue;
      const b64=await readFileAsBase64(f);
      onAdd(b64);
    }
    e.target.value="";
  };
  return(
    <div>
      <input ref={ref} type="file" accept="image/*" multiple onChange={handle} style={{display:"none"}}/>
      {!compact&&fotos.length>0&&(
        <div style={{display:"flex",flexWrap:"wrap",gap:6,marginBottom:8}}>
          {fotos.map((src,i)=>(
            <div key={i} style={{position:"relative",width:64,height:64,borderRadius:6,overflow:"hidden",border:`1px solid ${C.border}`,flexShrink:0}}>
              <img src={src} alt="" style={{width:"100%",height:"100%",objectFit:"cover"}}/>
            </div>
          ))}
        </div>
      )}
      <button onClick={()=>ref.current?.click()} style={{
        background:C.elevated,border:`1px dashed ${C.borderL}`,color:C.textS,
        borderRadius:7,padding:compact?"5px 10px":"7px 14px",cursor:"pointer",
        fontSize:compact?11:12,display:"flex",alignItems:"center",gap:6,transition:"all .15s",
      }}
      onMouseEnter={e=>e.currentTarget.style.borderColor=C.blue}
      onMouseLeave={e=>e.currentTarget.style.borderColor=C.borderL}>
        <span>📷</span>
        <span>{fotos.length>0?`${fotos.length} foto${fotos.length>1?"s":""} · agregar más`:"Adjuntar foto"}</span>
      </button>
    </div>
  );
}

// ─── FOTO GALLERY ────────────────────────────────────────────────────────
function FotoGallery({fotos=[]}){
  const [big,setBig]=useState(null);
  if(!fotos.length) return null;
  return(
    <>
      <div style={{display:"flex",flexWrap:"wrap",gap:6,marginTop:8}}>
        {fotos.map((src,i)=>(
          <div key={i} onClick={()=>setBig(src)} style={{
            width:68,height:68,borderRadius:7,overflow:"hidden",
            border:`1px solid ${C.border}`,cursor:"pointer",flexShrink:0,
            transition:"transform .12s",
          }}
          onMouseEnter={e=>e.currentTarget.style.transform="scale(1.06)"}
          onMouseLeave={e=>e.currentTarget.style.transform="scale(1)"}>
            <img src={src} alt="" style={{width:"100%",height:"100%",objectFit:"cover"}}/>
          </div>
        ))}
      </div>
      {big&&(
        <div onClick={()=>setBig(null)} style={{
          position:"fixed",inset:0,background:"#000000CC",zIndex:1000,
          display:"flex",alignItems:"center",justifyContent:"center",cursor:"zoom-out",
        }}>
          <img src={big} alt="" style={{maxWidth:"90vw",maxHeight:"90vh",borderRadius:10,boxShadow:"0 0 60px #000"}}/>
        </div>
      )}
    </>
  );
}

// ─── TOOLTIP ─────────────────────────────────────────────────────────────
const CTip=({active,payload})=>{
  if(!active||!payload?.length) return null;
  return <div style={{background:C.elevated,border:`1px solid ${C.border}`,borderRadius:8,padding:"8px 12px"}}>
    <div style={{fontSize:10,color:C.textS,marginBottom:2}}>{payload[0]?.payload?.fullName||payload[0]?.name}</div>
    <div style={{fontSize:18,fontWeight:600,color:C.textP,fontFamily:"'JetBrains Mono',monospace"}}>{payload[0]?.value}</div>
  </div>;
};

// ─── APP ─────────────────────────────────────────────────────────────────
export default function App(){
  const [blocks,setBlocks]         = useState(DEMO_BLOCKS);
  const [activities,setActivities] = useState(DEMO_ACTIVITIES);
  const [view,setView]             = useState("dashboard");
  const [sel,setSel]               = useState(null);

  const addBlock=useCallback((uid,problema,supervisor,nota,fotos=[])=>{
    setBlocks(p=>({...p,[uid]:[...(p[uid]||[]),{id:Date.now(),problema,detalle:nota||"Sin observación",supervisor,ts:new Date().toISOString(),fotos}]}));
  },[]);
  const resolveBlock=useCallback((uid,id)=>{
    setBlocks(p=>{const u=(p[uid]||[]).filter(b=>b.id!==id);const n={...p};if(!u.length)delete n[uid];else n[uid]=u;return n;});
  },[]);
  const addFotoToBlock=useCallback((uid,bid,foto)=>{
    setBlocks(p=>({...p,[uid]:(p[uid]||[]).map(b=>b.id===bid?{...b,fotos:[...(b.fotos||[]),foto]}:b)}));
  },[]);
  const updateActivity=useCallback((id,estado,razon="")=>{
    setActivities(p=>p.map(a=>a.id===id?{...a,estado,razon}:a));
  },[]);
  const addFotoToActivity=useCallback((id,foto)=>{
    setActivities(p=>p.map(a=>a.id===id?{...a,fotos:[...(a.fotos||[]),foto]}:a));
  },[]);
  const addActivity=useCallback((act)=>{
    setActivities(p=>[...p,{...act,id:Date.now(),estado:"programado",razon:"",fotos:[]}]);
  },[]);

  const stats=computeStats(blocks,activities);

  return(
    <div style={{display:"flex",height:"100vh",background:C.bg,color:C.textP,overflow:"hidden"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Plus Jakarta Sans',system-ui,sans-serif}
        ::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-thumb{background:#1E2E47;border-radius:2px}
        .cell{transition:transform .1s,box-shadow .1s;cursor:pointer}.cell:hover{transform:scale(1.12);z-index:20}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}.blink{animation:blink 2s infinite}
        @keyframes fu{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.fu{animation:fu .25s ease}
        @keyframes sr{from{opacity:0;transform:translateX(14px)}to{opacity:1;transform:translateX(0)}}.sr{animation:sr .2s ease}
        .nav:hover{background:#111B2E!important}.kpi{transition:all .18s}.kpi:hover{transform:translateY(-2px);border-color:#243652!important}
        button:focus,textarea:focus,input:focus,select:focus{outline:none}
      `}</style>
      <Sidebar view={view} setView={v=>{setView(v);setSel(null);}}/>
      <div style={{flex:1,overflow:"hidden",display:"flex",flexDirection:"column"}}>
        <Topbar/>
        <div style={{flex:1,overflow:"auto"}}>
          {view==="dashboard" && <Dashboard stats={stats} blocks={blocks} activities={activities}/>}
          {view==="plan"      && <PlanSemanal activities={activities} blocks={blocks} updateActivity={updateActivity} addActivity={addActivity} addFoto={addFotoToActivity}/>}
          {view==="panel"     && <Panel blocks={blocks} activities={activities} sel={sel} setSel={setSel} resolve={resolveBlock} addFoto={addFotoToBlock}/>}
          {view==="registrar" && <Registrar blocks={blocks} addBlock={addBlock} onDone={()=>setView("dashboard")}/>}
        </div>
      </div>
    </div>
  );
}

// ─── TOPBAR ──────────────────────────────────────────────────────────────
function Topbar(){
  return(
    <div style={{height:50,background:C.surface,borderBottom:`1px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 24px",flexShrink:0}}>
      <div style={{fontSize:13,color:C.textM}}>
        <span style={{color:C.textS}}>Proyecto</span>{" · "}
        <span style={{color:C.textP,fontWeight:700}}>Residencial Las Torres</span>
      </div>
      <div style={{display:"flex",alignItems:"center",gap:10}}>
        <div style={{width:6,height:6,borderRadius:"50%",background:"#22C55E",boxShadow:"0 0 8px #22C55E88"}}/>
        <span style={{fontSize:11,color:C.textM,fontFamily:"'JetBrains Mono',monospace"}}>
          {new Date().toLocaleDateString("es-CL",{day:"numeric",month:"short",year:"numeric"})}
        </span>
      </div>
    </div>
  );
}

// ─── SIDEBAR ─────────────────────────────────────────────────────────────
function Sidebar({view,setView}){
  const nav=[
    {id:"dashboard",icon:"▦", label:"Dashboard"},
    {id:"plan",     icon:"📅",label:"Plan Semanal"},
    {id:"panel",    icon:"⊞", label:"Panel Obra"},
    {id:"registrar",icon:"⊕", label:"Registrar"},
  ];
  return(
    <div style={{width:200,background:C.surface,borderRight:`1px solid ${C.border}`,display:"flex",flexDirection:"column",flexShrink:0}}>
      <div style={{padding:"18px 16px 16px",borderBottom:`1px solid ${C.border}`}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:34,height:34,borderRadius:9,background:"linear-gradient(135deg,#1D4ED8,#1E40AF)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:18}}>🏗</div>
          <div>
            <div style={{fontSize:14,fontWeight:800,color:C.textP,lineHeight:1,letterSpacing:"-.3px"}}>ObraTrack</div>
            <div style={{fontSize:9,color:C.textM,marginTop:3,letterSpacing:1}}>CONTROL OPERATIVO</div>
          </div>
        </div>
      </div>
      <div style={{padding:"14px 10px",flex:1}}>
        <div style={{fontSize:9,color:C.textM,letterSpacing:2,padding:"0 8px",marginBottom:8}}>MENÚ</div>
        {nav.map(item=>{
          const on=view===item.id;
          return(
            <div key={item.id} className="nav" onClick={()=>setView(item.id)} style={{
              display:"flex",alignItems:"center",gap:10,padding:"9px 12px",borderRadius:8,marginBottom:2,cursor:"pointer",
              background:on?"linear-gradient(135deg,#0F2347,#162B52)":"transparent",
              border:on?`1px solid #3B82F622`:`1px solid transparent`,transition:"all .15s",
            }}>
              <span style={{fontSize:15,opacity:on?1:.5}}>{item.icon}</span>
              <span style={{fontSize:13,fontWeight:on?700:400,color:on?"#60A5FA":C.textS}}>{item.label}</span>
            </div>
          );
        })}
      </div>
      <div style={{padding:"14px 18px",borderTop:`1px solid ${C.border}`}}>
        <div style={{fontSize:10,color:C.textM}}>v1.1 · © 2026 ObraTrack</div>
      </div>
    </div>
  );
}

// ─── DASHBOARD ───────────────────────────────────────────────────────────
function Dashboard({stats,blocks}){
  const {total,g,y,r,all,crit,byP,byS,avg,ppcData}=stats;
  const probData=PROBLEMAS.map(p=>({name:p.icon+" "+p.key.split(" ")[0],fullName:p.key,value:byP[p.key]||0,color:p.color})).filter(x=>x.value>0).sort((a,b)=>b.value-a.value);
  const supData=Object.entries(byS).sort((a,b)=>b[1]-a[1]).map(([nm,v])=>({name:nm.split(" ")[0],fullName:nm,value:v}));
  const pieData=[{name:"Avanzando",value:g,color:"#22C55E"},{name:"Alerta",value:y,color:"#F59E0B"},{name:"Paralizado",value:r,color:"#EF4444"}].filter(x=>x.value>0);
  const ppcColor=!ppcData?C.textM:ppcData.ppc>=80?"#22C55E":ppcData.ppc>=60?"#F59E0B":"#EF4444";
  return(
    <div className="fu" style={{padding:"24px",maxWidth:1080}}>
      <div style={{marginBottom:22}}>
        <h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Dashboard</h1>
        <p style={{fontSize:13,color:C.textM,marginTop:5}}>Estado al {new Date().toLocaleDateString("es-CL",{weekday:"long",day:"numeric",month:"long",year:"numeric"})}</p>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:12,marginBottom:20}}>
        {[
          {label:"Unidades libres", value:`${g}/${total}`,sub:`${Math.round((g/total)*100)}% avanzando`,color:"#22C55E",icon:"✓"},
          {label:"Bloqueos activos",value:all.length,      sub:`${y} alerta · ${r} paralizados`,         color:"#F59E0B",icon:"⚠"},
          {label:"Críticos",        value:crit.length,     sub:"Seg. o +2 días abierto",                 color:"#EF4444",icon:"!"},
          {label:"Días promedio",   value:`${avg}d`,        sub:"por bloqueo activo",                     color:C.blue,   icon:"⏱"},
          {label:"PPC Semanal",     value:ppcData?`${ppcData.ppc}%`:"—",sub:ppcData?`${ppcData.done}/${ppcData.total} completadas`:"Sin datos",color:ppcColor,icon:"📊"},
        ].map(k=>(
          <div key={k.label} className="kpi" style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"16px 16px 14px"}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:12}}>
              <span style={{fontSize:10,fontWeight:700,color:C.textM,letterSpacing:.5}}>{k.label.toUpperCase()}</span>
              <div style={{width:24,height:24,borderRadius:6,background:`${k.color}15`,border:`1px solid ${k.color}22`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,color:k.color,fontWeight:700}}>{k.icon}</div>
            </div>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:26,fontWeight:500,color:k.color,lineHeight:1,marginBottom:5}}>{k.value}</div>
            <div style={{fontSize:11,color:C.textM}}>{k.sub}</div>
          </div>
        ))}
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 260px",gap:12,marginBottom:20}}>
        <div style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"18px 20px"}}>
          <div style={{fontSize:13,fontWeight:700,color:C.textP,marginBottom:3}}>Bloqueos por tipo</div>
          <div style={{fontSize:11,color:C.textM,marginBottom:16}}>{all.length} bloqueos activos</div>
          {probData.length>0?(
            <ResponsiveContainer width="100%" height={165}>
              <BarChart data={probData} layout="vertical" margin={{top:0,right:8,bottom:0,left:0}}>
                <XAxis type="number" hide/>
                <YAxis type="category" dataKey="name" tick={{fill:C.textS,fontSize:11}} width={90} axisLine={false} tickLine={false}/>
                <Tooltip content={<CTip/>}/>
                <Bar dataKey="value" radius={[0,5,5,0]} background={{fill:C.elevated,radius:4}}>
                  {probData.map((e,i)=><Cell key={i} fill={e.color}/>)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ):<div style={{height:165,display:"flex",alignItems:"center",justifyContent:"center",color:C.textM,fontSize:13}}>Sin bloqueos</div>}
        </div>
        <div style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"18px 20px"}}>
          <div style={{fontSize:13,fontWeight:700,color:C.textP,marginBottom:3}}>Carga por supervisor</div>
          <div style={{fontSize:11,color:C.textM,marginBottom:16}}>Bloqueos asignados</div>
          {supData.length>0?(
            <ResponsiveContainer width="100%" height={165}>
              <BarChart data={supData} margin={{top:0,right:10,bottom:0,left:-20}}>
                <XAxis dataKey="name" tick={{fill:C.textS,fontSize:11}} axisLine={false} tickLine={false}/>
                <YAxis tick={{fill:C.textS,fontSize:10}} axisLine={false} tickLine={false}/>
                <Tooltip content={<CTip/>}/>
                <Bar dataKey="value" fill={C.blue} radius={[5,5,0,0]}/>
              </BarChart>
            </ResponsiveContainer>
          ):<div style={{height:165,display:"flex",alignItems:"center",justifyContent:"center",color:C.textM,fontSize:13}}>Sin datos</div>}
        </div>
        <div style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"18px 20px"}}>
          <div style={{fontSize:13,fontWeight:700,color:C.textP,marginBottom:3}}>Estado del proyecto</div>
          <div style={{fontSize:11,color:C.textM,marginBottom:6}}>{total} unidades</div>
          <ResponsiveContainer width="100%" height={120}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={32} outerRadius={52} paddingAngle={3} dataKey="value">
                {pieData.map((e,i)=><Cell key={i} fill={e.color}/>)}
              </Pie>
              <Tooltip content={<CTip/>}/>
            </PieChart>
          </ResponsiveContainer>
          <div style={{display:"flex",flexDirection:"column",gap:7,marginTop:4}}>
            {pieData.map(p=>(
              <div key={p.name} style={{display:"flex",alignItems:"center",justifyContent:"space-between"}}>
                <div style={{display:"flex",alignItems:"center",gap:7}}>
                  <div style={{width:8,height:8,borderRadius:2,background:p.color}}/>
                  <span style={{fontSize:11,color:C.textS}}>{p.name}</span>
                </div>
                <div style={{display:"flex",gap:6}}>
                  <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:12,color:p.color,fontWeight:500}}>{p.value}</span>
                  <span style={{fontSize:10,color:C.textM}}>{Math.round((p.value/total)*100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      {crit.length>0&&(
        <div style={{background:C.surface,border:"1px solid #3A1010",borderRadius:12,padding:"18px 20px"}}>
          <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:16}}>
            <div style={{width:8,height:8,borderRadius:"50%",background:"#EF4444",boxShadow:"0 0 10px #EF4444"}}/>
            <span style={{fontSize:13,fontWeight:700,color:"#EF4444"}}>Bloqueos críticos activos</span>
            <span style={{marginLeft:"auto",fontSize:11,color:"#EF4444",background:"#1C0404",padding:"2px 10px",borderRadius:20,fontWeight:600}}>{crit.length}</span>
          </div>
          <div style={{display:"grid",gridTemplateColumns:"70px 1fr 130px 110px 80px 60px",gap:10,padding:"0 10px",marginBottom:8}}>
            {["Unidad","Detalle","Supervisor","Tipo","Abierto","Fotos"].map(h=>(
              <div key={h} style={{fontSize:10,color:C.textM,fontWeight:600,letterSpacing:.5}}>{h.toUpperCase()}</div>
            ))}
          </div>
          {crit.map(b=>{
            let uid="?";
            Object.entries(blocks).forEach(([u,bs])=>{if(bs.some(x=>x.id===b.id))uid=u;});
            const d=diasAgo(b.ts),pCfg=PROBLEMAS.find(p=>p.key===b.problema)||{color:C.textS,icon:"•"};
            return(
              <div key={b.id} style={{display:"grid",gridTemplateColumns:"70px 1fr 130px 110px 80px 60px",gap:10,padding:"10px",background:C.elevated,borderRadius:8,marginBottom:6,alignItems:"center"}}>
                <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:13,fontWeight:600,color:"#60A5FA"}}>{uid}</div>
                <div style={{fontSize:12,color:C.textS,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{b.detalle}</div>
                <div style={{fontSize:12,color:C.textS}}>👤 {b.supervisor}</div>
                <div style={{display:"flex",alignItems:"center",gap:5}}>
                  <span>{pCfg.icon}</span>
                  <span style={{fontSize:11,color:pCfg.color,fontWeight:600}}>{b.problema.split(" ")[0]}</span>
                </div>
                <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:11,color:d>=2?"#EF4444":"#F59E0B",background:d>=2?"#1C0404":"#1C1500",padding:"3px 8px",borderRadius:5,textAlign:"center"}}>
                  {d===0?"Hoy":`${d}d`}
                </div>
                <div style={{fontSize:11,color:b.fotos?.length?C.blue:C.textM}}>
                  {b.fotos?.length?`📷 ${b.fotos.length}`:"—"}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── PLAN SEMANAL ─────────────────────────────────────────────────────────
const EST_CFG={
  programado:   {color:"#64748B",bg:"#111B2E",label:"Programado"},
  en_ejecucion: {color:"#3B82F6",bg:"#0F2347",label:"En ejecución"},
  completado:   {color:"#22C55E",bg:"#052E16",label:"Completado"},
  no_completado:{color:"#EF4444",bg:"#1C0404",label:"No completado"},
};

function PlanSemanal({activities,blocks,updateActivity,addActivity,addFoto}){
  const [adding,setAdding]=useState(false);
  const [form,setForm]=useState({uid:"",esp:ESPECIALIDADES[0],desc:"",resp:SUPERVISORES[0],fecha:new Date().toISOString().split("T")[0]});
  const [expandRazon,setExpandRazon]=useState(null);
  const [razonText,setRazonText]=useState("");
  const ppcData=computePPC(activities);
  const ppcColor=!ppcData?C.textM:ppcData.ppc>=80?"#22C55E":ppcData.ppc>=60?"#F59E0B":"#EF4444";

  const getWeekDays=()=>{
    const d=new Date(); d.setHours(0,0,0,0);
    const day=d.getDay(); const diff=day===0?-6:1-day;
    return Array.from({length:7},(_,i)=>{const dt=new Date(d);dt.setDate(d.getDate()+diff+i);return dt;});
  };
  const weekDays=getWeekDays();
  const byDate={};
  activities.forEach(a=>{if(!byDate[a.fecha])byDate[a.fecha]=[];byDate[a.fecha].push(a);});

  const submit=()=>{
    if(!form.uid||!form.desc) return;
    addActivity(form);
    setForm({uid:"",esp:ESPECIALIDADES[0],desc:"",resp:SUPERVISORES[0],fecha:new Date().toISOString().split("T")[0]});
    setAdding(false);
  };

  return(
    <div className="fu" style={{padding:"24px",maxWidth:960}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:20,flexWrap:"wrap",gap:12}}>
        <div>
          <h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Plan Semanal</h1>
          <p style={{fontSize:13,color:C.textM,marginTop:5}}>
            Semana {weekDays[0].toLocaleDateString("es-CL",{day:"numeric",month:"short"})} — {weekDays[6].toLocaleDateString("es-CL",{day:"numeric",month:"short",year:"numeric"})}
          </p>
        </div>
        <div style={{display:"flex",gap:10,alignItems:"center"}}>
          {ppcData&&(
            <div style={{background:C.surface,border:`1px solid ${ppcColor}33`,borderRadius:10,padding:"10px 18px",textAlign:"center"}}>
              <div style={{fontSize:9,color:C.textM,marginBottom:3,fontWeight:700,letterSpacing:.5}}>PPC SEMANAL</div>
              <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:26,fontWeight:600,color:ppcColor,lineHeight:1}}>{ppcData.ppc}%</div>
              <div style={{fontSize:10,color:C.textM,marginTop:3}}>{ppcData.done}/{ppcData.total} completadas</div>
            </div>
          )}
          <button onClick={()=>setAdding(!adding)} style={{background:"linear-gradient(135deg,#1D4ED8,#2563EB)",border:"none",color:"#FFF",borderRadius:9,padding:"10px 18px",cursor:"pointer",fontSize:13,fontWeight:700,boxShadow:"0 4px 16px #2563EB33"}}>
            + Nueva actividad
          </button>
        </div>
      </div>

      {adding&&(
        <div style={{background:C.surface,border:`1px solid ${C.blue}44`,borderRadius:12,padding:"18px",marginBottom:20}}>
          <div style={{fontSize:13,fontWeight:700,color:C.textP,marginBottom:14}}>Nueva actividad</div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:12,marginBottom:12}}>
            <div>
              <div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>UNIDAD</div>
              <input value={form.uid} onChange={e=>setForm(p=>({...p,uid:e.target.value}))} placeholder="Ej: 31, C2-A" style={{width:"100%",background:C.elevated,border:`1px solid ${C.border}`,borderRadius:7,color:C.textP,padding:"8px 10px",fontSize:13,fontFamily:"inherit"}}/>
            </div>
            <div>
              <div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>ESPECIALIDAD</div>
              <select value={form.esp} onChange={e=>setForm(p=>({...p,esp:e.target.value}))} style={{width:"100%",background:C.elevated,border:`1px solid ${C.border}`,borderRadius:7,color:C.textP,padding:"8px 10px",fontSize:13}}>
                {ESPECIALIDADES.map(e=><option key={e}>{e}</option>)}
              </select>
            </div>
            <div>
              <div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>FECHA</div>
              <input type="date" value={form.fecha} onChange={e=>setForm(p=>({...p,fecha:e.target.value}))} style={{width:"100%",background:C.elevated,border:`1px solid ${C.border}`,borderRadius:7,color:C.textP,padding:"8px 10px",fontSize:13}}/>
            </div>
          </div>
          <div style={{display:"grid",gridTemplateColumns:"2fr 1fr",gap:12,marginBottom:14}}>
            <div>
              <div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>DESCRIPCIÓN</div>
              <input value={form.desc} onChange={e=>setForm(p=>({...p,desc:e.target.value}))} placeholder="Describe la actividad..." style={{width:"100%",background:C.elevated,border:`1px solid ${C.border}`,borderRadius:7,color:C.textP,padding:"8px 10px",fontSize:13,fontFamily:"inherit"}}/>
            </div>
            <div>
              <div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>RESPONSABLE</div>
              <select value={form.resp} onChange={e=>setForm(p=>({...p,resp:e.target.value}))} style={{width:"100%",background:C.elevated,border:`1px solid ${C.border}`,borderRadius:7,color:C.textP,padding:"8px 10px",fontSize:13}}>
                {SUPERVISORES.map(s=><option key={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div style={{display:"flex",gap:8}}>
            <button onClick={submit} style={{background:"linear-gradient(135deg,#1D4ED8,#2563EB)",border:"none",color:"#FFF",borderRadius:7,padding:"9px 20px",cursor:"pointer",fontSize:13,fontWeight:700}}>Agregar</button>
            <button onClick={()=>setAdding(false)} style={{background:C.elevated,border:`1px solid ${C.border}`,color:C.textM,borderRadius:7,padding:"9px 16px",cursor:"pointer",fontSize:13}}>Cancelar</button>
          </div>
        </div>
      )}

      {weekDays.map((day,di)=>{
        const ds=day.toISOString().split("T")[0];
        const dayActs=byDate[ds]||[];
        const isToday=ds===new Date().toISOString().split("T")[0];
        if(!dayActs.length&&!isToday) return null;
        return(
          <div key={ds} style={{marginBottom:16}}>
            <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:8}}>
              <div style={{padding:"4px 12px",borderRadius:6,fontSize:12,fontWeight:700,background:isToday?"#1D3461":C.elevated,color:isToday?"#60A5FA":C.textM,border:isToday?`1px solid #3B82F644`:`1px solid ${C.border}`}}>
                {DIAS[di]} {day.toLocaleDateString("es-CL",{day:"numeric",month:"short"})}
                {isToday&&<span style={{marginLeft:8,fontSize:9,background:"#3B82F6",color:"#FFF",padding:"1px 6px",borderRadius:3}}>HOY</span>}
              </div>
              <div style={{flex:1,height:1,background:C.border}}/>
              <span style={{fontSize:11,color:C.textM}}>{dayActs.length} actividad{dayActs.length!==1?"es":""}</span>
            </div>
            {dayActs.map(act=>{
              const cfg=EST_CFG[act.estado]||EST_CFG.programado;
              const dv=actDiasVencida(act);
              return(
                <div key={act.id} style={{background:C.surface,border:`1px solid ${dv>0&&act.estado!=="completado"&&act.estado!=="no_completado"?`${dv>=2?"#EF4444":"#F59E0B"}44`:C.border}`,borderRadius:10,padding:"14px 16px",marginBottom:8}}>
                  <div style={{display:"flex",alignItems:"flex-start",gap:12}}>
                    <div style={{width:10,height:10,borderRadius:"50%",background:cfg.color,marginTop:4,flexShrink:0,boxShadow:act.estado==="completado"?"0 0 8px #22C55E55":act.estado==="en_ejecucion"?"0 0 8px #3B82F655":"none"}}/>
                    <div style={{flex:1,minWidth:0}}>
                      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:5,flexWrap:"wrap"}}>
                        <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:12,fontWeight:600,color:"#60A5FA",background:C.blueDim,padding:"2px 7px",borderRadius:4}}>{act.uid}</span>
                        <span style={{fontSize:11,color:C.textM,background:C.elevated,padding:"2px 8px",borderRadius:4}}>{act.esp}</span>
                        <span style={{fontSize:11,color:C.textM}}>👤 {act.resp}</span>
                        {dv>0&&act.estado!=="completado"&&act.estado!=="no_completado"&&(
                          <span style={{fontSize:10,color:dv>=2?"#EF4444":"#F59E0B",background:dv>=2?"#1C0404":"#1C1500",padding:"2px 7px",borderRadius:4,fontWeight:600,marginLeft:"auto"}}>⚠ {dv}d vencida</span>
                        )}
                      </div>
                      <div style={{fontSize:13,color:C.textS,marginBottom:8}}>{act.desc}</div>
                      {act.razon&&<div style={{fontSize:11,color:"#EF4444",background:"#1C0404",padding:"4px 10px",borderRadius:5,marginBottom:8,display:"inline-block"}}>Razón: {act.razon}</div>}

                      {/* FOTOS */}
                      <FotoGallery fotos={act.fotos||[]}/>
                      <div style={{marginTop:8}}>
                        <FotoUploader fotos={act.fotos||[]} compact onAdd={foto=>addFoto(act.id,foto)}/>
                      </div>

                      {expandRazon===act.id&&(
                        <div style={{marginTop:10,display:"flex",gap:8}}>
                          <input value={razonText} onChange={e=>setRazonText(e.target.value)} placeholder="¿Por qué no se completó?" style={{flex:1,background:C.elevated,border:`1px solid ${C.border}`,borderRadius:6,color:C.textP,padding:"7px 10px",fontSize:12,fontFamily:"inherit"}}/>
                          <button onClick={()=>{updateActivity(act.id,"no_completado",razonText);setExpandRazon(null);setRazonText("");}} style={{background:"#1C0404",border:"1px solid #EF4444",color:"#EF4444",borderRadius:6,padding:"7px 12px",cursor:"pointer",fontSize:12,fontWeight:600}}>Confirmar</button>
                          <button onClick={()=>setExpandRazon(null)} style={{background:C.elevated,border:`1px solid ${C.border}`,color:C.textM,borderRadius:6,padding:"7px 10px",cursor:"pointer",fontSize:12}}>×</button>
                        </div>
                      )}
                    </div>
                    <div style={{display:"flex",gap:6,flexShrink:0}}>
                      {act.estado==="programado"&&<button onClick={()=>updateActivity(act.id,"en_ejecucion")} style={{background:"#0F2347",border:"1px solid #3B82F644",color:"#60A5FA",borderRadius:6,padding:"6px 10px",cursor:"pointer",fontSize:11,fontWeight:600}}>▷ Iniciar</button>}
                      {act.estado==="en_ejecucion"&&<>
                        <button onClick={()=>updateActivity(act.id,"completado")} style={{background:"#052E16",border:"1px solid #22C55E44",color:"#22C55E",borderRadius:6,padding:"6px 10px",cursor:"pointer",fontSize:11,fontWeight:600}}>✓</button>
                        <button onClick={()=>setExpandRazon(act.id)} style={{background:"#1C0404",border:"1px solid #EF444444",color:"#EF4444",borderRadius:6,padding:"6px 10px",cursor:"pointer",fontSize:11,fontWeight:600}}>✗</button>
                      </>}
                      {act.estado==="completado"&&<span style={{fontSize:11,color:"#22C55E",background:"#052E16",padding:"5px 10px",borderRadius:6,fontWeight:600}}>✓ Listo</span>}
                      {act.estado==="no_completado"&&<span style={{fontSize:11,color:"#EF4444",background:"#1C0404",padding:"5px 10px",borderRadius:6,fontWeight:600,whiteSpace:"nowrap"}}>✗ No cumplido</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// ─── PANEL ───────────────────────────────────────────────────────────────
function Panel({blocks,activities,sel,setSel,resolve,addFoto}){
  return(
    <div className="fu" style={{display:"flex",height:"100%",overflow:"hidden"}}>
      <div style={{flex:1,overflow:"auto",padding:"24px"}}>
        <div style={{marginBottom:20}}>
          <h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Panel de Obra</h1>
          <p style={{fontSize:13,color:C.textM,marginTop:5}}>Toca una unidad para ver detalle, gestionar bloqueos y evidencia fotográfica</p>
        </div>
        <div style={{display:"flex",gap:14,alignItems:"flex-start",flexWrap:"wrap"}}>
          {TOWERS.map(tw=><TowerCard key={tw.id} tower={tw} blocks={blocks} activities={activities} sel={sel} onSel={setSel}/>)}
        </div>
      </div>
      {sel&&(
        <div className="sr" style={{width:340,background:C.surface,borderLeft:`1px solid ${C.border}`,overflow:"auto",flexShrink:0}}>
          <DetailPanel uid={sel} blocks={blocks[sel]||[]} activities={activities.filter(a=>a.uid===sel)} status={getStatus(sel,blocks,activities)} onClose={()=>setSel(null)} onResolve={id=>resolve(sel,id)} addFoto={(bid,foto)=>addFoto(sel,bid,foto)}/>
        </div>
      )}
    </div>
  );
}

// ─── TOWER CARD ──────────────────────────────────────────────────────────
function TowerCard({tower,blocks,activities,sel,onSel}){
  let g=0,y=0,r=0;
  tower.floors.forEach(f=>f.u.forEach(u=>{const s=getStatus(u,blocks,activities);if(s==="green")g++;else if(s==="yellow")y++;else r++;}));
  return(
    <div style={{background:C.surface,borderRadius:12,border:`1px solid ${C.border}`,padding:"16px 14px",minWidth:155,flex:tower.id==="B"?2:1}}>
      <div style={{marginBottom:14}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:8}}>
          <h2 style={{fontSize:15,fontWeight:800,color:C.textP}}>{tower.name}</h2>
          <div style={{display:"flex",gap:4}}>
            {r>0&&<span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:10,background:"#1C0404",color:"#EF4444",padding:"2px 7px",borderRadius:4,fontWeight:600}}>{r}</span>}
            {y>0&&<span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:10,background:"#1C1500",color:"#F59E0B",padding:"2px 7px",borderRadius:4,fontWeight:600}}>{y}</span>}
          </div>
        </div>
        <div style={{display:"inline-block",background:tower.sb,color:tower.sc,fontSize:9,fontWeight:700,padding:"3px 8px",borderRadius:4,letterSpacing:.8,border:`1px solid ${tower.sc}22`}}>
          {tower.stage.toUpperCase()}
        </div>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:5}}>
        {tower.floors.map(fl=>(
          <div key={fl.l} style={{display:"flex",alignItems:"center",gap:6}}>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:9,color:C.textM,width:24,textAlign:"right",flexShrink:0}}>{fl.l}</div>
            <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>
              {fl.u.map(uid=>{
                const st=getStatus(uid,blocks,activities),cfg=ST[st],isSel=sel===uid;
                const hasPhoto=Object.values(blocks[uid]||[]).some(b=>b.fotos?.length>0);
                return(
                  <div key={uid} className="cell" onClick={()=>onSel(isSel?null:uid)} style={{
                    width:36,height:36,borderRadius:7,background:isSel?cfg.color:cfg.bg,
                    border:`1.5px solid ${isSel?"#FFF":cfg.color}`,
                    boxShadow:isSel?`0 0 0 2px #FFF,${cfg.glow}`:st!=="green"?cfg.glow:"none",
                    display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",position:"relative",
                  }}>
                    <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:8,fontWeight:500,color:isSel?"#000":cfg.color,lineHeight:1}}>{uid}</span>
                    {st==="red"&&!isSel&&<span className="blink" style={{fontSize:5,color:"#EF4444",marginTop:1}}>⬤</span>}
                    {hasPhoto&&!isSel&&<div style={{position:"absolute",top:2,right:2,width:5,height:5,borderRadius:"50%",background:"#3B82F6"}}/>}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      <div style={{marginTop:14,paddingTop:12,borderTop:`1px solid ${C.border}`,display:"flex",justifyContent:"space-around"}}>
        {[["#22C55E",g,"OK"],["#F59E0B",y,"Alerta"],["#EF4444",r,"Bloq"]].map(([c,n,l])=>(
          <div key={l} style={{textAlign:"center"}}>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:16,color:c,fontWeight:500}}>{n}</div>
            <div style={{fontSize:9,color:C.textM,marginTop:2}}>{l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── DETAIL PANEL ────────────────────────────────────────────────────────
function DetailPanel({uid,blocks,activities,status,onClose,onResolve,addFoto}){
  const cfg=ST[status];
  const [conf,setConf]=useState(null);
  const totalFotos=blocks.reduce((a,b)=>a+(b.fotos?.length||0),0);
  return(
    <div style={{padding:20}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:16}}>
        <div>
          <div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:4}}>UNIDAD</div>
          <div style={{fontSize:34,fontWeight:800,color:cfg.color,lineHeight:1}}>{uid}</div>
          {totalFotos>0&&<div style={{fontSize:11,color:"#60A5FA",marginTop:4}}>📷 {totalFotos} foto{totalFotos>1?"s":""} de evidencia</div>}
        </div>
        <button onClick={onClose} style={{background:"none",border:"none",color:C.textM,cursor:"pointer",fontSize:22,padding:4,lineHeight:1}}>×</button>
      </div>

      <div style={{background:cfg.bg,border:`1px solid ${cfg.color}22`,borderRadius:10,padding:"12px 14px",marginBottom:18,display:"flex",alignItems:"center",gap:10}}>
        <div style={{width:10,height:10,borderRadius:"50%",background:cfg.color,boxShadow:cfg.glow,flexShrink:0}}/>
        <div>
          <div style={{fontSize:13,fontWeight:700,color:cfg.color}}>{cfg.label}</div>
          <div style={{fontSize:11,color:C.textM,marginTop:2}}>{blocks.length>0?`${blocks.length} bloqueo${blocks.length>1?"s":""} activo${blocks.length>1?"s":""}`:"Sin bloqueos"}</div>
        </div>
      </div>

      {blocks.length>0&&(
        <>
          <div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:12}}>BLOQUEOS ACTIVOS</div>
          {blocks.map(b=>{
            const d=diasAgo(b.ts),crit=b.problema==="Seguridad"||d>=2;
            const pCfg=PROBLEMAS.find(p=>p.key===b.problema)||{color:C.textS,icon:"•"};
            return(
              <div key={b.id} style={{background:C.elevated,borderRadius:10,padding:"14px",marginBottom:12,borderLeft:`3px solid ${crit?"#EF4444":"#F59E0B"}`}}>
                <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:6}}>
                  <span style={{fontSize:15}}>{pCfg.icon}</span>
                  <span style={{fontSize:13,fontWeight:700,color:C.textP}}>{b.problema}</span>
                  {crit&&<span style={{marginLeft:"auto",fontSize:9,background:"#1C0404",color:"#EF4444",padding:"2px 7px",borderRadius:4,fontWeight:700}}>CRÍTICO</span>}
                </div>
                <div style={{fontSize:12,color:C.textS,lineHeight:1.6,marginBottom:10}}>{b.detalle}</div>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
                  <span style={{fontSize:11,color:C.textM}}>👤 {b.supervisor}</span>
                  <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:11,color:d>=2?"#EF4444":"#F59E0B",background:d>=2?"#1C0404":"#1C1500",padding:"2px 8px",borderRadius:4}}>
                    {d===0?"Hoy":`${d}d abierto`}
                  </span>
                </div>

                {/* FOTOS DEL BLOQUEO */}
                <FotoGallery fotos={b.fotos||[]}/>
                <div style={{marginTop:8,marginBottom:10}}>
                  <FotoUploader fotos={b.fotos||[]} compact onAdd={foto=>addFoto(b.id,foto)}/>
                </div>

                {conf===b.id?(
                  <div style={{display:"flex",gap:6}}>
                    <button onClick={()=>{onResolve(b.id);setConf(null);}} style={{flex:1,background:"#052E16",border:"1px solid #22C55E",color:"#22C55E",borderRadius:7,padding:"8px",cursor:"pointer",fontSize:12,fontWeight:700}}>✓ Confirmar resolución</button>
                    <button onClick={()=>setConf(null)} style={{background:C.elevated,border:`1px solid ${C.border}`,color:C.textM,borderRadius:7,padding:"8px 12px",cursor:"pointer",fontSize:12}}>Cancelar</button>
                  </div>
                ):(
                  <button onClick={()=>setConf(b.id)} style={{width:"100%",background:"#0A1F12",border:"1px solid #22C55E22",color:"#22C55E",borderRadius:7,padding:"9px",cursor:"pointer",fontSize:12,fontWeight:600}}>
                    ✔ Marcar como resuelto
                  </button>
                )}
              </div>
            );
          })}
          {blocks.some(b=>b.problema==="Seguridad"||diasAgo(b.ts)>=2)&&(
            <div style={{background:"#110508",border:"1px solid #3A0F0F",borderRadius:10,padding:"12px 14px",marginTop:4}}>
              <div style={{fontSize:10,color:"#EF4444",fontWeight:700,marginBottom:5,letterSpacing:.5}}>⚠ ACCIÓN REQUERIDA</div>
              <div style={{fontSize:12,color:C.textS,lineHeight:1.6}}>
                {blocks.some(b=>b.problema==="Seguridad")?"Detener trabajos. Notificar prevención y jefe de terreno de inmediato.":"Bloqueo supera 2 días. Escalar a jefe de terreno para resolución prioritaria."}
              </div>
            </div>
          )}
        </>
      )}

      {activities.length>0&&(
        <div style={{marginTop:20}}>
          <div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:12}}>ACTIVIDADES ESTA SEMANA</div>
          {activities.map(act=>{
            const cfg2=EST_CFG[act.estado]||EST_CFG.programado;
            return(
              <div key={act.id} style={{background:C.elevated,borderRadius:8,padding:"10px 12px",marginBottom:8,display:"flex",alignItems:"center",gap:10}}>
                <div style={{width:8,height:8,borderRadius:"50%",background:cfg2.color,flexShrink:0}}/>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{fontSize:11,color:C.textM,marginBottom:2}}>{act.esp}</div>
                  <div style={{fontSize:12,color:C.textS,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{act.desc}</div>
                </div>
                <div style={{fontSize:10,color:cfg2.color,background:cfg2.bg,padding:"2px 7px",borderRadius:4,fontWeight:600,whiteSpace:"nowrap",flexShrink:0}}>{cfg2.label}</div>
              </div>
            );
          })}
        </div>
      )}

      {blocks.length===0&&activities.length===0&&(
        <div style={{textAlign:"center",padding:"40px 16px"}}>
          <div style={{fontSize:42,marginBottom:10}}>✓</div>
          <div style={{fontSize:14,color:"#22C55E",fontWeight:700}}>Sin bloqueos activos</div>
          <div style={{fontSize:12,color:C.textM,marginTop:6}}>Unidad avanzando normalmente</div>
        </div>
      )}
    </div>
  );
}

// ─── REGISTRAR ───────────────────────────────────────────────────────────
function Registrar({blocks,addBlock,onDone}){
  const [step,setStep]=useState(1);
  const [prob,setProb]=useState(null);
  const [unit,setUnit]=useState(null);
  const [sup,setSup]=useState(SUPERVISORES[0]);
  const [nota,setNota]=useState("");
  const [fotos,setFotos]=useState([]);
  const [ok,setOk]=useState(false);
  const [last,setLast]=useState(null);

  const can=prob&&unit&&sup;
  const register=()=>{
    if(!can) return;
    const k=`${unit}|${prob}`;
    if(last&&last.k===k&&Date.now()-last.t<6000) return;
    addBlock(unit,prob,sup,nota,fotos);
    setLast({k,t:Date.now()});
    setOk(true);
    setTimeout(()=>{setOk(false);setProb(null);setUnit(null);setNota("");setFotos([]);setStep(1);onDone();},2000);
  };

  if(ok) return(
    <div style={{height:"100%",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:14}}>
      <div style={{fontSize:62}}>✅</div>
      <div style={{fontSize:22,fontWeight:800,color:"#22C55E"}}>Bloqueo registrado</div>
      <div style={{fontSize:13,color:C.textM}}>{prob} · Unidad {unit}</div>
      {fotos.length>0&&<div style={{fontSize:12,color:"#60A5FA"}}>📷 {fotos.length} foto{fotos.length>1?"s":""} adjunta{fotos.length>1?"s":""}</div>}
      <div style={{fontSize:11,color:C.textM,opacity:.5,marginTop:4}}>Redirigiendo al dashboard...</div>
    </div>
  );

  return(
    <div className="fu" style={{maxWidth:620,margin:"0 auto",padding:"24px"}}>
      <div style={{marginBottom:22}}>
        <h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Registrar bloqueo</h1>
        <p style={{fontSize:13,color:C.textM,marginTop:5}}>Registra el problema con evidencia fotográfica en 3 pasos</p>
      </div>

      {/* Stepper */}
      <div style={{display:"flex",background:C.surface,borderRadius:10,border:`1px solid ${C.border}`,overflow:"hidden",marginBottom:24}}>
        {[{n:1,l:"Problema"},{n:2,l:"Unidad"},{n:3,l:"Confirmar"}].map(({n,l},i)=>{
          const done=step>n,active=step===n;
          return(
            <div key={n} onClick={()=>n<step&&setStep(n)} style={{flex:1,padding:"12px",display:"flex",alignItems:"center",gap:10,cursor:n<step?"pointer":"default",background:active?C.elevated:"transparent",borderRight:i<2?`1px solid ${C.border}`:"none",transition:"background .15s"}}>
              <div style={{width:26,height:26,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,fontWeight:700,background:done?"#22C55E":active?C.blue:"#1E293B",color:"#FFF",flexShrink:0,fontFamily:"'JetBrains Mono',monospace",transition:"background .2s"}}>
                {done?"✓":n}
              </div>
              <div>
                <div style={{fontSize:11,fontWeight:600,color:active?C.textP:C.textM}}>{l}</div>
                {n===1&&prob&&<div style={{fontSize:10,color:PROBLEMAS.find(p=>p.key===prob)?.color,marginTop:1}}>{prob}</div>}
                {n===2&&unit&&<div style={{fontSize:10,color:"#60A5FA",marginTop:1}}>Unidad {unit}</div>}
              </div>
            </div>
          );
        })}
      </div>

      {step===1&&(
        <div className="fu">
          <div style={{fontSize:13,color:C.textM,marginBottom:16}}>¿Qué tipo de problema encontraste?</div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
            {PROBLEMAS.map(p=>(
              <button key={p.key} onClick={()=>{setProb(p.key);setStep(2);}} style={{background:C.surface,border:`1.5px solid ${C.border}`,borderRadius:12,padding:"18px 16px",cursor:"pointer",textAlign:"left",transition:"all .15s"}}
              onMouseEnter={e=>{e.currentTarget.style.borderColor=p.color;e.currentTarget.style.background=C.elevated;}}
              onMouseLeave={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.background=C.surface;}}>
                <div style={{fontSize:26,marginBottom:8}}>{p.icon}</div>
                <div style={{fontSize:14,fontWeight:700,color:p.color,marginBottom:3}}>{p.key}</div>
                <div style={{fontSize:11,color:C.textM}}>{p.desc}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {step===2&&(
        <div className="fu">
          <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:16}}>
            <span style={{fontSize:13,fontWeight:600,color:PROBLEMAS.find(p=>p.key===prob)?.color,background:`${PROBLEMAS.find(p=>p.key===prob)?.color}15`,padding:"4px 12px",borderRadius:20}}>
              {PROBLEMAS.find(p=>p.key===prob)?.icon} {prob}
            </span>
            <button onClick={()=>{setProb(null);setStep(1);}} style={{background:"none",border:"none",color:C.textM,fontSize:11,cursor:"pointer",textDecoration:"underline"}}>cambiar</button>
          </div>
          <div style={{fontSize:13,color:C.textM,marginBottom:14}}>¿En qué unidad está el problema?</div>
          <div style={{display:"flex",flexDirection:"column",gap:10}}>
            {TOWERS.map(tw=>(
              <div key={tw.id} style={{background:C.surface,borderRadius:10,border:`1px solid ${C.border}`,padding:"14px"}}>
                <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}>
                  <span style={{fontSize:14,fontWeight:700,color:C.textP}}>{tw.name}</span>
                  <span style={{fontSize:9,background:tw.sb,color:tw.sc,padding:"2px 8px",borderRadius:4,fontWeight:700,letterSpacing:.5}}>{tw.stage}</span>
                </div>
                <div style={{display:"flex",flexDirection:"column",gap:5}}>
                  {tw.floors.map(fl=>(
                    <div key={fl.l} style={{display:"flex",alignItems:"center",gap:6}}>
                      <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:9,color:C.textM,width:24,textAlign:"right"}}>{fl.l}</div>
                      <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>
                        {fl.u.map(uid=>{
                          const st=getStatus(uid,blocks,[]),cfg=ST[st],isSel=unit===uid;
                          return(
                            <div key={uid} className="cell" onClick={()=>{setUnit(uid);setStep(3);}} style={{width:36,height:36,borderRadius:7,background:isSel?"#1D4ED8":cfg.bg,border:`1.5px solid ${isSel?"#3B82F6":cfg.color}`,display:"flex",alignItems:"center",justifyContent:"center"}}>
                              <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:8,color:isSel?"#FFF":cfg.color}}>{uid}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {step===3&&(
        <div className="fu">
          <div style={{background:C.elevated,border:`1px solid ${C.borderL}`,borderRadius:10,padding:"16px",marginBottom:20,display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
            <div>
              <div style={{fontSize:9,color:C.textM,letterSpacing:1.5,marginBottom:6}}>PROBLEMA</div>
              <div style={{fontSize:15,fontWeight:700,color:PROBLEMAS.find(p=>p.key===prob)?.color}}>{PROBLEMAS.find(p=>p.key===prob)?.icon} {prob}</div>
            </div>
            <div>
              <div style={{fontSize:9,color:C.textM,letterSpacing:1.5,marginBottom:6}}>UNIDAD</div>
              <div style={{fontSize:24,fontWeight:800,color:"#60A5FA"}}>{unit}</div>
            </div>
            <button onClick={()=>{setProb(null);setStep(1);}} style={{background:"none",border:`1px solid ${C.border}`,color:C.textM,borderRadius:6,padding:"5px 10px",cursor:"pointer",fontSize:10}}>cambiar problema</button>
            <button onClick={()=>{setUnit(null);setStep(2);}} style={{background:"none",border:`1px solid ${C.border}`,color:C.textM,borderRadius:6,padding:"5px 10px",cursor:"pointer",fontSize:10}}>cambiar unidad</button>
          </div>

          <div style={{marginBottom:18}}>
            <div style={{fontSize:12,fontWeight:600,color:C.textS,marginBottom:10}}>Supervisor responsable</div>
            <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
              {SUPERVISORES.map(s=>(
                <button key={s} onClick={()=>setSup(s)} style={{background:sup===s?C.blueDim:C.surface,border:`1.5px solid ${sup===s?C.blue:C.border}`,color:sup===s?"#60A5FA":C.textS,borderRadius:8,padding:"8px 16px",cursor:"pointer",fontSize:12,fontWeight:sup===s?700:400,transition:"all .15s"}}>{s}</button>
              ))}
            </div>
          </div>

          {/* FOTOS EN REGISTRO */}
          <div style={{marginBottom:18}}>
            <div style={{fontSize:12,fontWeight:600,color:C.textS,marginBottom:8}}>
              Evidencia fotográfica <span style={{color:C.textM,fontWeight:400}}>(recomendado)</span>
            </div>
            <FotoUploader fotos={fotos} onAdd={f=>setFotos(p=>[...p,f])}/>
          </div>

          <div style={{marginBottom:22}}>
            <div style={{fontSize:12,fontWeight:600,color:C.textS,marginBottom:8}}>
              Observación <span style={{color:C.textM,fontWeight:400}}>(opcional)</span>
            </div>
            <textarea value={nota} onChange={e=>setNota(e.target.value)} placeholder="Describe el problema con más detalle..." style={{width:"100%",background:C.surface,border:`1px solid ${C.border}`,borderRadius:8,color:C.textP,padding:"12px",fontSize:13,resize:"vertical",minHeight:70,fontFamily:"system-ui,sans-serif",lineHeight:1.6,transition:"border .15s"}}
            onFocus={e=>e.target.style.borderColor=C.blue}
            onBlur={e=>e.target.style.borderColor=C.border}/>
          </div>

          <button onClick={register} disabled={!can} style={{width:"100%",padding:"15px",borderRadius:10,border:"none",cursor:"pointer",background:can?"linear-gradient(135deg,#1D4ED8,#2563EB)":"#1E293B",color:can?"#FFF":C.textM,fontSize:15,fontWeight:700,letterSpacing:.3,transition:"all .2s",boxShadow:can?"0 4px 24px #2563EB33":"none"}}>
            {can?`Registrar bloqueo${fotos.length>0?` · 📷 ${fotos.length} foto${fotos.length>1?"s":""}`:""}  →`:"Completa todos los campos"}
          </button>
        </div>
      )}
    </div>
  );
}
