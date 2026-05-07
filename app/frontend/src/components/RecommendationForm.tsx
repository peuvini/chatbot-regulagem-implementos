import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
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
    <section className="space-y-5">
      <div>
        <p className="text-xs font-bold uppercase text-soil-600">Assistência técnica</p>
        <h2 className="text-3xl font-bold">Recomendação personalizada</h2>
      </div>
      <form className="panel grid gap-4 p-5 md:grid-cols-3" onSubmit={submit}>
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
          {loading ? "Processando..." : "Gerar recomendação"}
        </button>
      </form>
      <div className="grid gap-4 lg:grid-cols-2">
        {items.map((item) => (
          <article className="panel p-5" key={`${item.implement.id}-${item.score}`}>
            <div className="mb-3 flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold">{item.implement.modelo}</h3>
                <p className="text-sm text-slate-500">{item.implement.descricao}</p>
              </div>
              <span className="rounded-md bg-field-500 px-3 py-2 font-bold text-white">{item.score}</span>
            </div>
            <dl className="grid grid-cols-[130px_1fr] gap-2 text-sm">
              <dt className="font-bold text-slate-500">Potência</dt>
              <dd>{item.implement.potencia_min_hp} a {item.implement.potencia_max_hp} hp</dd>
              <dt className="font-bold text-slate-500">ML</dt>
              <dd>{item.ml_predicted_power_hp} hp</dd>
              <dt className="font-bold text-slate-500">Largura</dt>
              <dd>{item.implement.largura_mm} mm</dd>
              <dt className="font-bold text-slate-500">Peso médio</dt>
              <dd>{item.implement.peso_medio_kg?.toFixed(1)} kg</dd>
            </dl>
            <p className="mt-4 text-sm leading-6 text-slate-600">{item.technical_note}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="grid gap-2 text-sm font-bold text-slate-600">
      {label}
      {children}
    </label>
  );
}
