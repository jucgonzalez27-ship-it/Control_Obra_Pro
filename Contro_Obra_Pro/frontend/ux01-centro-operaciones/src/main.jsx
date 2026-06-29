import React from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  ArrowRight,
  Building2,
  CalendarClock,
  CheckCircle2,
  ClipboardList,
  Factory,
  FileText,
  Filter,
  Flag,
  Gauge,
  Hammer,
  Home,
  Map,
  Search,
  ShieldAlert,
  UserRound
} from "lucide-react";
import "./styles.css";

const navItems = [
  { label: "Centro de Operaciones", icon: Home, active: true },
  { label: "Departamentos", icon: Building2 },
  { label: "Restricciones", icon: ShieldAlert },
  { label: "Partidas", icon: ClipboardList },
  { label: "Responsables", icon: UserRound },
  { label: "Reportes", icon: FileText },
  { label: "Configuracion", icon: Gauge }
];

const priorityActions = [
  {
    priority: 1,
    impact: "8 departamentos detenidos",
    cause: "Falta suministro de muebles de cocina",
    action: "Coordinar ingreso del proveedor hoy antes de las 11:00",
    owner: "Bodega / Subcontrato Muebles",
    due: "Hoy 11:00"
  },
  {
    priority: 2,
    impact: "5 departamentos con avance verificable",
    cause: "Mano final de pintura declarada terminada",
    action: "Administrador debe verificar Piso 8 y Piso 9",
    owner: "Administrador",
    due: "Hoy 12:30"
  },
  {
    priority: 3,
    impact: "4 departamentos no pueden iniciar griferia",
    cause: "Cubiertas de cocina sin liberar",
    action: "Validar montaje de cubierta y despejar ingreso sanitario",
    owner: "Supervisor Terminaciones",
    due: "Hoy 14:00"
  },
  {
    priority: 4,
    impact: "3 departamentos con restriccion sanitaria",
    cause: "Partida previa no ejecutada en banos",
    action: "Coordinar cuadrilla sanitaria en Piso 6",
    owner: "Supervisor Instalaciones",
    due: "Hoy 15:00"
  },
  {
    priority: 5,
    impact: "2 departamentos listos para liberacion",
    cause: "Todas las partidas aplicables verificadas",
    action: "Completar liberacion administrativa",
    owner: "Administrador",
    due: "Hoy 16:30"
  }
];

const statuses = {
  operativo: {
    label: "Operativo",
    color: "border-emerald-300 bg-emerald-50 text-emerald-800",
    dot: "bg-emerald-500"
  },
  riesgo: {
    label: "Riesgo",
    color: "border-amber-300 bg-amber-50 text-amber-800",
    dot: "bg-amber-500"
  },
  bloqueado: {
    label: "Bloqueado",
    color: "border-red-300 bg-red-50 text-red-800",
    dot: "bg-red-500"
  },
  sinRevisar: {
    label: "Sin revisar",
    color: "border-slate-300 bg-slate-50 text-slate-600",
    dot: "bg-slate-400"
  }
};

const statusCycle = [
  "operativo",
  "riesgo",
  "bloqueado",
  "sinRevisar",
  "operativo",
  "operativo",
  "riesgo",
  "bloqueado"
];

const floors = Array.from({ length: 12 }, (_, index) => 12 - index).map((floor) => ({
  floor,
  departments: ["01", "02", "03", "04"].map((suffix, index) => {
    const status = statusCycle[(floor + index) % statusCycle.length];
    const restrictions = status === "bloqueado" ? (floor + index) % 3 + 1 : status === "riesgo" ? 1 : 0;
    const progress = Math.min(96, 42 + floor * 4 + index * 5 - restrictions * 9);
    return {
      id: `${floor}${suffix}`,
      status,
      progress,
      restrictions
    };
  })
}));

const kpis = [
  { label: "Departamentos liberables", value: "7", hint: "Listos para cierre", tone: "text-emerald-700" },
  { label: "Departamentos bloqueados", value: "11", hint: "Restriccion activa", tone: "text-red-700" },
  { label: "Departamentos con riesgo", value: "9", hint: "Seguimiento requerido", tone: "text-amber-700" },
  { label: "Avance oficial torre", value: "68%", hint: "Verificado", tone: "text-slate-900" },
  { label: "Restricciones criticas", value: "6", hint: "Impacto alto", tone: "text-red-700" }
];

