import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { ArrowRight, Eye, EyeOff, KeyRound, Mail } from "lucide-react";
import sandPathBackground from "../assets/auth-sand-path-background-v1.png";
import farmerTractor from "../assets/farmer-tractor-original-no-ground-v4.png";
import { api } from "../services/api";
import type { AuthResponse } from "../types/api";

type Props = {
  onAuthenticated: (auth: AuthResponse) => void;
};

export function AuthPage({ onAuthenticated }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const auth = mode === "register"
        ? await api.register({
            name: String(form.get("name") || ""),
            email: String(form.get("email") || ""),
            cpf: String(form.get("cpf") || ""),
            password: String(form.get("password") || ""),
          })
        : await api.login({
            email: String(form.get("email") || ""),
            password: String(form.get("password") || ""),
          });
      onAuthenticated(auth);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível autenticar");
    } finally {
      setLoading(false);
    }
  }

  function changeMode(nextMode: "login" | "register") {
    setMode(nextMode);
    setError("");
  }

  return (
    <main className="arips-auth relative min-h-screen overflow-hidden bg-[#b9bd45] text-[#202318]">
      <img className="auth-path-background pointer-events-none absolute inset-0 z-0" src={sandPathBackground} alt="" aria-hidden="true" />
      <span className="auth-tractor-shadow pointer-events-none absolute z-[9]" aria-hidden="true" />
      <img className="auth-farmer-tractor pointer-events-none absolute bottom-0 left-0 z-10" src={farmerTractor} alt="" aria-hidden="true" />
      <div className="auth-layout mx-auto grid min-h-screen max-w-[1500px] items-start gap-8 px-5 md:px-9 lg:grid-cols-[minmax(0,1fr)_minmax(460px,560px)] lg:gap-16">
        <section className="relative z-10 text-center lg:text-left">
          <h1 className="text-5xl font-black tracking-normal md:text-6xl">ARIPS</h1>
          <p className="mx-auto mt-4 max-w-xl text-xl font-semibold leading-8 lg:mx-0 lg:text-2xl">
            Auxiliando de forma inteligente a regulagem de preparo do solo
          </p>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-[#30351d]/80 lg:mx-0 lg:text-lg">
            Selecione implementos, confira a potência necessária e planeje operações de preparo do solo com uma base técnica organizada.
          </p>
        </section>

        <section className="auth-glass relative z-20 w-full">
          <div className="grid grid-cols-2 border-b border-white/35">
            <ModeButton active={mode === "login"} onClick={() => changeMode("login")}>Entrar</ModeButton>
            <ModeButton active={mode === "register"} onClick={() => changeMode("register")}>Registrar</ModeButton>
          </div>

          <div className="p-6 md:p-9">
            <div className="mb-7">
              <h2 className="text-3xl font-black text-[#1f2318]">{mode === "login" ? "Acesse sua conta" : "Registre sua conta"}</h2>
              <p className="mt-2 text-sm leading-6 text-[#2e3420]/75">
                {mode === "login" ? "Faça login para acessar suas consultas e planejamentos." : "Cadastre-se para utilizar as ferramentas técnicas."}
              </p>
            </div>

            <form className="grid gap-4" onSubmit={submit}>
              {mode === "register" && (
                <div className="grid gap-4 sm:grid-cols-2">
                  <AuthField label="Nome"><input className="input input-bordered auth-input" name="name" required /></AuthField>
                  <AuthField label="CPF"><input className="input input-bordered auth-input" inputMode="numeric" name="cpf" required /></AuthField>
                </div>
              )}

              <AuthField label="E-mail">
                <label className="input input-bordered auth-input flex items-center gap-3">
                  <Mail className="shrink-0 opacity-55" size={17} />
                  <input className="grow bg-transparent outline-none" name="email" required type="email" />
                </label>
              </AuthField>

              <AuthField label="Senha">
                <label className="input input-bordered auth-input flex items-center gap-2">
                  <KeyRound className="shrink-0 opacity-55" size={17} />
                  <input className="grow bg-transparent outline-none" minLength={8} name="password" required type={showPassword ? "text" : "password"} />
                  <button className="btn btn-ghost btn-circle btn-sm" aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"} onClick={() => setShowPassword((visible) => !visible)} type="button">
                    {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                  </button>
                </label>
              </AuthField>

              {error && <div className="alert alert-error rounded-2xl py-3 text-sm">{error}</div>}

              <button className="btn relative mt-2 min-h-12 rounded-2xl border-0 bg-[#4c532b] px-14 text-white hover:bg-[#3e4523]" disabled={loading} type="submit">
                {loading ? <span className="loading loading-spinner loading-sm" /> : null}
                <span>{loading ? "Processando..." : mode === "login" ? "Entrar" : "Registrar"}</span>
                {!loading && <ArrowRight className="absolute right-5 top-1/2 -translate-y-1/2" size={18} />}
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}

function ModeButton({ active, children, onClick }: { active: boolean; children: ReactNode; onClick: () => void }) {
  return (
    <button className={`relative min-h-20 px-4 text-base font-bold outline-none transition focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[#59651f] ${active ? "bg-white/24 text-[#1f2318]" : "text-[#2d321f]/65 hover:bg-white/15 hover:text-[#1f2318]"}`} onClick={onClick} type="button">
      {children}
      {active && <span className="absolute inset-x-8 bottom-0 h-1 rounded-full bg-[#59651f]" />}
    </button>
  );
}

function AuthField({ label, children }: { label: string; children: ReactNode }) {
  return <div className="grid gap-2 text-sm font-bold text-[#2b301e]"><span>{label}</span>{children}</div>;
}
