import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { ArrowDown, Gauge, Loader2, Ruler, Scale, Search, Tractor } from "lucide-react";
import type { RecommendationItem, RecommendationRequest } from "../types/api";
import { api } from "../services/api";

export function RecommendationForm() {
  const [items, setItems] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    const form = new FormData(event.currentTarget);
    const payload: RecommendationRequest = {
      implement_type: String(form.get("implement_type") || ""),
      family: String(form.get("family") || ""),
      tractor_power_hp: Number(form.get("tractor_power_hp") || 0) || undefined,
      soil_texture: String(form.get("soil_texture") || ""),
      moisture: String(form.get("moisture") || ""),
      crop: String(form.get("crop") || ""),
      limit: 8,
    };
    const result = await api.recommend(payload);
    setItems(result.recommendations);
    setLoading(false);
  }

  return (
    <section className="space-y-6">
      <div className="home-intro grid overflow-hidden rounded-3xl border border-[#bbb5a8] bg-[#d9d5c9] lg:grid-cols-[1.15fr_0.85fr]">
        <div className="p-6 md:p-9 lg:p-12">
          <p className="text-xs font-bold uppercase text-black/60">Seleção de implementos</p>
          <h2 className="mt-4 max-w-3xl text-4xl font-bold leading-[1.05] text-black md:text-5xl lg:text-6xl">Compatibilidade antes de entrar no campo.</h2>
          <p className="mt-5 max-w-2xl text-base leading-7 text-black/70 md:text-lg">Cruze potência disponível, condição do solo e tipo de operação para encontrar configurações adequadas de arados e grades.</p>
        </div>
        <div className="grid grid-cols-2 border-t border-[#aaa496] lg:border-l lg:border-t-0">
          <IntroFact icon={<Tractor size={24} />} label="1. Informe" value="Trator e operação" />
          <IntroFact icon={<Gauge size={24} />} label="2. Compare" value="Potência e conjunto" />
          <div className="col-span-2 flex items-center justify-between border-t border-[#aaa496] p-5 text-black md:p-7">
            <span className="text-sm font-semibold">Comece pelos dados disponíveis</span><ArrowDown size={22} />
          </div>
        </div>
      </div>
      <div>
        <p className="eyebrow">Dados da operação</p>
        <h3 className="mt-2 text-2xl font-bold text-slate-950">Encontre um conjunto compatível</h3>
        <p className="muted mt-2">Preencha apenas o que souber. Os campos em branco não impedem a consulta.</p>
      </div>
      <form className="panel grid gap-5 p-5 md:grid-cols-3 md:p-6" onSubmit={submit}>
        <Field label="Implemento">
          <select className="input" name="implement_type">
            <option value="">Todos</option>
            <option value="ARADO">Arado</option>
            <option value="GRADE">Grade</option>
          </select>
        </Field>
        <Field label="Família ou modelo">
          <input className="input" name="family" placeholder="NVCR, ASTH, CRI..." />
        </Field>
        <Field label="Potência do trator">
          <input className="input" name="tractor_power_hp" type="number" placeholder="120" />
        </Field>
        <Field label="Solo">
          <select className="input" name="soil_texture">
            <option value="">Não informado</option>
            <option value="argiloso">Argiloso</option>
            <option value="textura media">Textura média</option>
            <option value="arenoso">Arenoso</option>
          </select>
        </Field>
        <Field label="Umidade">
          <select className="input" name="moisture">
            <option value="">Não informado</option>
            <option value="seco">Seco</option>
            <option value="adequado">Adequado</option>
            <option value="umido">Úmido</option>
          </select>
        </Field>
        <Field label="Cultura">
          <input className="input" name="crop" placeholder="Soja, milho..." />
        </Field>
        <button className="button md:col-span-3" disabled={loading}>
          {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
          {loading ? "Verificando catálogo..." : "Buscar implementos compatíveis"}
        </button>
      </form>
      <div className="grid gap-4 lg:grid-cols-2">
        {items.map((item) => (
          <article className="panel overflow-hidden" key={`${item.implement.id}-${item.score}`}>
            <div className="mb-3 flex items-start justify-between gap-4">
              <div className="min-w-0 p-5 pb-2 md:p-6 md:pb-2">
                <p className="mb-2 text-xs font-semibold uppercase text-soil-600">{item.implement.grupo}</p>
                <h3 className="truncate text-lg font-semibold text-slate-950">{item.implement.modelo}</h3>
                <p className="muted mt-1">{item.implement.descricao}</p>
              </div>
              <span className="m-5 flex h-12 min-w-12 items-center justify-center rounded-full bg-field-500 px-3 text-sm font-semibold text-white md:m-6">{item.score}</span>
            </div>
            <dl className="grid gap-3 px-5 pb-5 sm:grid-cols-2 md:px-6 md:pb-6">
              <Fact icon={<Tractor size={17} />} label="Potência" value={`${item.implement.potencia_min_hp} a ${item.implement.potencia_max_hp} hp`} />
              <Fact icon={<Gauge size={17} />} label="ML" value={`${item.ml_predicted_power_hp} hp`} />
              <Fact icon={<Ruler size={17} />} label="Largura" value={`${item.implement.largura_mm ?? "ND"} mm`} />
              <Fact icon={<Scale size={17} />} label="Peso médio" value={`${item.implement.peso_medio_kg?.toFixed(1) ?? "ND"} kg`} />
            </dl>
            <p className="border-t border-slate-200 bg-slate-50 px-5 py-4 text-sm leading-6 text-slate-600 md:px-6">{item.technical_note}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function IntroFact({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="flex min-h-36 flex-col justify-between border-r border-[#aaa496] p-5 text-black last:border-r-0 md:p-7">
      {icon}
      <div><p className="text-xs font-bold uppercase text-black/55">{label}</p><p className="mt-1 text-sm font-bold md:text-base">{value}</p></div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="grid gap-2 text-sm font-semibold text-slate-600">
      {label}
      {children}
    </label>
  );
}

function Fact({ icon, label, value }: { icon: ReactNode; label: string; value: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3">
      <dt className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
        {icon}
        {label}
      </dt>
      <dd className="text-sm font-semibold text-slate-900">{value}</dd>
    </div>
  );
}
