import { BarChart3, Bot, Database, Gauge } from "lucide-react";
import type { ReactNode } from "react";

type Props = {
  data: {
    implements: Array<{ grupo: string; total: number; potencia_media: number; peso_medio: number }>;
    tractors: { total: number; potencia_min: number; potencia_max: number; potencia_media: number };
    families: Array<{ familia: string; grupo: string; total: number }>;
    model: { mae_hp: number; rmse_hp: number; training_rows: number };
  } | null;
};

export function Dashboard({ data }: Props) {
  const totalImplements = data?.implements.reduce((sum, item) => sum + item.total, 0) ?? 0;

  return (
    <section className="space-y-5">
      <div>
        <p className="text-xs font-bold uppercase text-soil-600">Validação progressiva</p>
        <h2 className="text-3xl font-bold">Painel técnico-científico</h2>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Metric icon={<Database />} label="Implementos" value={totalImplements || "-"} />
        <Metric icon={<Gauge />} label="Tratores" value={data?.tractors.total ?? "-"} />
        <Metric icon={<BarChart3 />} label="Faixa dos tratores" value={data ? `${data.tractors.potencia_min} a ${data.tractors.potencia_max} hp` : "-"} />
        <Metric icon={<Bot />} label="Erro médio ML" value={data ? `${data.model.mae_hp.toFixed(1)} hp` : "-"} />
      </div>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="panel p-5">
          <h3 className="mb-4 text-lg font-bold">Famílias com mais configurações</h3>
          <div className="space-y-3">
            {data?.families.slice(0, 10).map((item) => (
              <div className="flex items-center justify-between border-b border-soil-100 pb-2" key={`${item.grupo}-${item.familia}`}>
                <div>
                  <strong>{item.familia}</strong>
                  <p className="text-sm text-slate-500">{item.grupo}</p>
                </div>
                <span className="rounded-md bg-soil-100 px-2 py-1 text-sm font-bold text-soil-800">{item.total}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-5">
          <h3 className="mb-4 text-lg font-bold">Fluxo do sistema</h3>
          <div className="grid gap-3">
            {["XLSX técnico", "ETL", "PostgreSQL", "Modelo ML", "FastAPI", "React"].map((step) => (
              <div className="rounded-md bg-soil-100 p-3 font-bold text-soil-800" key={step}>
                {step}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: ReactNode }) {
  return (
    <article className="panel p-5">
      <div className="mb-4 text-soil-600">{icon}</div>
      <span className="text-sm text-slate-500">{label}</span>
      <strong className="mt-2 block text-2xl">{value}</strong>
    </article>
  );
}
