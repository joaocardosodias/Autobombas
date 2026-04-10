import { Shield } from "lucide-react"

/**
 * SystemFeatures — grade de funcionalidades do sistema.
 *
 * @param {object}  props
 * @param {Array}   props.features — lista de funcionalidades
 *   [{ id, icon: ReactNode, title: string, description: string }]
 */
export function SystemFeatures({ features = [] }) {
  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <Shield className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-primary">Funcionalidades do Sistema</h2>
          <p className="text-sm text-muted-foreground">Recursos disponíveis no dashboard</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((feature) => (
          <div
            key={feature.id}
            className="bg-card rounded-xl border-2 border-primary/10 p-5 hover:border-primary/30 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <span className="text-primary">{feature.icon}</span>
              </div>
              <div>
                <h3 className="font-semibold text-primary mb-1">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
              </div>
            </div>
          </div>
        ))}

        {features.length === 0 && (
          <p className="col-span-3 text-center text-sm text-muted-foreground py-8">
            Nenhuma funcionalidade cadastrada.
          </p>
        )}
      </div>
    </section>
  )
}
