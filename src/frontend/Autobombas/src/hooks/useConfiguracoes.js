import { http } from "@/api/api";
import { useEffect, useState, useCallback } from "react";

const BOMBA_ID = 1;

export function useConfiguracoes() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [erro, setErro] = useState(null);
  const [sucesso, setSucesso] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      const { data } = await http.get(`/bombas/${BOMBA_ID}`);
      setConfig(data);
      setErro(null);
    } catch (err) {
      setErro(err.response?.data?.detail ?? "Erro ao carregar configurações");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  async function salvar(campos) {
    setSaving(true);
    setSucesso(false);
    setErro(null);
    try {
      const { data } = await http.patch(`/bombas/${BOMBA_ID}/config`, campos);
      setConfig(data);
      setSucesso(true);
      setTimeout(() => setSucesso(false), 3000);
    } catch (err) {
      setErro(err.response?.data?.detail ?? "Erro ao salvar configurações");
    } finally {
      setSaving(false);
    }
  }

  return { config, loading, saving, erro, sucesso, salvar, recarregar: fetchConfig };
}
