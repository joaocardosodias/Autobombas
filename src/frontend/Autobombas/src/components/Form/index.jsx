import { Eye, EyeOff, Loader2, LogIn, Mail, Lock } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { useNavigate } from "react-router-dom";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault(); // isso previne a página recarregar após ser submetido, isso vem do html puro ai com essa função eu cancelo isso
    const data = await login(email, pass);

    if (data) {
      navigate("/dashboard");
    }
  };

  const handleChangeMail = (e) => {
    setEmail(e.target.value);
  };

  const handleChangePass = (e) => {
    setPass(e.target.value);
  };

  const handleClick = () => {
    setShowPassword(!showPassword);
  };

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-5">
      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Email */}
      <div className="flex flex-col gap-1.5">
        <label htmlFor="email" className="text-sm font-medium text-white/70">
          E-mail
        </label>
        <div className="relative">
          <Mail
            className="absolute left-3 top-1/2 -translate-y-1/2 text-white/35 pointer-events-none"
            size={16}
          />
          <input
            id="email"
            type="email"
            value={email}
            placeholder="seu@email.com"
            onChange={handleChangeMail}
            required
            className="h-12 w-full rounded-xl border border-white/10 bg-white/5 pl-10 pr-4 text-sm text-white placeholder:text-white/30 outline-none transition-colors focus:border-[#e4bc34]"
          />
        </div>
      </div>

      {/* Senha */}
      <div className="flex flex-col gap-1.5">
        <label htmlFor="password" className="text-sm font-medium text-white/70">
          Senha
        </label>
        <div className="relative">
          <Lock
            className="absolute left-3 top-1/2 -translate-y-1/2 text-white/35 pointer-events-none"
            size={16}
          />
          <input
            id="password"
            type={showPassword ? "text" : "password"}
            value={pass}
            placeholder="Digite sua senha"
            onChange={handleChangePass}
            required
            className="h-12 w-full rounded-xl border border-white/10 bg-white/5 pl-10 pr-12 text-sm text-white placeholder:text-white/30 outline-none transition-colors focus:border-[#e4bc34]"
          />
          <button
            type="button"
            onClick={handleClick}
            aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-white/35 hover:text-white/70 transition-colors"
          >
            {showPassword ? <Eye size={16} /> : <EyeOff size={16} />}
          </button>
        </div>
      </div>
      {/* Submit */}
      <button
        type="submit"
        disabled={isLoading}
        className="mt-1 flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#1e4d2b] text-sm font-semibold text-white transition-all hover:bg-[#163820] hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Entrando...
          </>
        ) : (
          <>
            <LogIn size={16} />
            Entrar na plataforma
          </>
        )}
      </button>
    </form>
  );
}
