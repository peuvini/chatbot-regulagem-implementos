import { BarChart3, Bot, CheckCircle2, Database, Gauge, Layers3, LineChart, Microscope, PieChart, ShieldCheck, Tractor, XCircle } from "lucide-react";
import type { ReactNode } from "react";
import type { DashboardData } from "../types/api";

type Props = {
  data: DashboardData | null;
};

export function Dashboard({ data }: Props) {
  const totalImplements = data?.implements.reduce((sum, item) => sum + item.total, 0) ?? 0;
  const scientific = data?.scientific;

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="eyebrow">Validação progressiva</p>
          <h2 className="page-title">Dashboard de métricas científicas</h2>
          <p className="muted mt-2 max-w-3xl">
            Indicadores para acompanhar qualidade dos dados, cobertura do treinamento, desempenho do modelo e sinais de uso durante a validação técnica do projeto.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="chip">Base técnica</span>
          <span className="chip">Validação</span>
          <span className="chip">Machine learning</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={<Database />} label="Implementos extraídos" value={totalImplements || "-"} detail={`${data?.implements.length ?? 0} grupos técnicos`} />
        <Metric icon={<Tractor />} label="Tratores na base" value={data?.tractors.total ?? "-"} detail={data ? `${data.tractors.potencia_min} a ${data.tractors.potencia_max} hp` : "Aguardando dados"} />
        <Metric icon={<Bot />} label="Erro médio do ML" value={data ? `${data.model.mae_hp.toFixed(1)} hp` : "-"} detail={data ? `RMSE ${data.model.rmse_hp.toFixed(1)} hp` : "Modelo não carregado"} />
        <Metric icon={<ShieldCheck />} label="Cobertura de treino" value={scientific ? `${scientific.ml_readiness.training_coverage_percent}%` : "-"} detail={data ? `${data.model.training_rows} linhas usadas` : "Aguardando modelo"} />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <Panel title="Qualidade dos Dados" eyebrow="Completude das extrações" icon={<Microscope size={22} />}>
          <div className="mb-5 grid gap-3 sm:grid-cols-3">
            <MiniStat label="Registros completos" value={scientific ? scientific.data_quality.complete_rows : "-"} />
            <MiniStat label="Completude crítica" value={scientific ? `${scientific.data_quality.complete_rows_percent}%` : "-"} />
            <MiniStat label="Total analisado" value={scientific ? scientific.data_quality.total_implements : "-"} />
          </div>
          <div className="grid gap-3">
            {scientific?.data_quality.completeness.map((item) => (
              <ProgressRow key={item.field} label={item.label} percent={item.percent} detail={`${item.filled} preenchidos · ${item.missing} faltantes`} />
            ))}
          </div>
        </Panel>

        <Panel title="Prontidão do Modelo" eyebrow="Indicadores de ML" icon={<LineChart size={22} />}>
          <div className="grid gap-3">
            <ReadinessItem label="Variável alvo" value={scientific?.ml_readiness.target ?? "-"} />
            <ReadinessItem label="Variáveis do modelo" value={scientific?.ml_readiness.feature_count ?? "-"} />
            <ReadinessItem label="MAE relativo" value={scientific ? `${scientific.ml_readiness.relative_mae_percent}%` : "-"} />
            <ReadinessItem label="Linhas de treino" value={data?.model.training_rows ?? "-"} />
          </div>
          <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-900">Leitura científica</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Quanto menor o MAE relativo, mais próxima a predição está da potência média indicada nos catálogos técnicos.
            </p>
          </div>
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel title="Distribuição por Potência" eyebrow="Implementos" icon={<BarChart3 size={22} />}>
          <BucketChart items={scientific?.power_ranges ?? []} colorClass="bg-soil-800" />
        </Panel>

        <Panel title="Disponibilidade de Tratores" eyebrow="Faixas de potência" icon={<Gauge size={22} />}>
          <BucketChart items={scientific?.tractor_power_ranges ?? []} colorClass="bg-field-500" />
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel title="Uso nas Recomendações" eyebrow="Validação com usuários" icon={<PieChart size={22} />}>
          <div className="grid gap-3 sm:grid-cols-3">
            <MiniStat label="Recomendações" value={scientific?.recommendation_usage.total_recommendations ?? 0} />
            <MiniStat label="Score médio top 1" value={scientific ? scientific.recommendation_usage.avg_top_score : "-"} />
            <MiniStat label="Itens retornados" value={scientific ? scientific.recommendation_usage.avg_returned_items : "-"} />
          </div>
          <div className="mt-5 grid gap-5 lg:grid-cols-3">
            <RankList title="Solos buscados" items={scientific?.recommendation_usage.top_requested_soils ?? []} />
            <RankList title="Implementos pedidos" items={scientific?.recommendation_usage.top_requested_implements ?? []} />
            <RankList title="Grupos recomendados" items={scientific?.recommendation_usage.top_recommended_groups ?? []} />
          </div>
        </Panel>

        <Panel title="Checklist de Validação" eyebrow="Próximos critérios científicos" icon={<CheckCircle2 size={22} />}>
          <div className="grid gap-3">
            {scientific?.validation_checklist.map((item) => (
              <div className="grid grid-cols-[auto_1fr] gap-3 rounded-xl border border-slate-200 bg-white p-4" key={item.label}>
                <div className={item.status ? "text-soil-600" : "text-slate-400"}>{item.status ? <CheckCircle2 size={20} /> : <XCircle size={20} />}</div>
                <div>
                  <p className="text-sm font-semibold text-slate-950">{item.label}</p>
                  <p className="mt-1 text-sm text-slate-500">{item.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel title="Famílias com Mais Configurações" eyebrow="Base técnica" icon={<Layers3 size={22} />}>
          <div className="grid gap-3">
            {data?.families.slice(0, 8).map((item) => (
              <div className="grid grid-cols-[1fr_auto] items-center gap-4 rounded-xl border border-slate-100 bg-slate-50/70 p-3" key={`${item.grupo}-${item.familia}`}>
                <div className="min-w-0">
                  <strong className="block truncate text-sm font-semibold text-slate-900">{item.familia}</strong>
                  <p className="text-xs font-semibold text-slate-500">{item.grupo}</p>
                </div>
                <span className="flex h-9 min-w-9 items-center justify-center rounded-full bg-soil-800 px-3 text-sm font-semibold text-white">{item.total}</span>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Resumo por Grupo" eyebrow="Arados e grades" icon={<Database size={22} />}>
          <div className="grid gap-3">
            {data?.implements.map((item) => (
              <div className="rounded-xl border border-slate-200 bg-white p-4" key={item.grupo}>
                <div className="mb-3 flex items-center justify-between">
                  <p className="font-semibold text-slate-950">{item.grupo}</p>
                  <span className="chip">{item.total} registros</span>
                </div>
                <div className="grid gap-2 text-sm text-slate-600">
                  <span>Potência média: <strong className="text-slate-950">{item.potencia_media} hp</strong></span>
                  <span>Peso médio: <strong className="text-slate-950">{item.peso_medio} kg</strong></span>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </section>
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

function Panel({ title, eyebrow, icon, children }: { title: string; eyebrow: string; icon: ReactNode; children: ReactNode }) {
  return (
    <section className="panel p-5 md:p-6">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-950">{title}</h3>
        </div>
        <div className="text-soil-600">{icon}</div>
      </div>
      {children}
    </section>
  );
}

function MiniStat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase text-slate-500">{label}</p>
      <strong className="mt-2 block text-xl font-semibold text-slate-950">{value}</strong>
    </div>
  );
}

function ProgressRow({ label, percent, detail }: { label: string; percent: number; detail: string }) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4">
        <span className="text-sm font-semibold text-slate-700">{label}</span>
        <span className="text-sm font-semibold text-slate-950">{percent}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-soil-700" style={{ width: `${Math.max(4, percent)}%` }} />
      </div>
      <p className="mt-1 text-xs text-slate-500">{detail}</p>
    </div>
  );
}

function BucketChart({ items, colorClass }: { items: Array<{ label: string; count: number; percent: number }>; colorClass: string }) {
  return (
    <div className="grid gap-4">
      {items.map((item) => (
        <div className="grid gap-2" key={item.label}>
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm font-semibold text-slate-700">{item.label}</span>
            <span className="text-sm text-slate-500">{item.count} registros · {item.percent}%</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-slate-100">
            <div className={`h-full rounded-full ${colorClass}`} style={{ width: `${Math.max(4, item.percent)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function ReadinessItem({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex min-h-12 items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white px-4">
      <span className="text-sm font-semibold text-slate-600">{label}</span>
      <strong className="text-sm font-semibold text-slate-950">{value}</strong>
    </div>
  );
}

function RankList({ title, items }: { title: string; items: Array<{ label: string; count: number; percent: number }> }) {
  return (
    <div>
      <p className="mb-3 text-sm font-semibold text-slate-950">{title}</p>
      <div className="grid gap-2">
        {items.length ? (
          items.map((item) => (
            <div className="rounded-xl border border-slate-200 bg-white p-3" key={item.label}>
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="truncate font-semibold text-slate-700">{item.label}</span>
                <span className="text-slate-500">{item.count}</span>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-soil-700" style={{ width: `${Math.max(4, item.percent)}%` }} />
              </div>
            </div>
          ))
        ) : (
          <p className="rounded-xl border border-dashed border-slate-200 p-3 text-sm text-slate-500">Sem dados registrados ainda.</p>
        )}
      </div>
    </div>
  );
}
