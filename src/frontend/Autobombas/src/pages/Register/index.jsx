import { useEffect, useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { CreateUserDialog } from "@/components/CreateUserDialog";
import { useUsers } from "@/hooks/useUsers";
import { SideBar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatusIndicator } from "@/components/DashboardStatus";
import { SensorsPanel } from "@/components/SensorsPanel";
import { useDashboardMonitor } from "@/hooks/useDashboardMonitor";

export function Register() {
  const { 
    usuarios, 
    isLoading, 
    fetchUsuarios, 
    deletarUsuario, 
    criarUsuario 
  } = useUsers();

  const [isSensorOpen, setIsSensorOpen] = useState(false);
  const { sensorsList, isSystemOnline, lastUpdated, activeSensorsCount } = useDashboardMonitor();

  useEffect(() => {
    fetchUsuarios();
  }, [fetchUsuarios]);

  const handleClickClose = () => {
    setIsSensorOpen(false);
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      
      <SideBar
        onSensorsClick={() => setIsSensorOpen(true)}
        systemStatusCount={`${activeSensorsCount} sensores ativos`}
        isOnline={isSystemOnline}
      />

      <main className="flex-1 flex flex-col min-h-0">
        
        <DashboardHeader
          statusSlot={<StatusIndicator status={isSystemOnline ? "connected" : "disconnected"} />}
          title="Gerenciamento de Usuários"
        />

        <div className="flex-1 overflow-auto p-6">
          
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-primary">Usuários</h1>
              <p className="text-sm text-muted-foreground mt-1">Gerencie os acessos do sistema AutoBombas</p>
            </div>
            
            <CreateUserDialog criarUsuario={criarUsuario} isLoadingGlob={isLoading} />
          </div>

          {/* Tabela de Usuários */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-200 bg-slate-50/50">
              <h2 className="text-lg font-semibold text-slate-800">Lista de Usuários</h2>
              <p className="text-sm text-slate-500">Todos os usuários cadastrados no sistema</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-slate-500 bg-slate-50 uppercase border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-4 font-medium">Nome</th>
                    <th className="px-6 py-4 font-medium">Email</th>
                    <th className="px-6 py-4 font-medium">Função</th>
                    <th className="px-6 py-4 font-medium text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {isLoading && usuarios.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-8 text-center text-slate-500">
                        Carregando usuários...
                      </td>
                    </tr>
                  ) : usuarios.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-8 text-center text-slate-500">
                        Nenhum usuário encontrado.
                      </td>
                    </tr>
                  ) : (
                    usuarios.map((user) => (
                      <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-900">{user.nome}</td>
                        <td className="px-6 py-4 text-slate-500">{user.email}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                            user.role === 'gestor' 
                              ? 'bg-[#10381B]/10 text-[#10381B]' 
                              : 'bg-slate-100 text-slate-600'
                          }`}>
                            {user.role === 'gestor' ? 'Gestor' : 'Operador'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button 
                              className="p-2 text-slate-400 hover:text-primary transition-colors rounded-lg hover:bg-slate-100"
                              title="Editar (em breve)"
                            >
                              <Pencil size={16} />
                            </button>
                            <button 
                              onClick={() => deletarUsuario(user.id)}
                              className="p-2 text-slate-400 hover:text-red-600 transition-colors rounded-lg hover:bg-red-50"
                              title="Deletar"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <SensorsPanel
        isOpen={isSensorOpen}
        onClickClose={handleClickClose}
        sensors={sensorsList}
        lastUpdated={lastUpdated}
      />
    </div>
  );
}