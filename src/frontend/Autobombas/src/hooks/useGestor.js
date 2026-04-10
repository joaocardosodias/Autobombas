import { useEffect, useState } from "react";
import { http } from "../api/api";

function formatDateTimePtBR(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

export const useGestor = () => {
    const pageSize = 10;

    const [currentPage, setCurrentPage] = useState(1);
    const [selectedBombaId, setSelectedBombaId] = useState("all");
    const [selectedStatus, setSelectedStatus] = useState("all");

    const [bombas, setBombas] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Reseta a paginação ao mudar os filtros
    useEffect(() => {
        setCurrentPage(1);
    }, [selectedBombaId, selectedStatus]);

    // Carrega a lista de bombas
    useEffect(() => {
        let active = true;

        async function carregarBombas() {
            try {
                const { data } = await http.get("/bombas");
                if (active) setBombas(data || []);
            } catch (err) {
                if (active) {
                    console.error("Erro ao carregar bombas:", err);
                    setError("Nao foi possivel carregar as bombas.");
                }
            }
        }

        carregarBombas();
        return () => { active = false; };
    }, []);


    useEffect(() => {
        let active = true;

        async function carregarSessoes() {
            setIsLoading(true);
            setError(null);

            try {
                const params = { page: currentPage, page_size: pageSize };
                if (selectedBombaId !== "all") params.bomba_id = Number(selectedBombaId);

                if (selectedStatus !== "all") params.status = selectedStatus;


                const { data } = await http.get("/gestao/atividades", { params });

                if (!active) return;


                const normalized = (data.items || []).map((atividade) => ({
                    ...atividade,
                    inicio: formatDateTimePtBR(atividade.timestamp), 

                    fim: "-", 
                }));

                setSessions(normalized);
                setTotal(data.total ?? 0);
                setTotalPages(data.total_pages ?? 1);
            } catch (err) {
                if (!active) return;
                console.error("Erro ao carregar atividades:", err);
                setError("Nao foi possivel carregar as atividades.");
                setSessions([]);
                setTotal(0);
                setTotalPages(1);
            } finally {
                if (active) setIsLoading(false);
            }
        }

        carregarSessoes();
        return () => { active = false; };
    }, [currentPage, selectedBombaId, selectedStatus, pageSize]);

    function onPageChange(page) {
        const clampedPage = Math.max(1, Math.min(page, totalPages));
        setCurrentPage(clampedPage);
    }

    return {
        bombas,
        sessions,
        total,
        currentPage,
        totalPages,
        pageSize,
        selectedBombaId,
        selectedStatus,
        setSelectedBombaId,
        setSelectedStatus,
        onPageChange,
        isLoading,
        error,
    };
};