const criticalRestrictions = [
  {
    impact: "8 deptos",
    problem: "Falta muebles cocina",
    owner: "Bodega",
    due: "Hoy 11:00",
    action: "Coordinar ingreso proveedor"
  },
  {
    impact: "5 deptos",
    problem: "Pintura final pendiente",
    owner: "Subcontrato Pintura",
    due: "Hoy 12:30",
    action: "Cerrar Piso 8"
  },
  {
    impact: "4 deptos",
    problem: "Cubiertas sin montar",
    owner: "Subcontrato Muebles",
    due: "Hoy 14:00",
    action: "Liberar ingreso sanitario"
  },
  {
    impact: "3 deptos",
    problem: "Partida previa no ejecutada",
    owner: "Supervisor Instalaciones",
    due: "Hoy 15:00",
    action: "Enviar cuadrilla sanitaria"
  }
];

const commitments = [
  { time: "09:00", text: "Llegada proveedor muebles", owner: "Bodega" },
  { time: "11:30", text: "Revision Depto 804", owner: "Administrador" },
  { time: "15:00", text: "Ingreso pintura Piso 8", owner: "Subcontrato Pintura" },
  { time: "16:30", text: "Liberacion administrativa", owner: "Administrador" }
];

function App() {
  return (
    <main className="min-h-screen bg-site-50 text-slate-900">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 shrink-0 bg-ink-950 px-5 py-6 text-white lg:block">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded bg-white/10">
              <Factory className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-slate-300">Control Obra Pro</p>
              <h1 className="text-lg font-semibold">Torre A</h1>
            </div>
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => (
              <button
                key={item.label}
                className={`flex h-11 w-full items-center gap-3 rounded px-3 text-left text-sm transition ${
                  item.active
                    ? "bg-white text-ink-950 shadow-soft"
                    : "text-slate-300 hover:bg-white/10 hover:text-white"
                }`}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </button>
            ))}
          </nav>
          <div className="mt-8 rounded border border-white/10 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-400">Usuario activo</p>
            <p className="mt-2 text-sm font-semibold">Administrador Obra</p>
            <p className="text-xs text-slate-400">Domingo 28 Jun</p>
          </div>
        </aside>

        <section className="flex min-w-0 flex-1 flex-col">
          <Header />
          <div className="space-y-6 px-5 py-6 lg:px-8">
            <PriorityActions />
            <DepartmentMap />
            <KpiStrip />
            <div className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
              <CriticalRestrictions />
              <Commitments />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function Header() {
  return (
    <header className="border-b border-site-200 bg-white px-5 py-4 lg:px-8">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Centro de Operaciones</p>
          <h2 className="text-2xl font-semibold tracking-tight text-slate-950">
            Que debo hacer ahora para liberar mas departamentos hoy
          </h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <FilterSelect label="Torre" value="Torre A" />
          <FilterSelect label="Piso" value="Todos" />
          <FilterSelect label="Estado" value="Todos" />
          <FilterSelect label="Responsable" value="Todos" />
          <label className="flex h-11 items-center gap-2 rounded border border-site-200 bg-site-50 px-3 text-sm text-slate-600">
            <Search className="h-4 w-4" />
            <input
              className="w-full bg-transparent outline-none placeholder:text-slate-400"
              placeholder="Buscar depto"
            />
          </label>
        </div>
      </div>
    </header>
  );
}

function FilterSelect({ label, value }) {
  return (
    <label className="flex h-11 items-center gap-2 rounded border border-site-200 bg-site-50 px-3 text-sm">
      <Filter className="h-4 w-4 text-slate-400" />
      <span className="text-slate-500">{label}</span>
      <select defaultValue={value} className="min-w-0 bg-transparent font-medium text-slate-800 outline-none">
        <option>{value}</option>
      </select>
    </label>
  );
}

