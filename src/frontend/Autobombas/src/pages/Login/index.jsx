import { Zap } from "lucide-react";
import { LoginVisual } from "../../components/LoginPainel";
import { LoginForm } from "../../components/Form";

export function Login() {

  return (
    <main className="flex h-dvh w-full bg-[#111b14]">

      {/* Painel esquerdo */}
      <div className="hidden shrink-0 lg:flex lg:w-[60%]">
        <LoginVisual />
      </div>

      {/* Lado direito  */}
      <div className="flex flex-1 flex-col ">

        {/* Header mobile */}
        <div className="flex items-center border-b border-white/7 px-6 py-4 lg:hidden">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#1e4d2b]">
              <Zap size={16} color="#e4bc34" />
            </div>
            <span className="text-base font-bold text-white">Itubombas</span>
          </div>
        </div>

        {/* Área central */}
        <div className="flex flex-1 flex-col items-center justify-center p-10 sm:px-12 lg:px-16 mb-20">
          <div className="w-full max-w-md">

            {/* Logo */}
            <div className="items-center gap-3 ">
                <img
                    src="/Autobombas-v4.png"
                    alt="AutoBombas"
                    className="h-auto w-auto -ml-10"
                    />
            </div>

            {/* Título */}
            <div className="mb-10">
              <h2 className="text-3xl font-bold tracking-tight text-white">
                Bem-vindo de volta
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-white/45">
                Acesse sua conta para gerenciar suas operações e equipamentos
              </p>
            </div>

            <LoginForm />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-white/7 px-6 py-4">
          <span className="text-xs text-white/25">
            © AutoBombas {new Date().getFullYear()}
          </span>
          <div className="flex items-center gap-1.5">
          </div>
        </div>
      </div>
    </main>
  );
}