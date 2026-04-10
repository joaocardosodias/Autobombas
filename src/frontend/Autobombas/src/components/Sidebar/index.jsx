import {
  LayoutDashboard,
  Settings,
  Cpu,
  LogOut,
  Info,
  UserPlus,
  ChartColumn
} from "lucide-react";
import { cn } from "@/lib/utils";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

export function SideBar({
  isOnline,
  systemStatusCount,
}) {
  const navLinkClass = ({ isActive }) =>
    cn(
      "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
      isActive
        ? "bg-[#10381B] text-primary-foreground shadow-md"
        : "text-primary hover:bg-primary/10 border border-transparent hover:border-primary/20",
    );

  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const onLogout = () => {
    logout();
    navigate("/auth/login");
  };

  return (
    <aside className="flex flex-col h-full bg-secondary/80 backdrop-blur-sm border-r border-primary/10 w-56 shadow-lg shrink-0">
      {/* Logo */}
      <div className="flex items-center justify-center p-6 border-b border-primary/10">
        <img
          src="/autobombas-logo 3-sem-fundo.png"
          alt="AutoBombas"
          className="h-auto w-auto "
        />
      </div>
      {/* Navegação */}
      <nav className="flex-1 p-4">
        <div className="space-y-1">
          <NavLink to="/dashboard" end className={navLinkClass}>
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink to="/sobre" className={navLinkClass}>
            <Info size={18} />
            <span>Sobre o Sistema</span>
          </NavLink>
          <NavLink to="/sensores" className={navLinkClass}>
            <Cpu size={18} />
            <span>Sensores</span>
          </NavLink>
          <NavLink to="/configuracoes" className={navLinkClass}>
            <Settings size={18} />
            <span>Configurações</span>
          </NavLink>

          {user?.role === "gestor" && (
            <NavLink to="/criar-user" className={navLinkClass}>
              <UserPlus size={18}/>
              <span>Criar Usuário</span>
            </NavLink>
          )}
          {user?.role === "gestor" && (
            <NavLink to="/gestor" className={navLinkClass}>
              <ChartColumn size={18} />
              <span>Painel do Gestor</span>
            </NavLink>
          )}
        </div>
      </nav>
      {/* Status do sistema */}
      <div className="p-4 border-t border-primary/10">
        <div className="bg-primary/5 rounded-xl p-3 mb-4">
          <div className="flex items-center gap-2 mb-1">
            <div
              className={cn(
                "w-2 h-2 rounded-full",
                isOnline ? "bg-green-500 animate-pulse" : "bg-red-500",
              )}
            />
            <span className="text-xs font-medium text-primary">
              Sistema Operacional
            </span>
          </div>
          <div className="text-xs text-muted-foreground">
            {systemStatusCount}
          </div>
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-primary hover:bg-destructive/10 hover:text-destructive border border-transparent hover:border-destructive/20 transition-all duration-200"
          >
            <LogOut size={18} />
            <span>Sair</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
