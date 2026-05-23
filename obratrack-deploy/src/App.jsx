import { useState, useCallback, useRef, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

// ═══════════════════════════════════════════════════════════════
// CONSTANTES
// ═══════════════════════════════════════════════════════════════
const SUPERVISORES   = ["Juan G.", "Carlos M.", "Pedro A.", "María S."];
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

// ═══════════════════════════════════════════════════════════════
// DEMO DATA
// ═══════════════════════════════════════════════════════════════
const ago = d => new Date(Date.now()-d*86400000).toISOString();
const DEMO_BLOCKS = {
  "31":[{id:1,problema:"Falta material",   detalle:"Porcelanato 60×60 sin stock en bodega",              supervisor:"Carlos M.",ts:ago(3),fotos:[]}],
  "22":[{id:2,problema:"Error ejecución",  detalle:"Nivelación de piso fuera de tolerancia ±5mm",        supervisor:"Pedro A.", ts:ago(3),fotos:[]}],
  "52":[{id:3,problema:"Interferencia",    detalle:"Instalación eléctrica sin terminar, bloquea pintura", supervisor:"Juan G.",  ts:ago(1),fotos:[]}],
  "45":[{id:4,problema:"Seguridad",        detalle:"Andamio sin revisión técnica — área clausurada",      supervisor:"Juan G.",  ts:ago(0),fotos:[]}],
  "13":[{id:5,problema:"Error ejecución",  detalle:"Tabique mal posicionado — demolición parcial",        supervisor:"Pedro A.", ts:ago(4),fotos:[]}],
  "56":[{id:6,problema:"Falta material",   detalle:"Ventanas sin instalar — retraso proveedor 7 días",    supervisor:"Pedro A.", ts:ago(3),fotos:[]}],
  "34":[{id:7,problema:"Falta material",   detalle:"Cerámica baño principal agotada",                     supervisor:"María S.", ts:ago(2),fotos:[]}],
};
const DEMO_MATERIALES = [
  {id:1, nombre:"Porcelanato 60×60",         unidad:"m²",    cat:"Terminaciones", stockActual:45,  stockMinimo:200, stockCritico:80,  ubicacion:"Bodega A - Est.1", movimientos:[], solicitudes:[]},
  {id:2, nombre:"Cerámica baño 30×30",        unidad:"m²",    cat:"Terminaciones", stockActual:180, stockMinimo:150, stockCritico:60,  ubicacion:"Bodega A - Est.2", movimientos:[], solicitudes:[]},
  {id:3, nombre:"Pintura látex blanca",        unidad:"galón", cat:"Terminaciones", stockActual:55,  stockMinimo:80,  stockCritico:25,  ubicacion:"Bodega A - Est.4", movimientos:[], solicitudes:[]},
  {id:4, nombre:"Estuco fino",                 unidad:"saco",  cat:"Terminaciones", stockActual:28,  stockMinimo:100, stockCritico:30,  ubicacion:"Bodega A - Est.5", movimientos:[], solicitudes:[]},
  {id:5, nombre:"Puertas interior",            unidad:"un",    cat:"Terminaciones", stockActual:8,   stockMinimo:20,  stockCritico:10,  ubicacion:"Bodega B - Z.1",   movimientos:[], solicitudes:[]},
  {id:6, nombre:"Ventanas aluminio",           unidad:"un",    cat:"Terminaciones", stockActual:4,   stockMinimo:15,  stockCritico:6,   ubicacion:"Bodega B - Z.2",   movimientos:[], solicitudes:[]},
  {id:7, nombre:"Fierro Ø10 A630-420H",       unidad:"barra", cat:"Obra Gruesa",   stockActual:180, stockMinimo:500, stockCritico:150, ubicacion:"Patio - Rack A",   movimientos:[], solicitudes:[]},
  {id:8, nombre:"Fierro Ø12 A630-420H",       unidad:"barra", cat:"Obra Gruesa",   stockActual:220, stockMinimo:300, stockCritico:100, ubicacion:"Patio - Rack B",   movimientos:[], solicitudes:[]},
  {id:9, nombre:"Moldaje fenólico 18mm",      unidad:"m²",    cat:"Obra Gruesa",   stockActual:650, stockMinimo:800, stockCritico:300, ubicacion:"Patio - Moldaje",  movimientos:[], solicitudes:[]},
  {id:10,nombre:"Alambre de amarre",           unidad:"kg",    cat:"Obra Gruesa",   stockActual:45,  stockMinimo:100, stockCritico:40,  ubicacion:"Bodega A - Est.8", movimientos:[], solicitudes:[]},
  {id:11,nombre:"Membrana impermeabilizante",  unidad:"m²",    cat:"General",       stockActual:320, stockMinimo:200, stockCritico:80,  ubicacion:"Bodega B - Z.4",   movimientos:[], solicitudes:[]},
  {id:12,nombre:"Tornillos autoperforantes",   unidad:"caja",  cat:"General",       stockActual:12,  stockMinimo:30,  stockCritico:10,  ubicacion:"Bodega A - Est.9", movimientos:[], solicitudes:[]},
];

// ═══════════════════════════════════════════════════════════════
// UTILS
// ═══════════════════════════════════════════════════════════════
const diasAgo     = ts => Math.floor((Date.now()-new Date(ts).getTime())/86400000);
const C = {
  bg:"#070B14",surface:"#0D1321",elevated:"#111B2E",border:"#1E2E47",borderL:"#243652",
  textP:"#E8EFF8",textS:"#8EA3BE",textM:"#4A6280",blue:"#3B82F6",blueDim:"#0F2347",
};

function getStatus(uid,blocks){
  const b=blocks[uid]||[];
  if(!b.length) return "green";
  if(b.some(x=>x.problema==="Seguridad"||diasAgo(x.ts)>=2)) return "red";
  return "yellow";
}
function getStockStatus(mat){
  if(mat.stockActual<mat.stockCritico)  return "red";
  if(mat.stockActual<mat.stockMinimo)   return "yellow";
  return "green";
}
const ST={
  green: {color:"#22C55E",bg:"#052E16",glow:"0 0 12px #22C55E44",label:"Avanzando"},
  yellow:{color:"#F59E0B",bg:"#1C1500",glow:"0 0 12px #F59E0B44",label:"Cuello de botella"},
  red:   {color:"#EF4444",bg:"#1C0404",glow:"0 0 12px #EF444444",label:"Paralizado"},
};
const SCOLOR={
  green: {color:"#22C55E",bg:"#052E16",label:"Stock OK",  icon:"✓"},
  yellow:{color:"#F59E0B",bg:"#1C1500",label:"Alerta",    icon:"▲"},
  red:   {color:"#EF4444",bg:"#1C0404",label:"Crítico",   icon:"●"},
};

function computeStats(blocks,materiales){
  let total=0,g=0,y=0,r=0;
  const all=Object.values(blocks).flat();
  const crit=all.filter(b=>b.problema==="Seguridad"||diasAgo(b.ts)>=2);
  const byP={},byS={};
  all.forEach(b=>{byP[b.problema]=(byP[b.problema]||0)+1;byS[b.supervisor]=(byS[b.supervisor]||0)+1;});
  TOWERS.forEach(tw=>tw.floors.forEach(fl=>fl.u.forEach(uid=>{
    total++;const s=getStatus(uid,blocks);
    if(s==="green")g++;else if(s==="yellow")y++;else r++;
  })));
  const avg=all.length>0?(all.reduce((a,b)=>a+diasAgo(b.ts),0)/all.length).toFixed(1):0;
  const matCrit=materiales.filter(m=>getStockStatus(m)==="red").length;
  return {total,g,y,r,all,crit,byP,byS,avg,matCrit};
}

function buildContext(blocks,materiales){
  const all=Object.values(blocks).flat();
  const crit=all.filter(b=>b.problema==="Seguridad"||diasAgo(b.ts)>=2);
  const bloqList=Object.entries(blocks).map(([uid,bs])=>
    bs.map(b=>`  • Unidad ${uid}: ${b.problema} | ${b.supervisor} | ${diasAgo(b.ts)===0?"Hoy":`${diasAgo(b.ts)}d`} | ${b.detalle}`).join("\n")
  ).join("\n");
  const bySup={};all.forEach(b=>{bySup[b.supervisor]=(bySup[b.supervisor]||0)+1;});
  const supRank=Object.entries(bySup).sort((a,b)=>b[1]-a[1]).map(([s,n])=>`  • ${s}: ${n}`).join("\n");
  const byProb={};all.forEach(b=>{byProb[b.problema]=(byProb[b.problema]||0)+1;});
  const probRank=Object.entries(byProb).sort((a,b)=>b[1]-a[1]).map(([p,n])=>`  • ${p}: ${n}`).join("\n");
  const matCrit=materiales.filter(m=>m.stockActual<m.stockCritico);
  const matAler=materiales.filter(m=>m.stockActual>=m.stockCritico&&m.stockActual<m.stockMinimo);
  const fecha=new Date().toLocaleDateString("es-CL",{weekday:"long",day:"numeric",month:"long",year:"numeric"});
  return `PROYECTO: Residencial Las Torres\nFECHA: ${fecha}\n\nBLOQUEOS ACTIVOS: ${all.length} (críticos: ${crit.length})\n\nDETALLE BLOQUEOS:\n${bloqList||"Sin bloqueos."}\n\nRANKING SUPERVISORES:\n${supRank||"Sin datos."}\n\nRANKING PROBLEMAS:\n${probRank||"Sin datos."}\n\nMATERIALES CRÍTICOS:\n${matCrit.map(m=>`  • ${m.nombre}: ${m.stockActual}/${m.stockCritico} ${m.unidad}`).join("\n")||"Sin críticos."}\n\nMATERIALES EN ALERTA:\n${matAler.map(m=>`  • ${m.nombre}: ${m.stockActual}/${m.stockMinimo} ${m.unidad}`).join("\n")||"Sin alertas."}`;
}

const CTip=({active,payload})=>{
  if(!active||!payload?.length) return null;
  return <div style={{background:C.elevated,border:`1px solid ${C.border}`,borderRadius:8,padding:"8px 12px"}}>
    <div style={{fontSize:10,color:C.textS,marginBottom:2}}>{payload[0]?.payload?.fullName||payload[0]?.name}</div>
    <div style={{fontSize:18,fontWeight:600,color:C.textP,fontFamily:"monospace"}}>{payload[0]?.value}</div>
  </div>;
};

async function readFileAsBase64(file){
  return new Promise((res,rej)=>{const r=new FileReader();r.onload=()=>res(r.result);r.onerror=rej;r.readAsDataURL(file);});
}

// ═══════════════════════════════════════════════════════════════
// APP
// ═══════════════════════════════════════════════════════════════
export default function App(){
  const [blocks,    setBlocks]    = useState(DEMO_BLOCKS);
  const [materiales,setMateriales]= useState(DEMO_MATERIALES);
  const [view,      setView]      = useState("dashboard");
  const [sel,       setSel]       = useState(null);

  const addBlock=useCallback((uid,problema,supervisor,nota,fotos=[])=>{
    setBlocks(p=>({...p,[uid]:[...(p[uid]||[]),{id:Date.now(),problema,detalle:nota||"Sin observación",supervisor,ts:new Date().toISOString(),fotos}]}));
  },[]);
  const resolveBlock=useCallback((uid,id)=>{
    setBlocks(p=>{const u=(p[uid]||[]).filter(b=>b.id!==id);const n={...p};if(!u.length)delete n[uid];else n[uid]=u;return n;});
  },[]);
  const addFotoBlock=useCallback((uid,bid,foto)=>{
    setBlocks(p=>({...p,[uid]:(p[uid]||[]).map(b=>b.id===bid?{...b,fotos:[...(b.fotos||[]),foto]}:b)}));
  },[]);

  const stats=computeStats(blocks,materiales);
  const context=buildContext(blocks,materiales);

  return(
    <div style={{display:"flex",height:"100vh",background:C.bg,color:C.textP,overflow:"hidden",fontFamily:"'Plus Jakarta Sans',system-ui,sans-serif"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        *{box-sizing:border-box;margin:0;padding:0}
        ::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-thumb{background:#1E2E47;border-radius:2px}
        .cell{transition:transform .1s,box-shadow .1s;cursor:pointer}.cell:hover{transform:scale(1.12);z-index:20}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}.blink{animation:blink 2s infinite}
        @keyframes fu{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.fu{animation:fu .25s ease}
        @keyframes sr{from{opacity:0;transform:translateX(14px)}to{opacity:1;transform:translateX(0)}}.sr{animation:sr .2s ease}
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
        .nav:hover{background:#111B2E!important}.kpi{transition:all .18s}.kpi:hover{transform:translateY(-2px)}
        button:focus,textarea:focus,input:focus,select:focus{outline:none}
      `}</style>

      <Sidebar view={view} setView={v=>{setView(v);setSel(null);}} stats={stats}/>
      <div style={{flex:1,overflow:"hidden",display:"flex",flexDirection:"column"}}>
        <Topbar/>
        <div style={{flex:1,overflow:"auto"}}>
          {view==="dashboard" && <Dashboard stats={stats} blocks={blocks} materiales={materiales}/>}
          {view==="panel"     && <Panel blocks={blocks} sel={sel} setSel={setSel} resolve={resolveBlock} addFoto={addFotoBlock}/>}
          {view==="registrar" && <Registrar blocks={blocks} addBlock={addBlock} onDone={()=>setView("dashboard")}/>}
          {view==="bodega"    && <BodegaView materiales={materiales} setMateriales={setMateriales}/>}
          {view==="informe"   && <InformeIA blocks={blocks} materiales={materiales}/>}
          {view==="chat"      && <ChatObra blocks={blocks} materiales={materiales} context={context}/>}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// TOPBAR
// ═══════════════════════════════════════════════════════════════
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

// ═══════════════════════════════════════════════════════════════
// SIDEBAR
// ═══════════════════════════════════════════════════════════════
function Sidebar({view,setView,stats}){
  const nav=[
    {id:"dashboard",icon:"▦", label:"Dashboard"},
    {id:"panel",    icon:"⊞", label:"Panel Obra"},
    {id:"registrar",icon:"⊕", label:"Registrar"},
    {id:"bodega",   icon:"📦",label:"Bodega",     badge:stats.matCrit>0?stats.matCrit:null,  badgeColor:"#EF4444"},
    {id:"informe",  icon:"📊",label:"Informe IA"},
    {id:"chat",     icon:"✦", label:"Chat Obra"},
  ];
  return(
    <div style={{width:200,background:C.surface,borderRight:`1px solid ${C.border}`,display:"flex",flexDirection:"column",flexShrink:0}}>
      <div style={{padding:"18px 16px 16px",borderBottom:`1px solid ${C.border}`}}>
        <div style={{display:"flex",alignItems:"center",gap:10}}>
          <div style={{width:34,height:34,borderRadius:9,background:"linear-gradient(135deg,#1D4ED8,#7C3AED)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:18}}>🏗</div>
          <div>
            <div style={{fontSize:14,fontWeight:800,color:C.textP,lineHeight:1,letterSpacing:"-.3px"}}>ObraTrack</div>
            <div style={{fontSize:9,color:C.textM,marginTop:3,letterSpacing:1}}>CONTROL OPERATIVO</div>
          </div>
        </div>
      </div>
      <div style={{padding:"14px 10px",flex:1}}>
        <div style={{fontSize:9,color:C.textM,letterSpacing:2,padding:"0 8px",marginBottom:8}}>MÓDULOS</div>
        {nav.map(item=>{
          const on=view===item.id;
          return(
            <div key={item.id} className="nav" onClick={()=>setView(item.id)} style={{
              display:"flex",alignItems:"center",gap:10,padding:"9px 12px",borderRadius:8,marginBottom:2,cursor:"pointer",
              background:on?"linear-gradient(135deg,#0F2347,#162B52)":"transparent",
              border:on?`1px solid #3B82F622`:`1px solid transparent`,transition:"all .15s",
            }}>
              <span style={{fontSize:15,opacity:on?1:.5}}>{item.icon}</span>
              <span style={{fontSize:13,fontWeight:on?700:400,color:on?"#60A5FA":C.textS,flex:1}}>{item.label}</span>
              {item.badge&&<span style={{background:item.badgeColor,color:"#FFF",fontSize:10,fontWeight:700,padding:"1px 6px",borderRadius:10}}>{item.badge}</span>}
            </div>
          );
        })}
      </div>
      <div style={{padding:"14px 18px",borderTop:`1px solid ${C.border}`}}>
        <div style={{fontSize:10,color:C.textM}}>v2.0 · © 2026 ObraTrack</div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════
function Dashboard({stats,blocks,materiales}){
  const {total,g,y,r,all,crit,byP,byS,avg,matCrit}=stats;
  const probData=PROBLEMAS.map(p=>({name:p.icon+" "+p.key.split(" ")[0],fullName:p.key,value:byP[p.key]||0,color:p.color})).filter(x=>x.value>0).sort((a,b)=>b.value-a.value);
  const supData=Object.entries(byS).sort((a,b)=>b[1]-a[1]).map(([nm,v])=>({name:nm.split(" ")[0],fullName:nm,value:v}));
  const pieData=[{name:"Avanzando",value:g,color:"#22C55E"},{name:"Alerta",value:y,color:"#F59E0B"},{name:"Paralizado",value:r,color:"#EF4444"}].filter(x=>x.value>0);
  return(
    <div className="fu" style={{padding:"24px",maxWidth:1080}}>
      <div style={{marginBottom:22}}>
        <h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Dashboard</h1>
        <p style={{fontSize:13,color:C.textM,marginTop:5}}>{new Date().toLocaleDateString("es-CL",{weekday:"long",day:"numeric",month:"long",year:"numeric"})}</p>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(5,1fr)",gap:12,marginBottom:20}}>
        {[
          {label:"Unidades libres",  value:`${g}/${total}`,sub:`${Math.round((g/total)*100)}% avanzando`,   color:"#22C55E",icon:"✓"},
          {label:"Bloqueos activos", value:all.length,      sub:`${y} alerta · ${r} paralizados`,            color:"#F59E0B",icon:"⚠"},
          {label:"Críticos",         value:crit.length,     sub:"Seg. o +2 días abierto",                    color:"#EF4444",icon:"!"},
          {label:"Días promedio",    value:`${avg}d`,        sub:"por bloqueo activo",                        color:C.blue,   icon:"⏱"},
          {label:"Mat. críticos",    value:matCrit,          sub:"bajo stock crítico en bodega",              color:matCrit>0?"#EF4444":"#22C55E",icon:"📦"},
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
                <XAxis type="number" hide/><YAxis type="category" dataKey="name" tick={{fill:C.textS,fontSize:11}} width={90} axisLine={false} tickLine={false}/>
                <Tooltip content={<CTip/>}/>
                <Bar dataKey="value" radius={[0,5,5,0]} background={{fill:C.elevated,radius:4}}>{probData.map((e,i)=><Cell key={i} fill={e.color}/>)}</Bar>
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
                <Tooltip content={<CTip/>}/><Bar dataKey="value" fill={C.blue} radius={[5,5,0,0]}/>
              </BarChart>
            </ResponsiveContainer>
          ):<div style={{height:165,display:"flex",alignItems:"center",justifyContent:"center",color:C.textM,fontSize:13}}>Sin datos</div>}
        </div>
        <div style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"18px 20px"}}>
          <div style={{fontSize:13,fontWeight:700,color:C.textP,marginBottom:3}}>Estado proyecto</div>
          <div style={{fontSize:11,color:C.textM,marginBottom:6}}>{total} unidades</div>
          <ResponsiveContainer width="100%" height={120}>
            <PieChart><Pie data={pieData} cx="50%" cy="50%" innerRadius={32} outerRadius={52} paddingAngle={3} dataKey="value">{pieData.map((e,i)=><Cell key={i} fill={e.color}/>)}</Pie><Tooltip content={<CTip/>}/></PieChart>
          </ResponsiveContainer>
          <div style={{display:"flex",flexDirection:"column",gap:7,marginTop:4}}>
            {pieData.map(p=>(
              <div key={p.name} style={{display:"flex",alignItems:"center",justifyContent:"space-between"}}>
                <div style={{display:"flex",alignItems:"center",gap:7}}><div style={{width:8,height:8,borderRadius:2,background:p.color}}/><span style={{fontSize:11,color:C.textS}}>{p.name}</span></div>
                <div style={{display:"flex",gap:6}}><span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:12,color:p.color,fontWeight:500}}>{p.value}</span><span style={{fontSize:10,color:C.textM}}>{Math.round((p.value/total)*100)}%</span></div>
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
          <div style={{display:"grid",gridTemplateColumns:"70px 1fr 130px 110px 80px",gap:10,padding:"0 10px",marginBottom:8}}>
            {["Unidad","Detalle","Supervisor","Tipo","Abierto"].map(h=><div key={h} style={{fontSize:10,color:C.textM,fontWeight:600,letterSpacing:.5}}>{h.toUpperCase()}</div>)}
          </div>
          {crit.map(b=>{
            let uid="?";Object.entries(blocks).forEach(([u,bs])=>{if(bs.some(x=>x.id===b.id))uid=u;});
            const d=diasAgo(b.ts),pCfg=PROBLEMAS.find(p=>p.key===b.problema)||{color:C.textS,icon:"•"};
            return(
              <div key={b.id} style={{display:"grid",gridTemplateColumns:"70px 1fr 130px 110px 80px",gap:10,padding:"10px",background:C.elevated,borderRadius:8,marginBottom:6,alignItems:"center"}}>
                <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:13,fontWeight:600,color:"#60A5FA"}}>{uid}</div>
                <div style={{fontSize:12,color:C.textS,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{b.detalle}</div>
                <div style={{fontSize:12,color:C.textS}}>👤 {b.supervisor}</div>
                <div style={{display:"flex",alignItems:"center",gap:5}}><span>{pCfg.icon}</span><span style={{fontSize:11,color:pCfg.color,fontWeight:600}}>{b.problema.split(" ")[0]}</span></div>
                <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:11,color:d>=2?"#EF4444":"#F59E0B",background:d>=2?"#1C0404":"#1C1500",padding:"3px 8px",borderRadius:5,textAlign:"center"}}>{d===0?"Hoy":`${d}d`}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// PANEL + TOWER CARD + DETAIL PANEL
// ═══════════════════════════════════════════════════════════════
function FotoUploader({fotos=[],onAdd,compact=false}){
  const ref=useRef();
  const handle=async(e)=>{const files=Array.from(e.target.files||[]);for(const f of files){if(!f.type.startsWith("image/"))continue;const b64=await readFileAsBase64(f);onAdd(b64);}e.target.value="";};
  return(
    <div>
      <input ref={ref} type="file" accept="image/*" multiple onChange={handle} style={{display:"none"}}/>
      {!compact&&fotos.length>0&&<div style={{display:"flex",flexWrap:"wrap",gap:6,marginBottom:8}}>{fotos.map((src,i)=><div key={i} style={{width:64,height:64,borderRadius:6,overflow:"hidden",border:`1px solid ${C.border}`}}><img src={src} alt="" style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>)}</div>}
      <button onClick={()=>ref.current?.click()} style={{background:C.elevated,border:`1px dashed ${C.borderL}`,color:C.textS,borderRadius:7,padding:compact?"5px 10px":"7px 14px",cursor:"pointer",fontSize:compact?11:12,display:"flex",alignItems:"center",gap:6}}>
        <span>📷</span><span>{fotos.length>0?`${fotos.length} foto${fotos.length>1?"s":""} · agregar más`:"Adjuntar foto"}</span>
      </button>
    </div>
  );
}
function FotoGallery({fotos=[]}){
  const [big,setBig]=useState(null);
  if(!fotos.length) return null;
  return(<>
    <div style={{display:"flex",flexWrap:"wrap",gap:6,marginTop:8}}>{fotos.map((src,i)=><div key={i} onClick={()=>setBig(src)} style={{width:68,height:68,borderRadius:7,overflow:"hidden",border:`1px solid ${C.border}`,cursor:"pointer"}}><img src={src} alt="" style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>)}</div>
    {big&&<div onClick={()=>setBig(null)} style={{position:"fixed",inset:0,background:"#000000CC",zIndex:1000,display:"flex",alignItems:"center",justifyContent:"center",cursor:"zoom-out"}}><img src={big} alt="" style={{maxWidth:"90vw",maxHeight:"90vh",borderRadius:10}}/></div>}
  </>);
}
function Panel({blocks,sel,setSel,resolve,addFoto}){
  return(
    <div className="fu" style={{display:"flex",height:"100%",overflow:"hidden"}}>
      <div style={{flex:1,overflow:"auto",padding:"24px"}}>
        <div style={{marginBottom:20}}><h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Panel de Obra</h1><p style={{fontSize:13,color:C.textM,marginTop:5}}>Toca una unidad para ver detalle y gestionar bloqueos</p></div>
        <div style={{display:"flex",gap:14,alignItems:"flex-start",flexWrap:"wrap"}}>{TOWERS.map(tw=><TowerCard key={tw.id} tower={tw} blocks={blocks} sel={sel} onSel={setSel}/>)}</div>
      </div>
      {sel&&<div className="sr" style={{width:340,background:C.surface,borderLeft:`1px solid ${C.border}`,overflow:"auto",flexShrink:0}}><DetailPanel uid={sel} blocks={blocks[sel]||[]} status={getStatus(sel,blocks)} onClose={()=>setSel(null)} onResolve={id=>resolve(sel,id)} addFoto={(bid,foto)=>addFoto(sel,bid,foto)}/></div>}
    </div>
  );
}
function TowerCard({tower,blocks,sel,onSel}){
  let g=0,y=0,r=0;tower.floors.forEach(f=>f.u.forEach(u=>{const s=getStatus(u,blocks);if(s==="green")g++;else if(s==="yellow")y++;else r++;}));
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
        <div style={{display:"inline-block",background:tower.sb,color:tower.sc,fontSize:9,fontWeight:700,padding:"3px 8px",borderRadius:4,letterSpacing:.8,border:`1px solid ${tower.sc}22`}}>{tower.stage.toUpperCase()}</div>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:5}}>
        {tower.floors.map(fl=>(
          <div key={fl.l} style={{display:"flex",alignItems:"center",gap:6}}>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:9,color:C.textM,width:24,textAlign:"right",flexShrink:0}}>{fl.l}</div>
            <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>
              {fl.u.map(uid=>{const st=getStatus(uid,blocks),cfg=ST[st],isSel=sel===uid;return(
                <div key={uid} className="cell" onClick={()=>onSel(isSel?null:uid)} style={{width:36,height:36,borderRadius:7,background:isSel?cfg.color:cfg.bg,border:`1.5px solid ${isSel?"#FFF":cfg.color}`,boxShadow:isSel?`0 0 0 2px #FFF,${cfg.glow}`:st!=="green"?cfg.glow:"none",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center"}}>
                  <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:8,fontWeight:500,color:isSel?"#000":cfg.color,lineHeight:1}}>{uid}</span>
                  {st==="red"&&!isSel&&<span className="blink" style={{fontSize:5,color:"#EF4444",marginTop:1}}>⬤</span>}
                </div>
              );})}
            </div>
          </div>
        ))}
      </div>
      <div style={{marginTop:14,paddingTop:12,borderTop:`1px solid ${C.border}`,display:"flex",justifyContent:"space-around"}}>
        {[["#22C55E",g,"OK"],["#F59E0B",y,"Alerta"],["#EF4444",r,"Bloq"]].map(([c,n,l])=>(
          <div key={l} style={{textAlign:"center"}}><div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:16,color:c,fontWeight:500}}>{n}</div><div style={{fontSize:9,color:C.textM,marginTop:2}}>{l}</div></div>
        ))}
      </div>
    </div>
  );
}
function DetailPanel({uid,blocks,status,onClose,onResolve,addFoto}){
  const cfg=ST[status];const [conf,setConf]=useState(null);
  return(
    <div style={{padding:20}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:16}}>
        <div><div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:4}}>UNIDAD</div><div style={{fontSize:34,fontWeight:800,color:cfg.color,lineHeight:1}}>{uid}</div></div>
        <button onClick={onClose} style={{background:"none",border:"none",color:C.textM,cursor:"pointer",fontSize:22,padding:4,lineHeight:1}}>×</button>
      </div>
      <div style={{background:cfg.bg,border:`1px solid ${cfg.color}22`,borderRadius:10,padding:"12px 14px",marginBottom:18,display:"flex",alignItems:"center",gap:10}}>
        <div style={{width:10,height:10,borderRadius:"50%",background:cfg.color,boxShadow:cfg.glow,flexShrink:0}}/>
        <div><div style={{fontSize:13,fontWeight:700,color:cfg.color}}>{cfg.label}</div><div style={{fontSize:11,color:C.textM,marginTop:2}}>{blocks.length>0?`${blocks.length} bloqueo${blocks.length>1?"s":""} activo${blocks.length>1?"s":""}`:"Sin bloqueos"}</div></div>
      </div>
      {blocks.length>0?(
        <>{<div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:12}}>BLOQUEOS ACTIVOS</div>}
        {blocks.map(b=>{
          const d=diasAgo(b.ts),crit=b.problema==="Seguridad"||d>=2,pCfg=PROBLEMAS.find(p=>p.key===b.problema)||{color:C.textS,icon:"•"};
          return(
            <div key={b.id} style={{background:C.elevated,borderRadius:10,padding:"14px",marginBottom:12,borderLeft:`3px solid ${crit?"#EF4444":"#F59E0B"}`}}>
              <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:6}}>
                <span style={{fontSize:15}}>{pCfg.icon}</span><span style={{fontSize:13,fontWeight:700,color:C.textP}}>{b.problema}</span>
                {crit&&<span style={{marginLeft:"auto",fontSize:9,background:"#1C0404",color:"#EF4444",padding:"2px 7px",borderRadius:4,fontWeight:700}}>CRÍTICO</span>}
              </div>
              <div style={{fontSize:12,color:C.textS,lineHeight:1.6,marginBottom:10}}>{b.detalle}</div>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
                <span style={{fontSize:11,color:C.textM}}>👤 {b.supervisor}</span>
                <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:11,color:d>=2?"#EF4444":"#F59E0B",background:d>=2?"#1C0404":"#1C1500",padding:"2px 8px",borderRadius:4}}>{d===0?"Hoy":`${d}d abierto`}</span>
              </div>
              <FotoGallery fotos={b.fotos||[]}/>
              <div style={{marginTop:8,marginBottom:10}}><FotoUploader fotos={b.fotos||[]} compact onAdd={foto=>addFoto(b.id,foto)}/></div>
              {conf===b.id?(
                <div style={{display:"flex",gap:6}}>
                  <button onClick={()=>{onResolve(b.id);setConf(null);}} style={{flex:1,background:"#052E16",border:"1px solid #22C55E",color:"#22C55E",borderRadius:7,padding:"8px",cursor:"pointer",fontSize:12,fontWeight:700}}>✓ Confirmar resolución</button>
                  <button onClick={()=>setConf(null)} style={{background:C.elevated,border:`1px solid ${C.border}`,color:C.textM,borderRadius:7,padding:"8px 12px",cursor:"pointer",fontSize:12}}>Cancelar</button>
                </div>
              ):(
                <button onClick={()=>setConf(b.id)} style={{width:"100%",background:"#0A1F12",border:"1px solid #22C55E22",color:"#22C55E",borderRadius:7,padding:"9px",cursor:"pointer",fontSize:12,fontWeight:600}}>✔ Marcar como resuelto</button>
              )}
            </div>
          );
        })}
        {blocks.some(b=>b.problema==="Seguridad"||diasAgo(b.ts)>=2)&&(
          <div style={{background:"#110508",border:"1px solid #3A0F0F",borderRadius:10,padding:"12px 14px"}}>
            <div style={{fontSize:10,color:"#EF4444",fontWeight:700,marginBottom:5}}>⚠ ACCIÓN REQUERIDA</div>
            <div style={{fontSize:12,color:C.textS,lineHeight:1.6}}>{blocks.some(b=>b.problema==="Seguridad")?"Detener trabajos. Notificar a prevención y jefe de terreno de inmediato.":"Bloqueo supera 2 días. Escalar a jefe de terreno para resolución prioritaria."}</div>
          </div>
        )}</>
      ):(
        <div style={{textAlign:"center",padding:"40px 16px"}}><div style={{fontSize:42,marginBottom:10}}>✓</div><div style={{fontSize:14,color:"#22C55E",fontWeight:700}}>Sin bloqueos activos</div></div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// REGISTRAR
// ═══════════════════════════════════════════════════════════════
function Registrar({blocks,addBlock,onDone}){
  const [step,setStep]=useState(1);const [prob,setProb]=useState(null);const [unit,setUnit]=useState(null);
  const [sup,setSup]=useState(SUPERVISORES[0]);const [nota,setNota]=useState("");const [fotos,setFotos]=useState([]);
  const [ok,setOk]=useState(false);const [last,setLast]=useState(null);
  const can=prob&&unit&&sup;
  const register=()=>{
    if(!can)return;const k=`${unit}|${prob}`;
    if(last&&last.k===k&&Date.now()-last.t<6000)return;
    addBlock(unit,prob,sup,nota,fotos);setLast({k,t:Date.now()});setOk(true);
    setTimeout(()=>{setOk(false);setProb(null);setUnit(null);setNota("");setFotos([]);setStep(1);onDone();},2000);
  };
  if(ok)return(<div style={{height:"100%",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",gap:14}}><div style={{fontSize:62}}>✅</div><div style={{fontSize:22,fontWeight:800,color:"#22C55E"}}>Bloqueo registrado</div><div style={{fontSize:13,color:C.textM}}>{prob} · Unidad {unit}</div>{fotos.length>0&&<div style={{fontSize:12,color:"#60A5FA"}}>📷 {fotos.length} foto{fotos.length>1?"s":""} adjunta{fotos.length>1?"s":""}</div>}</div>);
  return(
    <div className="fu" style={{maxWidth:620,margin:"0 auto",padding:"24px"}}>
      <div style={{marginBottom:22}}><h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Registrar bloqueo</h1><p style={{fontSize:13,color:C.textM,marginTop:5}}>Registra el problema con evidencia fotográfica</p></div>
      <div style={{display:"flex",background:C.surface,borderRadius:10,border:`1px solid ${C.border}`,overflow:"hidden",marginBottom:24}}>
        {[{n:1,l:"Problema"},{n:2,l:"Unidad"},{n:3,l:"Confirmar"}].map(({n,l},i)=>{
          const done=step>n,active=step===n;
          return(<div key={n} onClick={()=>n<step&&setStep(n)} style={{flex:1,padding:"12px",display:"flex",alignItems:"center",gap:10,cursor:n<step?"pointer":"default",background:active?C.elevated:"transparent",borderRight:i<2?`1px solid ${C.border}`:"none",transition:"background .15s"}}>
            <div style={{width:26,height:26,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,fontWeight:700,background:done?"#22C55E":active?C.blue:"#1E293B",color:"#FFF",flexShrink:0,fontFamily:"'JetBrains Mono',monospace"}}>{done?"✓":n}</div>
            <div><div style={{fontSize:11,fontWeight:600,color:active?C.textP:C.textM}}>{l}</div>
              {n===1&&prob&&<div style={{fontSize:10,color:PROBLEMAS.find(p=>p.key===prob)?.color,marginTop:1}}>{prob}</div>}
              {n===2&&unit&&<div style={{fontSize:10,color:"#60A5FA",marginTop:1}}>Unidad {unit}</div>}
            </div>
          </div>);
        })}
      </div>
      {step===1&&(<div className="fu"><div style={{fontSize:13,color:C.textM,marginBottom:16}}>¿Qué tipo de problema encontraste?</div><div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
        {PROBLEMAS.map(p=>(<button key={p.key} onClick={()=>{setProb(p.key);setStep(2);}} style={{background:C.surface,border:`1.5px solid ${C.border}`,borderRadius:12,padding:"18px 16px",cursor:"pointer",textAlign:"left",transition:"all .15s"}}
          onMouseEnter={e=>{e.currentTarget.style.borderColor=p.color;e.currentTarget.style.background=C.elevated;}}
          onMouseLeave={e=>{e.currentTarget.style.borderColor=C.border;e.currentTarget.style.background=C.surface;}}>
          <div style={{fontSize:26,marginBottom:8}}>{p.icon}</div><div style={{fontSize:14,fontWeight:700,color:p.color,marginBottom:3}}>{p.key}</div><div style={{fontSize:11,color:C.textM}}>{p.desc}</div>
        </button>))}
      </div></div>)}
      {step===2&&(<div className="fu">
        <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:16}}>
          <span style={{fontSize:13,fontWeight:600,color:PROBLEMAS.find(p=>p.key===prob)?.color,background:`${PROBLEMAS.find(p=>p.key===prob)?.color}15`,padding:"4px 12px",borderRadius:20}}>{PROBLEMAS.find(p=>p.key===prob)?.icon} {prob}</span>
          <button onClick={()=>{setProb(null);setStep(1);}} style={{background:"none",border:"none",color:C.textM,fontSize:11,cursor:"pointer",textDecoration:"underline"}}>cambiar</button>
        </div>
        <div style={{fontSize:13,color:C.textM,marginBottom:14}}>¿En qué unidad está el problema?</div>
        <div style={{display:"flex",flexDirection:"column",gap:10}}>{TOWERS.map(tw=>(
          <div key={tw.id} style={{background:C.surface,borderRadius:10,border:`1px solid ${C.border}`,padding:"14px"}}>
            <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:10}}><span style={{fontSize:14,fontWeight:700,color:C.textP}}>{tw.name}</span><span style={{fontSize:9,background:tw.sb,color:tw.sc,padding:"2px 8px",borderRadius:4,fontWeight:700,letterSpacing:.5}}>{tw.stage}</span></div>
            <div style={{display:"flex",flexDirection:"column",gap:5}}>{tw.floors.map(fl=>(
              <div key={fl.l} style={{display:"flex",alignItems:"center",gap:6}}>
                <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:9,color:C.textM,width:24,textAlign:"right"}}>{fl.l}</div>
                <div style={{display:"flex",gap:4,flexWrap:"wrap"}}>{fl.u.map(uid=>{const st=getStatus(uid,blocks),cfg=ST[st],isSel=unit===uid;return(
                  <div key={uid} className="cell" onClick={()=>{setUnit(uid);setStep(3);}} style={{width:36,height:36,borderRadius:7,background:isSel?"#1D4ED8":cfg.bg,border:`1.5px solid ${isSel?"#3B82F6":cfg.color}`,display:"flex",alignItems:"center",justifyContent:"center"}}>
                    <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:8,color:isSel?"#FFF":cfg.color}}>{uid}</span>
                  </div>);})}</div>
              </div>
            ))}</div>
          </div>
        ))}</div>
      </div>)}
      {step===3&&(<div className="fu">
        <div style={{background:C.elevated,border:`1px solid ${C.borderL}`,borderRadius:10,padding:"16px",marginBottom:20,display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
          <div><div style={{fontSize:9,color:C.textM,letterSpacing:1.5,marginBottom:6}}>PROBLEMA</div><div style={{fontSize:15,fontWeight:700,color:PROBLEMAS.find(p=>p.key===prob)?.color}}>{PROBLEMAS.find(p=>p.key===prob)?.icon} {prob}</div></div>
          <div><div style={{fontSize:9,color:C.textM,letterSpacing:1.5,marginBottom:6}}>UNIDAD</div><div style={{fontSize:24,fontWeight:800,color:"#60A5FA"}}>{unit}</div></div>
          <button onClick={()=>{setProb(null);setStep(1);}} style={{background:"none",border:`1px solid ${C.border}`,color:C.textM,borderRadius:6,padding:"5px 10px",cursor:"pointer",fontSize:10}}>cambiar problema</button>
          <button onClick={()=>{setUnit(null);setStep(2);}} style={{background:"none",border:`1px solid ${C.border}`,color:C.textM,borderRadius:6,padding:"5px 10px",cursor:"pointer",fontSize:10}}>cambiar unidad</button>
        </div>
        <div style={{marginBottom:18}}><div style={{fontSize:12,fontWeight:600,color:C.textS,marginBottom:10}}>Supervisor responsable</div>
          <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>{SUPERVISORES.map(s=>(
            <button key={s} onClick={()=>setSup(s)} style={{background:sup===s?C.blueDim:C.surface,border:`1.5px solid ${sup===s?C.blue:C.border}`,color:sup===s?"#60A5FA":C.textS,borderRadius:8,padding:"8px 16px",cursor:"pointer",fontSize:12,fontWeight:sup===s?700:400,transition:"all .15s"}}>{s}</button>
          ))}</div>
        </div>
        <div style={{marginBottom:18}}><div style={{fontSize:12,fontWeight:600,color:C.textS,marginBottom:8}}>Evidencia fotográfica <span style={{color:C.textM,fontWeight:400}}>(recomendado)</span></div><FotoUploader fotos={fotos} onAdd={f=>setFotos(p=>[...p,f])}/></div>
        <div style={{marginBottom:22}}><div style={{fontSize:12,fontWeight:600,color:C.textS,marginBottom:8}}>Observación <span style={{color:C.textM,fontWeight:400}}>(opcional)</span></div>
          <textarea value={nota} onChange={e=>setNota(e.target.value)} placeholder="Describe el problema..." style={{width:"100%",background:C.surface,border:`1px solid ${C.border}`,borderRadius:8,color:C.textP,padding:"12px",fontSize:13,resize:"vertical",minHeight:70,fontFamily:"system-ui,sans-serif",lineHeight:1.6}}
          onFocus={e=>e.target.style.borderColor=C.blue} onBlur={e=>e.target.style.borderColor=C.border}/>
        </div>
        <button onClick={register} disabled={!can} style={{width:"100%",padding:"15px",borderRadius:10,border:"none",cursor:"pointer",background:can?"linear-gradient(135deg,#1D4ED8,#2563EB)":"#1E293B",color:can?"#FFF":C.textM,fontSize:15,fontWeight:700,transition:"all .2s",boxShadow:can?"0 4px 24px #2563EB33":"none"}}>
          {can?`Registrar bloqueo${fotos.length>0?` · 📷 ${fotos.length} foto${fotos.length>1?"s":""}`:""} →`:"Completa todos los campos"}
        </button>
      </div>)}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// BODEGA
// ═══════════════════════════════════════════════════════════════
function StockBar({mat,height=8}){
  const status=getStockStatus(mat),sc=SCOLOR[status];
  const max=Math.max(mat.stockMinimo*1.3,mat.stockActual*1.1);
  const pctAct=Math.min((mat.stockActual/max)*100,100);
  const pctCrit=(mat.stockCritico/max)*100,pctMin=(mat.stockMinimo/max)*100;
  return(
    <div style={{position:"relative",width:"100%",marginTop:6}}>
      <div style={{height,background:"#1A2540",borderRadius:4,overflow:"visible",position:"relative"}}>
        <div style={{height:"100%",width:`${pctAct}%`,background:sc.color,borderRadius:4,transition:"width .4s",position:"relative",zIndex:2}}/>
        <div style={{position:"absolute",left:`${pctCrit}%`,top:-3,bottom:-3,width:2,background:"#EF4444",zIndex:3,borderRadius:1}}/>
        <div style={{position:"absolute",left:`${pctMin}%`,top:-3,bottom:-3,width:2,background:"#F59E0B",zIndex:3,borderRadius:1}}/>
      </div>
      <div style={{display:"flex",justifyContent:"space-between",marginTop:4}}>
        <span style={{fontFamily:"'JetBrains Mono',monospace",fontSize:10,color:sc.color,fontWeight:600}}>{mat.stockActual} {mat.unidad}</span>
        <span style={{fontSize:9,color:C.textM}}><span style={{color:"#EF4444"}}>●</span> crit {mat.stockCritico} <span style={{color:"#F59E0B"}}>▲</span> mín {mat.stockMinimo}</span>
      </div>
    </div>
  );
}
function BodegaView({materiales,setMateriales}){
  const [selId,setSelId]=useState(null);const [catFilt,setCatFilt]=useState("Todos");
  const cats=["Todos",...new Set(materiales.map(m=>m.cat))];
  const filtered=materiales.filter(m=>catFilt==="Todos"||m.cat===catFilt);
  const sel=materiales.find(m=>m.id===selId);
  const total=materiales.length,rojos=materiales.filter(m=>getStockStatus(m)==="red").length,amarillos=materiales.filter(m=>getStockStatus(m)==="yellow").length,verdes=materiales.filter(m=>getStockStatus(m)==="green").length;
  const ordered=[...filtered].sort((a,b)=>({red:0,yellow:1,green:2}[getStockStatus(a)]-{red:0,yellow:1,green:2}[getStockStatus(b)]));
  const addMov=(id,tipo,cantidad,responsable,obs)=>{setMateriales(prev=>prev.map(m=>{if(m.id!==id)return m;const delta=tipo==="entrada"?+cantidad:-cantidad;return{...m,stockActual:Math.max(0,m.stockActual+delta),movimientos:[{id:Date.now(),tipo,cantidad,responsable,obs,fecha:new Date().toISOString()},...(m.movimientos||[])]};}));};
  const addSol=(id,cantidad,responsable,fechaEstimada)=>{setMateriales(prev=>prev.map(m=>m.id!==id?m:{...m,solicitudes:[...(m.solicitudes||[]),{id:Date.now(),cantidad,responsable,fechaEstimada,fechaSolicitud:new Date().toISOString(),estado:"pendiente"}]}));};
  const resolverSol=(matId,solId)=>{setMateriales(prev=>prev.map(m=>m.id!==matId?m:{...m,solicitudes:m.solicitudes.map(s=>s.id===solId?{...s,estado:"recibido"}:s)}));};
  return(
    <div style={{display:"flex",height:"100%",overflow:"hidden"}}>
      <div style={{flex:1,overflow:"auto",padding:"24px"}}>
        <div style={{marginBottom:20}}><h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Control de Bodega</h1><p style={{fontSize:13,color:C.textM,marginTop:5}}>Stock en tiempo real · Alertas anticipadas · Solicitudes de reposición</p></div>
        <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
          {[{label:"Total materiales",value:total,color:C.textS},{label:"Stock OK",value:verdes,color:"#22C55E"},{label:"Alerta",value:amarillos,color:"#F59E0B"},{label:"Crítico",value:rojos,color:"#EF4444"}].map(k=>(
            <div key={k.label} style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"14px 16px"}}>
              <div style={{fontSize:10,fontWeight:700,color:C.textM,letterSpacing:.5,marginBottom:8}}>{k.label.toUpperCase()}</div>
              <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:28,fontWeight:500,color:k.color,lineHeight:1}}>{k.value}</div>
            </div>
          ))}
        </div>
        <div style={{display:"flex",gap:8,marginBottom:16,flexWrap:"wrap"}}>{cats.map(c=><button key={c} onClick={()=>setCatFilt(c)} style={{background:catFilt===c?C.blueDim:C.surface,border:`1px solid ${catFilt===c?C.blue:C.border}`,color:catFilt===c?"#60A5FA":C.textM,borderRadius:20,padding:"5px 14px",cursor:"pointer",fontSize:12,fontWeight:catFilt===c?700:400,transition:"all .15s"}}>{c}</button>)}</div>
        <div style={{display:"flex",flexDirection:"column",gap:8}}>
          {ordered.map(mat=>{const st=getStockStatus(mat),sc=SCOLOR[st],isSel=selId===mat.id,solPend=(mat.solicitudes||[]).filter(s=>s.estado==="pendiente");return(
            <div key={mat.id} onClick={()=>setSelId(isSel?null:mat.id)} style={{background:C.surface,border:`1.5px solid ${isSel?C.blue:st!=="green"?`${sc.color}33`:C.border}`,borderRadius:10,padding:"14px 16px",cursor:"pointer",transition:"all .15s",boxShadow:isSel?`0 0 0 2px ${C.blue}44`:"none"}}>
              <div style={{display:"flex",alignItems:"flex-start",gap:12}}>
                <div style={{width:10,height:10,borderRadius:"50%",background:sc.color,flexShrink:0,marginTop:4,boxShadow:st!=="green"?`0 0 8px ${sc.color}66`:"none"}}/>
                <div style={{flex:1,minWidth:0}}>
                  <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:4,flexWrap:"wrap"}}>
                    <span style={{fontSize:13,fontWeight:700,color:C.textP}}>{mat.nombre}</span>
                    <span style={{fontSize:10,color:C.textM,background:C.elevated,padding:"2px 7px",borderRadius:4}}>{mat.cat}</span>
                    <span style={{fontSize:10,color:C.textM}}>📍 {mat.ubicacion}</span>
                    {solPend.length>0&&<span style={{fontSize:10,color:"#60A5FA",background:C.blueDim,padding:"2px 7px",borderRadius:4,marginLeft:"auto"}}>📋 {solPend.length} pendiente{solPend.length>1?"s":""}</span>}
                  </div>
                  <StockBar mat={mat}/>
                </div>
                <div style={{background:sc.bg,border:`1px solid ${sc.color}33`,borderRadius:7,padding:"4px 10px",flexShrink:0,textAlign:"center"}}><div style={{fontSize:10,color:sc.color,fontWeight:700}}>{sc.icon} {sc.label}</div></div>
              </div>
            </div>
          );})}
        </div>
      </div>
      {sel&&<div className="sr" style={{width:340,background:C.surface,borderLeft:`1px solid ${C.border}`,overflow:"auto",flexShrink:0}}><MatDetail mat={sel} onClose={()=>setSelId(null)} onMov={addMov} onSol={addSol} onResolver={resolverSol}/></div>}
    </div>
  );
}
function MatDetail({mat,onClose,onMov,onSol,onResolver}){
  const st=getStockStatus(mat),sc=SCOLOR[st];
  const [tab,setTab]=useState("movimiento");const [tipo,setTipo]=useState("entrada");
  const [qty,setQty]=useState("");const [resp,setResp]=useState("");const [obs,setObs]=useState("");
  const [sqty,setSqty]=useState("");const [sresp,setSresp]=useState("");const [sfec,setSfec]=useState("");
  const [ok,setOk]=useState(false);
  const handleMov=()=>{if(!qty||!resp)return;onMov(mat.id,tipo,parseFloat(qty),resp,obs);setQty("");setObs("");setOk(true);setTimeout(()=>setOk(false),1500);};
  const handleSol=()=>{if(!sqty||!sresp||!sfec)return;onSol(mat.id,parseFloat(sqty),sresp,sfec);setSqty("");setSfec("");setOk(true);setTimeout(()=>setOk(false),1500);};
  const solPend=(mat.solicitudes||[]).filter(s=>s.estado==="pendiente"),solRec=(mat.solicitudes||[]).filter(s=>s.estado==="recibido");
  const inp={width:"100%",background:C.elevated,border:`1px solid ${C.border}`,borderRadius:7,color:C.textP,padding:"8px 10px",fontSize:13,fontFamily:"inherit",transition:"border .15s"};
  return(
    <div style={{padding:20}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:16}}>
        <div><div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:4}}>MATERIAL</div><div style={{fontSize:16,fontWeight:800,color:C.textP,lineHeight:1.2}}>{mat.nombre}</div><div style={{fontSize:11,color:C.textM,marginTop:4}}>📍 {mat.ubicacion}</div></div>
        <button onClick={onClose} style={{background:"none",border:"none",color:C.textM,cursor:"pointer",fontSize:22,padding:4,lineHeight:1}}>×</button>
      </div>
      <div style={{background:sc.bg,border:`1px solid ${sc.color}22`,borderRadius:10,padding:"12px 14px",marginBottom:16}}>
        <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:8}}><div style={{width:10,height:10,borderRadius:"50%",background:sc.color,boxShadow:`0 0 8px ${sc.color}66`}}/><span style={{fontSize:13,fontWeight:700,color:sc.color}}>{sc.label}</span></div>
        <StockBar mat={mat} height={10}/>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8,marginTop:12}}>
          {[{l:"Actual",v:mat.stockActual,c:sc.color},{l:"Mínimo",v:mat.stockMinimo,c:"#F59E0B"},{l:"Crítico",v:mat.stockCritico,c:"#EF4444"}].map(x=>(
            <div key={x.l} style={{textAlign:"center",background:C.elevated,borderRadius:7,padding:"8px 4px"}}><div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:16,color:x.c,fontWeight:600}}>{x.v}</div><div style={{fontSize:9,color:C.textM,marginTop:2}}>{x.l} ({mat.unidad})</div></div>
          ))}
        </div>
      </div>
      {solPend.length>0&&<div style={{background:"#0B1E2D",border:"1px solid #38BDF822",borderRadius:10,padding:"12px 14px",marginBottom:16}}>
        <div style={{fontSize:11,fontWeight:700,color:"#38BDF8",marginBottom:10}}>📋 Solicitudes pendientes</div>
        {solPend.map(s=><div key={s.id} style={{background:C.elevated,borderRadius:8,padding:"10px 12px",marginBottom:8}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:4}}><span style={{fontSize:13,fontWeight:700,color:C.textP}}>{s.cantidad} {mat.unidad}</span><span style={{fontSize:10,color:"#F59E0B",background:"#1C1500",padding:"2px 7px",borderRadius:4,fontWeight:600}}>PENDIENTE</span></div>
          <div style={{fontSize:11,color:C.textM,marginBottom:4}}>👤 {s.responsable}</div>
          <div style={{fontSize:11,color:C.textM,marginBottom:8}}>📅 Llegada: <span style={{color:"#60A5FA",fontWeight:600}}>{new Date(s.fechaEstimada).toLocaleDateString("es-CL",{day:"numeric",month:"short",year:"numeric"})}</span></div>
          <button onClick={()=>onResolver(mat.id,s.id)} style={{width:"100%",background:"#052E16",border:"1px solid #22C55E44",color:"#22C55E",borderRadius:6,padding:"6px",cursor:"pointer",fontSize:12,fontWeight:600}}>✓ Marcar como recibido</button>
        </div>)}
      </div>}
      <div style={{display:"flex",background:C.elevated,borderRadius:8,padding:4,marginBottom:16}}>
        {[["movimiento","Registrar movimiento"],["solicitud","Solicitar reposición"]].map(([k,l])=>(
          <button key={k} onClick={()=>setTab(k)} style={{flex:1,padding:"8px",border:"none",borderRadius:6,cursor:"pointer",background:tab===k?C.surface:"transparent",color:tab===k?C.textP:C.textM,fontSize:12,fontWeight:tab===k?700:400,boxShadow:tab===k?"0 1px 4px #00000033":"none",transition:"all .15s"}}>{l}</button>
        ))}
      </div>
      {ok&&<div style={{background:"#052E16",border:"1px solid #22C55E44",borderRadius:8,padding:"10px 14px",marginBottom:14,textAlign:"center",color:"#22C55E",fontWeight:700,fontSize:13}}>✓ Registrado correctamente</div>}
      {tab==="movimiento"&&<div>
        <div style={{display:"flex",gap:8,marginBottom:14}}>{[["entrada","📥 Entrada","#22C55E"],["salida","📤 Salida","#EF4444"]].map(([k,l,c])=>(
          <button key={k} onClick={()=>setTipo(k)} style={{flex:1,background:tipo===k?`${c}15`:C.elevated,border:`1.5px solid ${tipo===k?c:C.border}`,color:tipo===k?c:C.textM,borderRadius:8,padding:"10px",cursor:"pointer",fontSize:13,fontWeight:tipo===k?700:400,transition:"all .15s"}}>{l}</button>
        ))}</div>
        <div style={{marginBottom:12}}><div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>CANTIDAD ({mat.unidad})</div><input type="number" value={qty} onChange={e=>setQty(e.target.value)} placeholder="0" style={inp} onFocus={e=>e.target.style.borderColor=C.blue} onBlur={e=>e.target.style.borderColor=C.border}/></div>
        <div style={{marginBottom:12}}><div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>RESPONSABLE</div><input value={resp} onChange={e=>setResp(e.target.value)} placeholder="Nombre" style={inp} onFocus={e=>e.target.style.borderColor=C.blue} onBlur={e=>e.target.style.borderColor=C.border}/></div>
        <div style={{marginBottom:16}}><div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>OBSERVACIÓN</div><input value={obs} onChange={e=>setObs(e.target.value)} placeholder="Ej: usado en depto 31-32" style={inp} onFocus={e=>e.target.style.borderColor=C.blue} onBlur={e=>e.target.style.borderColor=C.border}/></div>
        <button onClick={handleMov} disabled={!qty||!resp} style={{width:"100%",padding:"13px",borderRadius:9,border:"none",cursor:"pointer",background:qty&&resp?"linear-gradient(135deg,#1D4ED8,#2563EB)":"#1E293B",color:qty&&resp?"#FFF":C.textM,fontSize:14,fontWeight:700,transition:"all .2s",boxShadow:qty&&resp?"0 4px 20px #2563EB33":"none"}}>{tipo==="entrada"?"📥 Registrar entrada":"📤 Registrar salida"}</button>
      </div>}
      {tab==="solicitud"&&<div>
        <div style={{background:"#1C1500",border:"1px solid #F59E0B22",borderRadius:8,padding:"10px 12px",marginBottom:16}}><div style={{fontSize:11,color:"#F59E0B"}}>⚠ Stock actual: <strong>{mat.stockActual} {mat.unidad}</strong>{" — "}{st==="red"?"CRÍTICO — solicitar urgente":"Alerta — solicitar pronto"}</div></div>
        <div style={{marginBottom:12}}><div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>CANTIDAD A SOLICITAR ({mat.unidad})</div><input type="number" value={sqty} onChange={e=>setSqty(e.target.value)} placeholder="0" style={inp} onFocus={e=>e.target.style.borderColor=C.blue} onBlur={e=>e.target.style.borderColor=C.border}/></div>
        <div style={{marginBottom:12}}><div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>RESPONSABLE DE GESTIÓN</div><input value={sresp} onChange={e=>setSresp(e.target.value)} placeholder="Quién hace el pedido" style={inp} onFocus={e=>e.target.style.borderColor=C.blue} onBlur={e=>e.target.style.borderColor=C.border}/></div>
        <div style={{marginBottom:16}}><div style={{fontSize:10,color:C.textM,marginBottom:6,fontWeight:700,letterSpacing:.5}}>FECHA ESTIMADA DE LLEGADA</div><input type="date" value={sfec} onChange={e=>setSfec(e.target.value)} style={inp} min={new Date().toISOString().split("T")[0]}/></div>
        <button onClick={handleSol} disabled={!sqty||!sresp||!sfec} style={{width:"100%",padding:"13px",borderRadius:9,border:"none",cursor:"pointer",background:sqty&&sresp&&sfec?"linear-gradient(135deg,#B45309,#D97706)":"#1E293B",color:sqty&&sresp&&sfec?"#FFF":C.textM,fontSize:14,fontWeight:700,transition:"all .2s",boxShadow:sqty&&sresp&&sfec?"0 4px 20px #D9770633":"none"}}>📋 Crear solicitud de reposición</button>
        {solRec.length>0&&<div style={{marginTop:20,paddingTop:16,borderTop:`1px solid ${C.border}`}}>
          <div style={{fontSize:9,color:C.textM,letterSpacing:2,marginBottom:10}}>HISTORIAL RECIBIDOS</div>
          {solRec.map(s=><div key={s.id} style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"8px 10px",background:C.elevated,borderRadius:7,marginBottom:6}}><span style={{fontSize:12,color:C.textS}}>{s.cantidad} {mat.unidad}</span><span style={{fontSize:10,color:"#22C55E",background:"#052E16",padding:"2px 7px",borderRadius:4,fontWeight:600}}>✓ Recibido</span></div>)}
        </div>}
      </div>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// INFORME IA
