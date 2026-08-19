import { useState } from "react";
import type { FormEvent } from "react";
import { Database, Search } from "lucide-react";
import type { Implement } from "../types/api";
import { api } from "../services/api";

type Props = {
  trainingRows?: number;
};

export function DatabaseSearch({ trainingRows }: Props) {
  const [items, setItems] = useState<Implement[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const params = new URLSearchParams();
    params.set("limit", "120");
    for (const [key, value] of form.entries()) {
      if (String(value)) params.set(key, String(value));
    }
    const result = await api.implements(params);
    setItems(result.items);
    setHasSearched(true);
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="eyebrow">Base técnica</p>
          <h2 className="page-title">Consulta de implementos</h2>
          <p className="muted mt-2 max-w-2xl">Pesquise modelos extraídos das planilhas de arados e grades para conferir largura, peso e potência exigida.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="chip">
            <Database size={14} />
            {trainingRows ?? "-"} linhas de treino
          </span>
          <span className="chip">{items.length || 0} registros na tela</span>
        </div>
      </div>
      <form className="panel grid gap-3 p-4 md:grid-cols-[180px_1fr_auto]" onSubmit={submit}>
        <select className="input" name="grupo">
          <option value="">Todos</option>
          <option value="ARADO">Arados</option>
          <option value="GRADE">Grades</option>
        </select>
        <input className="input" name="q" placeholder="Buscar por família, modelo ou descrição..." />
        <button className="button">
          <Search size={18} />
          Buscar
        </button>
      </form>
      {!hasSearched && (
        <div className="panel grid min-h-56 place-items-center p-8 text-center">
          <div>
            <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#e4eadf] text-[#31533f]"><Database size={25} /></span>
            <h3 className="mt-4 text-lg font-bold">Consulte a base técnica</h3>
            <p className="muted mt-2">Escolha os filtros ou informe um modelo para começar a pesquisa.</p>
          </div>
        </div>
      )}
      {hasSearched && items.length === 0 && (
        <div className="panel grid min-h-56 place-items-center p-8 text-center">
          <div>
            <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#eee4d5] text-[#6d513c]"><Search size={24} /></span>
            <h3 className="mt-4 text-lg font-bold">Nenhum implemento encontrado</h3>
            <p className="muted mt-2">Revise os filtros e tente uma descrição mais ampla.</p>
          </div>
        </div>
      )}
      {items.length > 0 && <div className="panel panel-scroll overflow-auto">
        <table className="w-full min-w-[900px] border-collapse text-sm">
          <thead className="bg-slate-950 text-left text-white">
            <tr>
              <th className="px-4 py-3 font-semibold">Grupo</th>
              <th className="px-4 py-3 font-semibold">Modelo</th>
              <th className="px-4 py-3 font-semibold">Descrição</th>
              <th className="px-4 py-3 font-semibold">Largura</th>
              <th className="px-4 py-3 font-semibold">Peso</th>
              <th className="px-4 py-3 font-semibold">Potência</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr className="border-t border-slate-200 transition hover:bg-slate-50" key={item.id}>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.grupo === "ARADO" ? "bg-harvest-500/10 text-harvest-500" : "bg-field-500/10 text-field-700"}`}>
                    {item.grupo}
                  </span>
                </td>
                <td className="px-4 py-3 font-semibold text-slate-950">{item.modelo}</td>
                <td className="max-w-[360px] px-4 py-3 text-slate-600">{item.descricao}</td>
                <td className="px-4 py-3 text-slate-700">{item.largura_mm ?? "ND"} mm</td>
                <td className="px-4 py-3 text-slate-700">{item.peso_medio_kg?.toFixed(1) ?? "ND"} kg</td>
                <td className="px-4 py-3 font-semibold text-slate-900">{item.potencia_min_hp ?? "ND"} a {item.potencia_max_hp ?? "ND"} hp</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>}
    </section>
  );
}
