import { ArrowRight } from "lucide-react";

export function LoginVisual() {

  const features = [
    "Controle de equipamentos em tempo real",
    "Indicadores e relatórios automáticos",
    "Integração com múltiplos processos",
  ];

  return (
    <div className="relative flex h-full w-full overflow-hidden">

      {/* Background imagem */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url('/itubombas-bg.png')",
        }}
      />

     
      <div className="absolute inset-0 bg-linear-to-r from-[#052e1b]/75 via-[#0a3f26]/55 to-transparent" />

      
      <div className="absolute -left-25 top-25 h-75 w-75 rounded-full bg-[#2c8f54]/20 blur-3xl" />

      {/* Conteúdo */}
      <div className="relative z-10 flex h-full flex-col justify-center px-16 xl:px-24">

        <div className="flex max-w-xl flex-col gap-10">

          <div>
            <h1 className="text-4xl font-bold leading-[1.1] tracking-tight text-white xl:text-5xl">
              Gestão inteligente
              <br />
              para sua <span className="text-[#e4bc34]">operação</span>
            </h1>

            <p className="mt-5 max-w-md text-[15px] leading-relaxed text-white/70">
              O AutoBombas centraliza o controle de equipamentos, processos e indicadores da sua empresa em uma única plataforma.
            </p>
          </div>

          {/* Features */}
          <div className="flex flex-col gap-3">
            {features.map((f) => (
              <div key={f} className="flex items-center gap-3">
                <div className="h-1.5 w-1.5 shrink-0 rounded-full bg-[#b1cd49]" />
                <span className="text-sm text-white/70">{f}</span>
              </div>
            ))}
          </div>

          {/* CTA */}
          <button
            type="button"
            className="group inline-flex w-fit items-center gap-2 text-sm font-semibold text-[#e4bc34] transition-all"
          >
            Saiba mais sobre a plataforma
            <ArrowRight
              size={14}
              className="transition-transform group-hover:translate-x-1"
            />
          </button>

        </div>

      </div>
    </div>
  );
}