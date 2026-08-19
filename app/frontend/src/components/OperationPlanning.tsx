import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { CalendarDays, Clock, FileText, Gauge, Ruler, Search, Tractor } from "lucide-react";
import { ApiError, api } from "../services/api";
import type { OperationPlanningResponse, OperationSizing } from "../types/api";

export function OperationPlanning() {
  const [result, setResult] = useState<OperationPlanningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [startDate, setStartDate] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setFieldErrors({});
    const form = new FormData(event.currentTarget);
    const startDateValue = String(form.get("start_date") || "");
    const endDateValue = String(form.get("end_date") || "");
    if (startDateValue && endDateValue && endDateValue <= startDateValue) {
      setFieldErrors({ end_date: "A data final deve ser posterior à data inicial." });
      setError("Corrija a data final para calcular o planejamento.");
      setLoading(false);
      return;
    }
    try {
      const response = await api.planOperation({
        area_ha: Number(form.get("area_ha") || 0),
        start_date: startDateValue,
        end_date: endDateValue,
        hours_per_day: Number(form.get("hours_per_day") || 8),
      });
      setResult(response);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message);
        setFieldErrors(Object.fromEntries(caught.fields.map((item) => [item.field, item.message])));
      } else {
        setError(caught instanceof Error ? caught.message : "Não foi possível calcular o planejamento.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="eyebrow">Dimensionamento operacional</p>
          <h2 className="page-title">Planejamento de conjuntos mecanizados</h2>
          <p className="muted mt-2 max-w-3xl">
            Informe area e periodo de trabalho para calcular tempo disponivel, ritmo operacional, largura necessaria e quantidade de conjuntos para arado, grade destorroadora e grade niveladora.
          </p>
        </div>
        <span className="chip">
          <Clock size={14} />
          Jornada padrao de 8 h/dia
        </span>
      </div>

      <form className="panel grid gap-5 p-5 md:grid-cols-4 md:p-6" onSubmit={submit}>
        <Field label="Area a preparar (ha)">
          <input className="input" min="0.1" name="area_ha" placeholder="120" required step="0.1" type="number" />
        </Field>
        <Field label="Data inicial">
          <input className="input" name="start_date" onChange={(event) => setStartDate(event.target.value)} required type="date" />
        </Field>
        <Field error={fieldErrors.end_date} label="Data final">
          <input aria-invalid={Boolean(fieldErrors.end_date)} className="input aria-[invalid=true]:border-red-500 aria-[invalid=true]:ring-2 aria-[invalid=true]:ring-red-100" min={startDate || undefined} name="end_date" required type="date" />
        </Field>
        <Field label="Horas por dia">
          <input className="input" defaultValue={8} max={24} min={1} name="hours_per_day" required step="0.5" type="number" />
        </Field>
        {error && <p className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm font-semibold text-red-700 md:col-span-4">{error}</p>}
        <button className="button md:col-span-4" disabled={loading} type="submit">
          <Search size={18} />
          {loading ? "Calculando..." : "Calcular planejamento"}
        </button>
      </form>

      {result && (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Metric icon={<CalendarDays />} label="Dias do periodo" value={result.time_distribution.days} detail="Data final - data inicial" />
            <Metric icon={<Clock />} label="Tempo disponivel" value={`${result.time_distribution.total_available_hours} h`} detail={`${result.time_distribution.hours_per_day} h por dia`} />
            <Metric icon={<Tractor />} label="Tempo arado" value={`${result.time_distribution.plow_hours} h`} detail="TD x 2/3" />
            <Metric icon={<Gauge />} label="Tempo grades" value={`${result.time_distribution.harrow_total_hours} h`} detail="TD x 1/3" />
          </div>

          <div className="grid gap-5 xl:grid-cols-3">
            {result.operations.map((operation) => (
              <OperationCard operation={operation} key={operation.key} />
            ))}
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
            <section className="panel p-5 md:p-6">
              <div className="mb-5 flex items-center justify-between gap-4">
                <div>
                  <p className="eyebrow">Relatorio final</p>
                  <h3 className="text-lg font-semibold text-slate-950">Conjuntos recomendados</h3>
                </div>
                <FileText className="text-soil-600" size={22} />
              </div>
              <div className="grid gap-3">
                {result.final_report.map((line) => (
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm font-semibold text-slate-800" key={line}>
                    {line}
                  </div>
                ))}
              </div>
            </section>

            <section className="panel p-5 md:p-6">
              <div className="mb-5">
                <p className="eyebrow">Formulas aplicadas</p>
                <h3 className="text-lg font-semibold text-slate-950">Memorial de calculo</h3>
              </div>
              <div className="grid gap-2">
                {result.formulas.map((formula) => (
                  <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700" key={formula}>
                    {formula}
                  </div>
                ))}
              </div>
            </section>
          </div>
        </>
      )}
    </section>
  );
}

function OperationCard({ operation }: { operation: OperationSizing }) {
  return (
    <article className="panel overflow-hidden">
      <div className="border-b border-slate-200 bg-slate-50 p-5">
        <p className="eyebrow">{operation.name}</p>
        <h3 className="mt-2 text-xl font-semibold text-slate-950">{operation.equipment_count} conjunto(s)</h3>
        <p className="muted mt-2">{operation.formula}</p>
      </div>
      <div className="grid gap-3 p-5">
        <Fact label="Area considerada" value={`${operation.area_considered_ha} ha`} />
        <Fact label="Tempo disponivel" value={`${operation.available_hours} h`} />
        <Fact label="Ritmo operacional" value={`${operation.operational_rhythm_ha_h} ha/h`} />
        <Fact label="Largura minima" value={`${operation.required_width_m} m`} />
        <Fact label="Largura selecionada" value={operation.selected_width_m ? `${operation.selected_width_m} m` : "ND"} />
        <Fact label="Potencia requerida" value={operation.required_power_hp ? `${operation.required_power_hp} hp` : "ND"} />
      </div>
      <div className="grid gap-3 border-t border-slate-200 bg-white p-5">
        <Selection icon={<Ruler size={17} />} label="Implemento" title={operation.implement?.modelo ?? "Nao encontrado"} detail={operation.implement?.descricao ?? "Sem implemento compativel"} />
        <Selection icon={<Tractor size={17} />} label="Trator" title={operation.tractor?.nome ?? "Nao encontrado"} detail={operation.tractor?.potencia_hp ? `${operation.tractor.potencia_hp} hp` : "Sem trator compativel"} />
        {operation.notes.map((note) => (
          <p className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-800" key={note}>
            {note}
          </p>
        ))}
      </div>
    </article>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: ReactNode }) {
  return (
    <label className="grid gap-2 text-sm font-semibold text-slate-600">
      {label}
      {children}
      {error && <span className="text-xs font-semibold text-red-700">{error}</span>}
    </label>
  );
}

function Metric({ icon, label, value, detail }: { icon: ReactNode; label: string; value: ReactNode; detail: string }) {
  return (
    <article className="panel p-5">
      <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-soil-100 text-soil-800">{icon}</div>
      <span className="text-sm font-medium text-slate-500">{label}</span>
      <strong className="mt-2 block text-2xl font-semibold text-slate-950">{value}</strong>
      <p className="mt-2 text-sm text-slate-500">{detail}</p>
    </article>
  );
}

function Fact({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex min-h-11 items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white px-3">
      <span className="text-sm font-semibold text-slate-500">{label}</span>
      <strong className="text-sm font-semibold text-slate-950">{value}</strong>
    </div>
  );
}

function Selection({ icon, label, title, detail }: { icon: ReactNode; label: string; title: string; detail: string }) {
  return (
    <div className="grid grid-cols-[auto_1fr] gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
      <div className="mt-1 text-soil-700">{icon}</div>
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
        <p className="truncate text-sm font-semibold text-slate-950">{title}</p>
        <p className="mt-1 text-sm text-slate-500">{detail}</p>
      </div>
    </div>
  );
}
