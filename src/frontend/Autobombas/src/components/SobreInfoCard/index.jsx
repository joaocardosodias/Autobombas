import { FileText } from "lucide-react"

/**
 * PumpInfoCard — exibe a identificação e dados técnicos do equipamento.
 *
 * @param {object} props
 * @param {object} props.pump — dados do equipamento
 *   {
 *     id: string,
 *     modelo: string,
 *     serie: string,
 *     versaoFirmware: string,
 *     dataInstalacao: string,
 *     ultimaManutencao: string,
 *     capacidade: string,
 *     profundidadeMax: string,
 *     potencia: string,
 *     tensao: string,
 *     status: "online"|"offline"|"warning"
 *   }
 */
export function PumpInfoCard({ pump = {} }) {
  const {
    id               = "—",
    modelo           = "—",
    serie            = "—",
    versaoFirmware   = "—",
    dataInstalacao   = "—",
    ultimaManutencao = "—",
    capacidade       = "—",
    profundidadeMax  = "—",
    corrente         = "—",
    tensao           = "—",
    status           = "online",
  } = pump

  const isOnline = status === "online"

  const fields = [
    { label: "Modelo",              value: modelo },
    { label: "Número de Série",     value: serie,           mono: true },
    { label: "Versão Firmware",     value: versaoFirmware },
    { label: "Data de Instalação",  value: dataInstalacao },
    { label: "Última Manutenção",   value: ultimaManutencao },
    { label: "Capacidade",          value: capacidade },
    { label: "Profundidade Máx.",   value: profundidadeMax },
    { label: "Corrente / Tensão",   value: `${corrente} / ${tensao}` },
  ]

  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <FileText className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-primary">Identificação do Equipamento de Simulação</h2>
          <p className="text-sm text-muted-foreground">Dados da bomba de simulação de dragagem</p>
        </div>
      </div>

      <div className="bg-card rounded-2xl border-2 border-primary/10 shadow-sm overflow-hidden">
        {/* Destaque do ID */}
        <div className="bg-primary/5 px-6 py-4 border-b border-primary/10">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">
                ID do Equipamento
              </span>
              <h3 className="text-2xl font-bold text-primary font-mono">{id}</h3>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 rounded-full">
              <div
                className={
                  isOnline
                    ? "w-2 h-2 rounded-full bg-green-500 animate-pulse"
                    : "w-2 h-2 rounded-full bg-red-500"
                }
              />
              <span className="text-sm font-medium text-green-600">
                {isOnline ? "Operacional" : "Offline"}
              </span>
            </div>
          </div>
        </div>

        {/* Grid de campos */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {fields.map(({ label, value, mono }) => (
              <div key={label} className="space-y-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
                <p className={`font-semibold text-primary ${mono ? "font-mono" : ""}`}>{value}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
