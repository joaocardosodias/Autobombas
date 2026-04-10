import { http } from "@/api/api";
import { useCallback, useState } from "react";

export const useUsers = () => {
const [usuarios, setUsuarios] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchUsuarios = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
        const { data } = await http.get("/usuarios");
        setUsuarios(data);
    } catch (err) {
      const msgErro = err.response?.data?.detail || "Erro ao carregar lista de usuários";
      setError(msgErro);
      alert(msgErro)
    } finally {
      setIsLoading(false);
    }
  }, []);

  const criarUsuario = async (dadosUsuario) => {
    setIsLoading(true);
    setError(null);
    try {
      await http.post("/usuarios", dadosUsuario);
      await fetchUsuarios();
      alert("Usuário criado com sucesso")
      return {success: true};
    } catch (err) {
      const msgErro = err.response?.data?.detail || "Erro ao criar usuário.";
      setError(msgErro);
      return { success: false, error: msgErro}
    } finally {
      setIsLoading(false);
    }
  };

  const deletarUsuario = async (id) => {
    if (!window.confirm("Tem certeza que deseja excluir este usuário?")) return;

    setIsLoading(true);
    setError(null);
    try {
      await http.delete(`/usuarios/${id}`);
      alert("Usuário removido com sucesso")
      await fetchUsuarios()
    } catch (err) {
      const msgErro = err.response?.data?.detail || "Erro ao deletar usuário";
      setError(msgErro);
      alert(msgErro);
    } finally {
      setIsLoading(false);
    }
  };

  return {usuarios, isLoading, error, fetchUsuarios, criarUsuario, deletarUsuario};
};