// ═══════════════════════════════════════════════════════════════
function InformeIA({blocks,materiales}){
  const [loading,setLoading]=useState(false);const [informe,setInforme]=useState(null);const [error,setError]=useState(null);const [copiado,setCopiado]=useState(false);
  const all=Object.values(blocks).flat();const crit=all.filter(b=>b.problema==="Seguridad"||diasAgo(b.ts)>=2);const matCrit=materiales.filter(m=>m.stockActual<m.stockCritico);
  const solPend=materiales.flatMap(m=>(m.solicitudes||[]).filter(s=>s.estado==="pendiente").map(s=>({...s,material:m.nombre,unidad:m.unidad})));
  const fecha=new Date().toLocaleDateString("es-CL",{weekday:"long",day:"numeric",month:"long",year:"numeric"});
  const prompt=`FECHA: ${fecha}\nPROYECTO: Residencial Las Torres\nBLOQUEOS ACTIVOS: ${all.length} (críticos: ${crit.length})\n\nDETALLE CRÍTICOS:\n${crit.map(b=>{let uid="?";Object.entries(blocks).forEach(([u,bs])=>{if(bs.some(x=>x.id===b.id))uid=u;});return`• Unidad ${uid}: ${b.problema} | ${b.supervisor} | ${diasAgo(b.ts)===0?"Hoy":`${diasAgo(b.ts)}d abierto`} | ${b.detalle}`;}).join("\n")||"Sin críticos."}\n\nBLOQUEOS NORMALES:\n${all.filter(b=>b.problema!=="Seguridad"&&diasAgo(b.ts)<2).map(b=>{let uid="?";Object.entries(blocks).forEach(([u,bs])=>{if(bs.some(x=>x.id===b.id))uid=u;});return`• Unidad ${uid}: ${b.problema} | ${b.supervisor}`;}).join("\n")||"Sin bloqueos normales."}\n\nMATERIALES CRÍTICOS:\n${matCrit.map(m=>`• ${m.nombre}: ${m.stockActual}/${m.stockCritico} ${m.unidad}`).join("\n")||"Sin críticos."}\n\nSOLICITUDES PENDIENTES:\n${solPend.map(s=>`• ${s.material}: ${s.cantidad} ${s.unidad} — llegada ${new Date(s.fechaEstimada).toLocaleDateString("es-CL")}`).join("\n")||"Sin solicitudes."}`;
  const generar=async()=>{
    setLoading(true);setError(null);setInforme(null);
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:1000,system:`Eres un asistente especializado en gestión de obras de construcción en Chile. Genera informes diarios de obra claros y accionables.\n\nEstructura EXACTA:\n📊 INFORME DIARIO DE OBRA\n[Proyecto] · [Fecha]\n\nRESUMEN EJECUTIVO\n[3-4 líneas para el gerente. Estado general, problemas urgentes.]\n\n🔴 CRÍTICOS — ACCIÓN INMEDIATA\n[Bloqueos críticos con unidad, problema y días. Si no hay: "Sin situaciones críticas."]\n\n🟡 EN SEGUIMIENTO\n[Bloqueos normales. Si no hay, omitir.]\n\n📦 BODEGA\n[Materiales críticos y alertas. Si ok: "Bodega sin alertas."]\n\n✅ RECOMENDACIONES\n[2-3 acciones concretas para mañana]\n\nMáximo 350 palabras. Lenguaje directo y profesional. Listo para WhatsApp.`,messages:[{role:"user",content:prompt}]})});
      const data=await res.json();const texto=data?.content?.[0]?.text;if(!texto)throw new Error();setInforme(texto);
    }catch{setError("Error al generar el informe. Verifica tu conexión e intenta nuevamente.");}
    finally{setLoading(false);}
  };
  const copiar=()=>{if(!informe)return;navigator.clipboard.writeText(informe);setCopiado(true);setTimeout(()=>setCopiado(false),2000);};
  return(
    <div style={{maxWidth:760,margin:"0 auto",padding:"24px"}}>
      <div style={{marginBottom:24}}><h1 style={{fontSize:21,fontWeight:800,color:C.textP,lineHeight:1}}>Informe Diario con IA</h1><p style={{fontSize:13,color:C.textM,marginTop:5}}>Generado automáticamente · Listo para enviar al gerente por WhatsApp</p></div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:24}}>
        {[{label:"Bloqueos activos",value:all.length,color:all.length>0?"#F59E0B":"#22C55E",icon:"⚠"},{label:"Críticos",value:crit.length,color:crit.length>0?"#EF4444":"#22C55E",icon:"🔴"},{label:"Materiales críticos",value:matCrit.length,color:matCrit.length>0?"#EF4444":"#22C55E",icon:"📦"}].map(k=>(
          <div key={k.label} style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:10,padding:"14px 16px"}}>
            <div style={{fontSize:10,fontWeight:700,color:C.textM,letterSpacing:.5,marginBottom:8}}>{k.label.toUpperCase()}</div>
            <div style={{fontFamily:"'JetBrains Mono',monospace",fontSize:26,fontWeight:500,color:k.color,lineHeight:1,marginBottom:4}}>{k.value}</div>
            <div style={{fontSize:11,color:C.textM}}>al {new Date().toLocaleTimeString("es-CL",{hour:"2-digit",minute:"2-digit"})}</div>
          </div>
        ))}
      </div>
      <button onClick={generar} disabled={loading} style={{width:"100%",padding:"16px",borderRadius:12,border:"none",cursor:loading?"not-allowed":"pointer",background:loading?"#1E293B":"linear-gradient(135deg,#1D4ED8,#7C3AED)",color:"#FFF",fontSize:15,fontWeight:700,marginBottom:20,display:"flex",alignItems:"center",justifyContent:"center",gap:10,boxShadow:loading?"none":"0 4px 24px #2563EB33",transition:"all .2s"}}>
        {loading?<><div style={{width:18,height:18,border:"2px solid #ffffff44",borderTop:"2px solid #FFF",borderRadius:"50%",animation:"spin 1s linear infinite"}}/>Generando informe...</>:<>✦ Generar informe del día</>}
      </button>
      {error&&<div style={{background:"#1C0404",border:"1px solid #EF444444",borderRadius:10,padding:"14px 16px",marginBottom:16,color:"#EF4444",fontSize:13}}>{error}</div>}
      {informe&&<div className="fu">
        <div style={{display:"flex",gap:8,marginBottom:14,flexWrap:"wrap"}}>
          <button onClick={copiar} style={{background:copiado?"#052E16":"#0F2347",border:`1px solid ${copiado?"#22C55E":"#3B82F6"}`,color:copiado?"#22C55E":"#60A5FA",borderRadius:8,padding:"8px 18px",cursor:"pointer",fontSize:12,fontWeight:700,display:"flex",alignItems:"center",gap:6,transition:"all .2s"}}>{copiado?"✓ Copiado":"📋 Copiar informe"}</button>
          <button onClick={generar} style={{background:C.elevated,border:`1px solid ${C.border}`,color:C.textM,borderRadius:8,padding:"8px 18px",cursor:"pointer",fontSize:12,fontWeight:600}}>↻ Regenerar</button>
        </div>
        <div style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"22px 24px"}}><p style={{fontFamily:"'Plus Jakarta Sans',sans-serif",fontSize:13,color:C.textS,lineHeight:1.8,margin:0,whiteSpace:"pre-wrap"}}>{informe}</p></div>
        <div style={{marginTop:14,background:"#0B1E0F",border:"1px solid #22C55E22",borderRadius:10,padding:"12px 16px",display:"flex",alignItems:"center",gap:10}}><span style={{fontSize:18}}>💬</span><div><div style={{fontSize:12,fontWeight:700,color:"#22C55E",marginBottom:2}}>Listo para enviar</div><div style={{fontSize:11,color:C.textM}}>Copia y pega en WhatsApp al gerente o administrador de contrato.</div></div></div>
      </div>}
      {!informe&&!loading&&!error&&<div style={{background:C.surface,border:`1px dashed ${C.border}`,borderRadius:12,padding:"48px 24px",textAlign:"center"}}><div style={{fontSize:40,marginBottom:14}}>✦</div><div style={{fontSize:15,fontWeight:700,color:C.textS,marginBottom:8}}>El informe se genera en segundos</div><div style={{fontSize:13,color:C.textM,maxWidth:380,margin:"0 auto",lineHeight:1.6}}>La IA lee todos los bloqueos, materiales críticos y estado del proyecto y redacta un informe profesional listo para enviar.</div></div>}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// CHAT OBRA
