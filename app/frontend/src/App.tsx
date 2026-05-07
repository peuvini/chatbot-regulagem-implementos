import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Bot, Database, Gauge, LayoutDashboard } from "lucide-react";
import { Chatbot } from "./components/Chatbot";
import { Dashboard } from "./components/Dashboard";
import { DatabaseSearch } from "./components/DatabaseSearch";
import { RecommendationForm } from "./components/RecommendationForm";
import { api } from "./services/api";

type View = "dashboard" | "recommendation" | "chat" | "database";

export function App() {
  const [view, setView] = useState<View>("dashboard");
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof api.stats>> | null>(null);
  const [status, setStatus] = useState("Conectando...");

  useEffect(() => {
    Promise.all([api.health(), api.stats()])
      .then(([health, stats]) => {
        setStatus(`${health.status.toUpperCase()} · ${stats.model.training_rows} linhas de treino`);
        setDashboard(stats);
      })
      .catch((error: Error) => setStatus(`Erro: ${error.message}`));
  }, []);

  return (
    <div className="grid min-h-screen lg:grid-cols-[280px_1fr]">
      <aside className="flex flex-col gap-8 bg-soil-950 p-6 text-white lg:sticky lg:top-0 lg:h-screen">
        <div>
          <p className="mb-2 text-xs font-bold uppercase text-green-200">Pesquisa aplicada</p>
          <h1 className="text-2xl font-bold leading-tight">Regulagem de Implementos</h1>
        </div>
        <nav className="grid gap-2">
          <NavButton active={view === "dashboard"} icon={<LayoutDashboard size={18} />} onClick={() => setView("dashboard")}>Painel</NavButton>
          <NavButton active={view === "recommendation"} icon={<Gauge size={18} />} onClick={() => setView("recommendation")}>Recomendação</NavButton>
          <NavButton active={view === "chat"} icon={<Bot size={18} />} onClick={() => setView("chat")}>Chatbot</NavButton>
          <NavButton active={view === "database"} icon={<Database size={18} />} onClick={() => setView("database")}>Banco</NavButton>
        </nav>
        <div className="mt-auto text-sm leading-6 text-green-100">{status}</div>
      </aside>
      <main className="p-5 lg:p-8">
        {view === "dashboard" && <Dashboard data={dashboard} />}
        {view === "recommendation" && <RecommendationForm />}
        {view === "chat" && <Chatbot />}
        {view === "database" && <DatabaseSearch />}
      </main>
    </div>
  );
}

function NavButton({ active, icon, children, onClick }: { active: boolean; icon: ReactNode; children: ReactNode; onClick: () => void }) {
  return (
    <button
      className={`flex items-center gap-3 rounded-md px-3 py-3 text-left font-bold transition ${active ? "bg-white/15" : "hover:bg-white/10"}`}
      onClick={onClick}
    >
      {icon}
      {children}
    </button>
  );
}
