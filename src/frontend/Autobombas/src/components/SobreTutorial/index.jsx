import { useState } from "react"
import { BookOpen, ChevronRight, ChevronDown } from "lucide-react"
import { cn } from "../../lib/utils"

/**
 * TutorialAccordion — lista de tutoriais expansíveis.
 *
 * @param {object}  props
 * @param {Array}   props.tutorials — lista de tutoriais
 *   [{
 *     id: string,
 *     title: string,
 *     icon: ReactNode,
 *     steps: [{ title: string, description: string }]
 *   }]
 * @param {string}  [props.defaultOpen] — id do tutorial aberto por padrão
 */
export function TutorialAccordion({ tutorials = [], defaultOpen = null }) {
  const [expanded, setExpanded] = useState(defaultOpen)

  const toggle = (id) => setExpanded((prev) => (prev === id ? null : id))

  return (
    <section className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-primary">Tutoriais de Utilização</h2>
          <p className="text-sm text-muted-foreground">Aprenda a utilizar o sistema</p>
        </div>
      </div>

      <div className="space-y-3">
        {tutorials.map((tutorial) => {
          const isOpen = expanded === tutorial.id
          return (
            <div
              key={tutorial.id}
              className="bg-card rounded-xl border-2 border-primary/10 overflow-hidden transition-all duration-200"
            >
              <button
                onClick={() => toggle(tutorial.id)}
                className="w-full flex items-center justify-between p-5 hover:bg-primary/5 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={cn(
                      "w-10 h-10 rounded-lg flex items-center justify-center transition-colors",
                      isOpen ? "bg-[#1e4d2b] text-white" : "bg-primary/10 text-primary"
                    )}
                  >
                    {tutorial.icon}
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-primary">{tutorial.title}</h3>
                    <p className="text-sm text-muted-foreground">{tutorial.steps.length} passos</p>
                  </div>
                </div>
                {isOpen ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground" />
                )}
              </button>

              {isOpen && (
                <div className="px-5 pb-5 border-t border-primary/10">
                  <div className="pt-4 space-y-4">
                    {tutorial.steps.map((step, i) => (
                      <div key={i} className="flex gap-4">
                        <div className="flex flex-col items-center">
                          <div className="w-8 h-8 rounded-full bg-[#1e4d2b] flex items-center justify-center text-sm font-bold  text-white shrink-0">
                            {i + 1}
                          </div>
                          {i < tutorial.steps.length - 1 && (
                            <div className="w-0.5 flex-1 bg-primary/10 mt-2" />
                          )}
                        </div>
                        <div className="pb-4">
                          <h4 className="font-medium text-primary mb-1">{step.title}</h4>
                          <p className="text-sm text-muted-foreground leading-relaxed">{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}

        {tutorials.length === 0 && (
          <p className="text-center text-sm text-muted-foreground py-8">
            Nenhum tutorial disponível.
          </p>
        )}
      </div>
    </section>
  )
}