function PriorityActions() {
  return (
    <section>
      <SectionHeader
        icon={Flag}
        title="Acciones prioritarias"
        subtitle="Que hago primero para generar avance hoy"
      />
      <div className="mt-3 grid gap-4 xl:grid-cols-5">
        {priorityActions.map((action) => (
          <article key={action.priority} className="rounded border border-site-200 bg-white p-4 shadow-soft">
            <div className="flex items-start justify-between gap-3">
              <span className="rounded bg-ink-950 px-2 py-1 text-xs font-semibold text-white">
                Prioridad {action.priority}
              </span>
              <span className="text-xs font-medium text-slate-500">{action.due}</span>
            </div>
            <h3 className="mt-3 text-base font-semibold text-slate-950">{action.impact}</h3>
            <p className="mt-2 text-sm text-slate-600">Causa: {action.cause}</p>
            <p className="mt-2 text-sm font-medium text-slate-900">Accion: {action.action}</p>
            <div className="mt-4 flex items-center justify-between gap-3 border-t border-site-100 pt-3 text-xs text-slate-500">
              <span>{action.owner}</span>
              <ArrowRight className="h-4 w-4" />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function DepartmentMap() {
  return (
    <section className="rounded border border-site-200 bg-white p-5 shadow-soft">
      <SectionHeader
        icon={Map}
        title="Mapa operativo de departamentos"
        subtitle="Donde debo actuar"
      />
      <div className="mt-5 space-y-3">
        {floors.map((floor) => (
          <div key={floor.floor} className="grid grid-cols-[72px_1fr] items-center gap-3">
            <div className="text-sm font-semibold text-slate-500">Piso {floor.floor}</div>
            <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
              {floor.departments.map((department) => (
                <DepartmentCard key={department.id} department={department} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function DepartmentCard({ department }) {
  const status = statuses[department.status];
  return (
    <button className={`h-24 rounded border p-3 text-left transition hover:-translate-y-0.5 hover:shadow-soft ${status.color}`}>
      <div className="flex items-start justify-between">
        <span className="text-lg font-bold tracking-tight">{department.id}</span>
        <span className={`mt-1 h-2.5 w-2.5 rounded-full ${status.dot}`} />
      </div>
      <div className="mt-3 flex items-end justify-between">
        <div>
          <p className="text-xs font-medium opacity-80">{status.label}</p>
          <p className="text-xl font-semibold">{department.progress}%</p>
        </div>
        <span className="rounded bg-white/70 px-2 py-1 text-xs font-semibold">
          R: {department.restrictions}
        </span>
      </div>
    </button>
  );
}

function KpiStrip() {
  return (
    <section>
      <SectionHeader icon={Gauge} title="KPIs secundarios" subtitle="Como va la torre" />
      <div className="mt-3 grid gap-4 md:grid-cols-5">
        {kpis.map((kpi) => (
          <article key={kpi.label} className="rounded border border-site-200 bg-white p-4 shadow-soft">
            <p className="text-sm text-slate-500">{kpi.label}</p>
            <p className={`mt-2 text-3xl font-semibold ${kpi.tone}`}>{kpi.value}</p>
            <p className="mt-1 text-xs text-slate-500">{kpi.hint}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function CriticalRestrictions() {
  return (
    <section className="rounded border border-site-200 bg-white p-5 shadow-soft">
      <SectionHeader
        icon={AlertTriangle}
        title="Restricciones criticas"
        subtitle="Que esta deteniendo la obra"
      />
      <div className="mt-4 overflow-hidden rounded border border-site-200">
        <table className="w-full text-left text-sm">
          <thead className="bg-site-100 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Impacto</th>
              <th className="px-4 py-3">Problema</th>
              <th className="px-4 py-3">Responsable</th>
              <th className="px-4 py-3">Fecha</th>
              <th className="px-4 py-3">Accion</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-site-100">
            {criticalRestrictions.map((item) => (
              <tr key={`${item.impact}-${item.problem}`} className="bg-white">
                <td className="px-4 py-3 font-semibold text-red-700">{item.impact}</td>
                <td className="px-4 py-3 text-slate-800">{item.problem}</td>
                <td className="px-4 py-3 text-slate-600">{item.owner}</td>
                <td className="px-4 py-3 text-slate-600">{item.due}</td>
                <td className="px-4 py-3 font-medium text-slate-900">{item.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Commitments() {
  return (
    <section className="rounded border border-site-200 bg-white p-5 shadow-soft">
      <SectionHeader
        icon={CalendarClock}
        title="Compromisos proximos"
        subtitle="Que no puedo olvidar hoy"
      />
      <div className="mt-5 space-y-4">
        {commitments.map((commitment) => (
          <div key={`${commitment.time}-${commitment.text}`} className="grid grid-cols-[64px_1fr] gap-4">
            <div className="text-sm font-semibold text-slate-950">{commitment.time}</div>
            <div className="border-l border-site-200 pl-4">
              <p className="text-sm font-medium text-slate-900">{commitment.text}</p>
              <p className="text-xs text-slate-500">{commitment.owner}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded bg-site-100 text-slate-700">
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
          <p className="text-sm text-slate-500">{subtitle}</p>
        </div>
      </div>
      <CheckCircle2 className="hidden h-5 w-5 text-emerald-600 sm:block" />
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
