import { useState } from "react";
import type { FormEvent } from "react";
import type { Implement } from "../types/api";
import { api } from "../services/api";

export function DatabaseSearch() {
  const [items, setItems] = useState<Implement[]>([]);

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
  }

  return (
    <section className="space-y-5">
      <div>
        <p className="text-xs font-bold uppercase text-soil-600">Base técnica</p>
        <h2 className="text-3xl font-bold">Consulta de implementos</h2>
      </div>
      <form className="panel grid gap-3 p-4 md:grid-cols-[180px_1fr_auto]" onSubmit={submit}>
        <select className="input" name="grupo">
          <option value="">Todos</option>
          <option value="ARADO">Arados</option>
          <option value="GRADE">Grades</option>
        </select>
        <input className="input" name="q" placeholder="Buscar por família, modelo ou descrição..." />
        <button className="button">Buscar</button>
      </form>
      <div className="panel overflow-auto">
        <table className="min-w-[900px] w-full border-collapse text-sm">
          <thead className="bg-soil-100 text-left">
            <tr>
              <th className="p-3">Grupo</th>
              <th className="p-3">Modelo</th>
              <th className="p-3">Descrição</th>
              <th className="p-3">Largura</th>
              <th className="p-3">Peso</th>
              <th className="p-3">Potência</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr className="border-t border-soil-100" key={item.id}>
                <td className="p-3">{item.grupo}</td>
                <td className="p-3 font-bold">{item.modelo}</td>
                <td className="p-3">{item.descricao}</td>
                <td className="p-3">{item.largura_mm ?? "ND"} mm</td>
                <td className="p-3">{item.peso_medio_kg?.toFixed(1) ?? "ND"} kg</td>
                <td className="p-3">{item.potencia_min_hp ?? "ND"} a {item.potencia_max_hp ?? "ND"} hp</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