// ═══════════════════════════════════════════════════════════════
const SUGERIDAS=["¿Qué debo resolver hoy primero?","¿Qué departamentos están paralizados?","¿Qué supervisor tiene más bloqueos?","¿Cuál es el estado de la bodega?","¿Qué materiales van a faltar pronto?","Dame un resumen ejecutivo del proyecto","¿Qué acciones concretas recomiendas para esta semana?"];
function ChatObra({context}){
  const [messages,setMessages]=useState([]);const [input,setInput]=useState("");const [loading,setLoading]=useState(false);
  const bottomRef=useRef(null);const inputRef=useRef(null);
  useEffect(()=>{bottomRef.current?.scrollIntoView({behavior:"smooth"});},[messages,loading]);
  const send=async(texto)=>{
    const q=texto||input.trim();if(!q||loading)return;setInput("");
    const userMsg={role:"user",content:q,ts:new Date()};const newHistory=[...messages,userMsg];setMessages(newHistory);setLoading(true);
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:1000,system:`Eres el asistente de obra inteligente de ObraTrack. Conoces en detalle el estado actual del proyecto.\n\nDATOS ACTUALES:\n${context}\n\nInstrucciones: Responde como experto en construcción chileno. Directo y concreto. Usa números reales. Prioriza por impacto. Máximo 150 palabras salvo que pidan resumen completo. Español profesional y cercano.`,messages:newHistory.map(m=>({role:m.role,content:m.content}))})});
      const data=await res.json();const resp=data?.content?.[0]?.text||"Sin respuesta.";setMessages(prev=>[...prev,{role:"assistant",content:resp,ts:new Date()}]);
    }catch{setMessages(prev=>[...prev,{role:"assistant",content:"Error de conexión. Intenta nuevamente.",ts:new Date(),isError:true}]);}
    finally{setLoading(false);inputRef.current?.focus();}
  };
  const handleKey=(e)=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();send();}};
  return(
    <div style={{display:"flex",flexDirection:"column",height:"100%",maxWidth:800,margin:"0 auto",padding:"0 24px"}}>
      <div style={{padding:"20px 0 14px",borderBottom:`1px solid ${C.border}`,flexShrink:0}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <div style={{display:"flex",alignItems:"center",gap:10}}>
            <div style={{width:34,height:34,borderRadius:9,background:"linear-gradient(135deg,#1D4ED8,#7C3AED)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:17}}>✦</div>
            <div><h1 style={{fontSize:17,fontWeight:800,color:C.textP,lineHeight:1}}>Chat con la Obra</h1><p style={{fontSize:11,color:C.textM,marginTop:2}}>Pregunta cualquier cosa sobre el estado del proyecto</p></div>
          </div>
          {messages.length>0&&<button onClick={()=>setMessages([])} style={{background:"none",border:`1px solid ${C.border}`,color:C.textM,borderRadius:7,padding:"5px 12px",cursor:"pointer",fontSize:11}}>Limpiar</button>}
        </div>
      </div>
      <div style={{flex:1,overflow:"auto",paddingTop:16,paddingBottom:8}}>
        {messages.length===0&&<div style={{textAlign:"center",padding:"32px 0 24px"}}>
          <div style={{width:56,height:56,borderRadius:16,background:"linear-gradient(135deg,#1D4ED8,#7C3AED)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:26,margin:"0 auto 14px"}}>✦</div>
          <div style={{fontSize:15,fontWeight:700,color:C.textP,marginBottom:6}}>Hola. Conozco tu obra de memoria.</div>
          <div style={{fontSize:13,color:C.textM,maxWidth:360,margin:"0 auto",lineHeight:1.6}}>Pregúntame lo que necesites — qué está bloqueado, qué materiales van a faltar, qué debes resolver primero.</div>
        </div>}
        {messages.map((msg,i)=>(
          <div key={i} className="fu" style={{marginBottom:14,display:"flex",flexDirection:"column",alignItems:msg.role==="user"?"flex-end":"flex-start"}}>
            {msg.role==="assistant"&&<div style={{display:"flex",alignItems:"center",gap:7,marginBottom:5}}><div style={{width:22,height:22,borderRadius:6,background:"linear-gradient(135deg,#1D4ED8,#7C3AED)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11}}>✦</div><span style={{fontSize:10,color:C.textM,fontWeight:600}}>OBRA IA</span><span style={{fontSize:10,color:C.textM}}>{msg.ts.toLocaleTimeString("es-CL",{hour:"2-digit",minute:"2-digit"})}</span></div>}
            <div style={{maxWidth:"85%",background:msg.role==="user"?"linear-gradient(135deg,#1D4ED8,#2563EB)":msg.isError?"#1C0404":C.elevated,border:msg.role==="user"?"none":msg.isError?"1px solid #EF444433":`1px solid ${C.border}`,borderRadius:msg.role==="user"?"14px 14px 4px 14px":"4px 14px 14px 14px",padding:"12px 16px",boxShadow:msg.role==="user"?"0 4px 16px #2563EB33":"none"}}>
              <p style={{fontFamily:"'Plus Jakarta Sans',sans-serif",fontSize:13,color:msg.role==="user"?"#FFF":C.textS,lineHeight:1.7,margin:0,whiteSpace:"pre-wrap"}}>{msg.content}</p>
            </div>
            {msg.role==="user"&&<div style={{fontSize:10,color:C.textM,marginTop:4}}>{msg.ts.toLocaleTimeString("es-CL",{hour:"2-digit",minute:"2-digit"})}</div>}
          </div>
        ))}
        {loading&&<div className="fu" style={{display:"flex",alignItems:"center",gap:7,marginBottom:14}}>
          <div style={{width:22,height:22,borderRadius:6,background:"linear-gradient(135deg,#1D4ED8,#7C3AED)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11}}>✦</div>
          <div style={{background:C.elevated,border:`1px solid ${C.border}`,borderRadius:"4px 14px 14px 14px",padding:"12px 16px",display:"flex",gap:5,alignItems:"center"}}>
            {[0,1,2].map(i=><div key={i} style={{width:6,height:6,borderRadius:"50%",background:C.blue,animation:`pulse 1.2s ease ${i*0.2}s infinite`}}/>)}
          </div>
        </div>}
        <div ref={bottomRef}/>
      </div>
      {messages.length===0&&<div style={{paddingBottom:12,flexShrink:0}}>
        <div style={{fontSize:10,color:C.textM,fontWeight:600,letterSpacing:.5,marginBottom:8}}>PREGUNTAS FRECUENTES</div>
        <div style={{display:"flex",flexWrap:"wrap",gap:6}}>{SUGERIDAS.map((q,i)=><button key={i} onClick={()=>send(q)} style={{background:C.surface,border:`1px solid ${C.border}`,color:C.textS,borderRadius:20,padding:"6px 14px",cursor:"pointer",fontSize:12,transition:"all .15s",fontFamily:"'Plus Jakarta Sans',sans-serif"}}>{q}</button>)}</div>
      </div>}
      <div style={{paddingBottom:20,paddingTop:10,flexShrink:0,borderTop:`1px solid ${C.border}`}}>
        <div style={{display:"flex",gap:10,alignItems:"flex-end"}}>
          <div style={{flex:1,background:C.surface,border:`1px solid ${C.border}`,borderRadius:12,padding:"4px 4px 4px 14px",display:"flex",alignItems:"flex-end",gap:8,transition:"border .15s"}} onFocusCapture={e=>e.currentTarget.style.borderColor=C.blue} onBlurCapture={e=>e.currentTarget.style.borderColor=C.border}>
            <textarea ref={inputRef} value={input} onChange={e=>setInput(e.target.value)} onKeyDown={handleKey} placeholder="Pregunta algo sobre la obra..." rows={1} style={{flex:1,background:"none",border:"none",color:C.textP,fontSize:13,fontFamily:"'Plus Jakarta Sans',sans-serif",resize:"none",lineHeight:1.5,padding:"10px 0",maxHeight:120,overflowY:"auto"}} onInput={e=>{e.target.style.height="auto";e.target.style.height=Math.min(e.target.scrollHeight,120)+"px";}}/>
            <button onClick={()=>send()} disabled={!input.trim()||loading} style={{width:38,height:38,borderRadius:9,border:"none",cursor:"pointer",background:input.trim()&&!loading?"linear-gradient(135deg,#1D4ED8,#7C3AED)":"#1E293B",color:"#FFF",fontSize:16,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0,transition:"all .2s",marginBottom:3,boxShadow:input.trim()&&!loading?"0 2px 12px #2563EB44":"none"}}>
              {loading?<div style={{width:14,height:14,border:"2px solid #ffffff33",borderTop:"2px solid #FFF",borderRadius:"50%",animation:"spin 1s linear infinite"}}/>:"→"}
            </button>
          </div>
        </div>
        <div style={{fontSize:10,color:C.textM,marginTop:6,textAlign:"center"}}>Enter para enviar · Shift+Enter para nueva línea</div>
      </div>
    </div>
  );
}
