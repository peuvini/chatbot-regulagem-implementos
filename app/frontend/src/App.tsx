import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Bot, Calculator, Database, Gauge, LayoutDashboard, LogOut, Menu, UserRound, X } from "lucide-react";
import tractorDriver from "./assets/cartoon-tractor-driver-no-soil-transparent-v4.png";
import farmerHoe from "./assets/cartoon-farmer-hoe-v1.png";
import { AuthPage } from "./components/AuthPage";
import { Chatbot } from "./components/Chatbot";
import { Dashboard } from "./components/Dashboard";
import { DatabaseSearch } from "./components/DatabaseSearch";
import { OperationPlanning } from "./components/OperationPlanning";
import { RecommendationForm } from "./components/RecommendationForm";
import { api } from "./services/api";
import type { AuthResponse, User } from "./types/api";

type View = "dashboard" | "recommendation" | "planning" | "chat" | "database";

const tokenStorageKey = "regulagem_implementos_token";

export function App() {
  const [view, setView] = useState<View>("recommendation");
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof api.stats>> | null>(null);
  const [status, setStatus] = useState("Conectando...");
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.remove("dark");
    document.documentElement.setAttribute("data-theme", "arips");
  }, []);

  useEffect(() => {
    api.health().then((health) => setStatus(health.status.toUpperCase())).catch((error: Error) => setStatus(`Erro: ${error.message}`));
  }, []);

  useEffect(() => {
    const token = localStorage.getItem(tokenStorageKey);
    if (!token) {
      setAuthLoading(false);
      return;
    }
    api.me(token).then(setUser).catch(() => localStorage.removeItem(tokenStorageKey)).finally(() => setAuthLoading(false));
  }, []);

  useEffect(() => {
    if (!user) return;
    if (user.role !== "admin" && (view === "dashboard" || view === "database")) setView("recommendation");
    if (user.role === "admin") {
      api.stats().then((stats) => {
        setStatus("OK");
        setDashboard(stats);
      }).catch((error: Error) => setStatus(`Erro: ${error.message}`));
    }
  }, [user, view]);

  function authenticate(auth: AuthResponse) {
    localStorage.setItem(tokenStorageKey, auth.access_token);
    setUser(auth.user);
  }

  function logout() {
    localStorage.removeItem(tokenStorageKey);
    setUser(null);
  }

  function selectView(nextView: View) {
    setView(nextView);
    setMenuOpen(false);
  }

  if (authLoading) return <div className="grid min-h-screen place-items-center bg-[#b9bd45] text-sm font-semibold text-[#34391c]">Carregando acesso...</div>;
  if (!user) return <AuthPage onAuthenticated={authenticate} />;

  return (
    <div className="arips-app grid h-[100dvh] grid-rows-[auto_minmax(0,1fr)_58px] overflow-hidden bg-[#9ea83f] text-base-content lg:grid-rows-[auto_minmax(0,1fr)_112px] xl:grid-rows-[auto_minmax(0,1fr)_132px]">
      <header className="relative z-40 mx-auto w-full max-w-[1680px] px-2 sm:px-4">
        <div className="arips-navbar flex min-h-24 items-center rounded-b-[34px] bg-[#6d513c] px-5 text-[#fffaf1] shadow-lg lg:px-8">
          <div className="flex w-auto items-center lg:w-1/5">
            <button className="mr-2 flex h-11 w-11 items-center justify-center rounded-full bg-white/10 lg:hidden" aria-label={menuOpen ? "Fechar menu" : "Abrir menu"} onClick={() => setMenuOpen((open) => !open)} type="button">
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
            <button className="text-left" onClick={() => selectView("recommendation")} type="button">
              <span className="block text-2xl font-black tracking-normal">ARIPS</span>
              <span className="hidden text-[10px] font-semibold text-white/70 xl:block">Regulagem de preparo do solo</span>
            </button>
          </div>

          <nav className="hidden flex-1 items-center justify-center lg:flex">
            <div className="flex items-center gap-1">
              {user.role === "admin" && <TopNav active={view === "dashboard"} icon={<LayoutDashboard size={17} />} onClick={() => selectView("dashboard")}>Painel técnico</TopNav>}
              <TopNav active={view === "recommendation"} icon={<Gauge size={17} />} onClick={() => selectView("recommendation")}>Recomendação</TopNav>
              <TopNav active={view === "planning"} icon={<Calculator size={17} />} onClick={() => selectView("planning")}>Planejamento</TopNav>
              <TopNav active={view === "chat"} icon={<Bot size={17} />} onClick={() => selectView("chat")}>Assistente técnico</TopNav>
              {user.role === "admin" && <TopNav active={view === "database"} icon={<Database size={17} />} onClick={() => selectView("database")}>Banco técnico</TopNav>}
            </div>
          </nav>

          <div className="ml-auto flex w-auto items-center justify-end gap-1 lg:w-1/5">
            <div className="hidden min-w-0 items-center gap-2 rounded-full bg-white/10 px-3 py-2 md:flex">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#d4aa55] text-[#2f2a1c]"><UserRound size={16} /></span>
              <span className="max-w-24 truncate text-sm font-semibold">{user.name}</span>
              <span className={`status-dot ${status === "OK" ? "online" : ""}`} title={status} />
            </div>
            <button className="btn btn-ghost btn-circle text-white hover:bg-white/10" aria-label="Sair" onClick={logout} title="Sair" type="button"><LogOut size={18} /></button>
          </div>
        </div>

        {menuOpen && (
          <nav className="menu mt-2 rounded-2xl bg-[#6d513c] p-3 text-[#fffaf1] shadow-xl lg:hidden">
            {user.role === "admin" && <TopNav active={view === "dashboard"} icon={<LayoutDashboard size={17} />} onClick={() => selectView("dashboard")}>Painel técnico</TopNav>}
            <TopNav active={view === "recommendation"} icon={<Gauge size={17} />} onClick={() => selectView("recommendation")}>Recomendação</TopNav>
            <TopNav active={view === "planning"} icon={<Calculator size={17} />} onClick={() => selectView("planning")}>Planejamento</TopNav>
            <TopNav active={view === "chat"} icon={<Bot size={17} />} onClick={() => selectView("chat")}>Assistente técnico</TopNav>
            {user.role === "admin" && <TopNav active={view === "database"} icon={<Database size={17} />} onClick={() => selectView("database")}>Banco técnico</TopNav>}
          </nav>
        )}
      </header>

      <main className="relative z-10 min-h-0 w-full overflow-hidden px-4 py-4 md:px-6 md:py-5">
        <div className="workspace-surface mx-auto h-full max-w-[1440px] overflow-hidden rounded-[24px] bg-[#f3efe4] p-2 shadow-xl" key={view}>
          <div className="workspace-scroll h-full overflow-y-auto rounded-[18px] p-2 md:p-4 lg:p-6">
            {view === "dashboard" && <Dashboard data={dashboard} />}
            {view === "recommendation" && <RecommendationForm />}
            {view === "planning" && <OperationPlanning />}
            {view === "chat" && <Chatbot />}
            {view === "database" && <DatabaseSearch trainingRows={dashboard?.model.training_rows} />}
          </div>
        </div>
      </main>

      <footer className="relative z-20 min-h-0 overflow-visible" aria-hidden="true">
        <div className="soil-cross-section pointer-events-none absolute inset-0 z-10" />
        <img className="pointer-events-none absolute bottom-4 left-2 z-20 hidden w-32 lg:block xl:w-40" src={tractorDriver} alt="" />
        <img className="pointer-events-none absolute bottom-1 right-2 z-20 hidden h-28 lg:block xl:h-32" src={farmerHoe} alt="" />
      </footer>
    </div>
  );
}

function TopNav({ active, icon, children, onClick }: { active: boolean; icon: ReactNode; children: ReactNode; onClick: () => void }) {
  return <button className={`flex min-h-11 items-center gap-2 whitespace-nowrap rounded-full px-3 text-sm font-semibold transition xl:px-4 ${active ? "bg-[#e0ad4f] text-[#332416]" : "text-[#fffaf1] hover:bg-white/10"}`} onClick={onClick} type="button">{icon}{children}</button>;
}
