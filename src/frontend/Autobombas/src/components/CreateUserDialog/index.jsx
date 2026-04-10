import { Plus, X } from "lucide-react";
import { useState } from "react";

export function CreateUserDialog({ criarUsuario, isLoadingGlob }) {
  const [isOpen, setIsOpen] = useState(false);
  const [erroForm, setErroForm] = useState("");

  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [role, setRole] = useState("operador");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErroForm("");

    const res = await criarUsuario({ nome, email, senha, role });

    if (res.success) {
      setNome("");
      setEmail("");
      setSenha("");
      setRole("operador");
      setIsOpen(false);
    } else {
      setErroForm(res.error);
    }
  };

  const handleClickCreate = () => {
    setIsOpen(true);
  };

  const handleClick = () => {
    setIsOpen(false)
  }
  const handleChangeName = (e) => setNome(e.target.value)
  

  const handleChangeEmail = (e) => setEmail(e.target.value)

  const handleChangePass = (e) => setSenha(e.target.value)

  const handleChangeRole = (e) => setRole(e.target.value)

  return (
    <>
      <button
        onClick={handleClickCreate}
        className="flex items-center gap-2 bg-[#10381B] hover:bg-[#10381B]/90 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        <Plus size={16} />
        Novo Usuário
      </button>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-lg w-full max-w-md overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-semibold text-slate-800">
                  Criar Novo Usuário
                </h2>
                <p className="text-sm text-slate-500">
                  Adicione um novo usuário ao sistema.
                </p>
              </div>
              <button onClick={handleClick} className="text-slate-400 hover:text-slate-600 transition-colors">
                    <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
                {erroForm && (
                    <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">
                  {erroForm}
                </div>
                )}
                <div className="space-y-1">
                    <label className="text-sm font-medium text-slate-700">Nome *</label>
                    <input
                    required
                    type="text"
                    value={nome}
                    onChange={handleChangeName}
                    placeholder="Nome Completo"
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#10381B]/20 focus:border-[#10381B] text-sm"
                    disabled={isLoadingGlob}
                    />
                </div>
                <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Email *</label>
                <input 
                  required 
                  type="email" 
                  value={email} 
                  onChange={handleChangeEmail} 
                  placeholder="email@exemplo.com" 
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#10381B]/20 focus:border-[#10381B] text-sm" 
                  disabled={isLoadingGlob} 
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Senha *</label>
                <input 
                  required 
                  type="password" 
                  value={senha} 
                  onChange={handleChangePass} 
                  placeholder="Mínimo 6 caracteres" 
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#10381B]/20 focus:border-[#10381B] text-sm" 
                  disabled={isLoadingGlob} 
                  minLength={6}
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Função *</label>
                <select 
                  value={role} 
                  onChange={handleChangeRole} 
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#10381B]/20 focus:border-[#10381B] text-sm bg-white" 
                  disabled={isLoadingGlob}
                >
                  <option value="operador">Operador</option>
                  <option value="gestor">Gestor</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button 
                  type="button" 
                  onClick={() => setIsOpen(false)} 
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors" 
                  disabled={isLoadingGlob}
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 text-sm font-medium text-white bg-[#10381B] hover:bg-[#10381B]/90 rounded-lg transition-colors" 
                  disabled={isLoadingGlob}
                >
                  {isLoadingGlob ? "Processando..." : "Criar Usuário"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
