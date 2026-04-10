import { AlertTriangle, HelpCircle, Phone, Mail } from "lucide-react"

/**
 * SafetyWarnings — bloco de avisos de segurança.
 *
 * @param {object}  props
 * @param {Array}   props.warnings — lista de strings com os avisos
 */
export function SafetyWarnings({ warnings = [] }) {
  if (warnings.length === 0) return null

  return (
    <section className="mt-8">
      <div className="bg-amber-500/10 border-2 border-amber-500/30 rounded-xl p-5">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h3 className="font-semibold text-amber-700 mb-2">Avisos de Segurança</h3>
            <ul className="space-y-2">
              {warnings.map((w, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-amber-700/80">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 shrink-0" />
                  {w}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}

/**
 * SupportCard — bloco de contato do suporte técnico.
 *
 * @param {object} props
 * @param {string} props.phone — telefone de suporte
 * @param {string} props.email — e-mail de suporte
 */
export function SupportCard({ phone = "—", email = "—" }) {
  return (
    <section className="mt-6 mb-4">
      <div className="bg-card rounded-xl border-2 border-primary/10 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <HelpCircle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-primary">Precisa de Ajuda?</h3>
              <p className="text-sm text-muted-foreground">Entre em contato com o suporte técnico</p>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <a
              href={`tel:${phone}`}
              className="flex items-center gap-2 px-4 py-2 bg-primary/5 text-primary rounded-lg hover:bg-primary/10 transition-colors text-sm font-medium"
            >
              <Phone size={16} />
              {phone}
            </a>
            <a
              href={`mailto:${email}`}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
            >
              <Mail size={16} />
              {email}
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}
