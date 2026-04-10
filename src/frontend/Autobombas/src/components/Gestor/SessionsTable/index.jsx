import React from "react";
import { Link } from "react-router-dom";

const statusStyles = {
    Finalizada: "bg-emerald-100 text-emerald-700",
    "Em Andamento": "bg-blue-100 text-blue-700",
    Alerta: "bg-red-100 text-red-700",
};

export function SessionsTable({
    sessions = [],
    total = 0,
    currentPage = 1,
    totalPages = 1,
    pageSize = 10,
    onPageChange = () => {},
}) {
    const from = total > 0 ? (currentPage - 1) * pageSize + 1 : 0;
    const to = total > 0 ? Math.min(currentPage * pageSize, total) : 0;
    return (
        <div data-slot="card" className="bg-card text-card-foreground flex flex-col gap-6 rounded-xl py-6 border-0 shadow-sm">
            <div data-slot="card-header" className="px-6 pb-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="text-lg font-semibold">Histórico de Sessões</div>
                </div>
            </div>
            <div data-slot="card-content" className="px-6 overflow-x-auto">
                <table className="w-full caption-bottom text-sm min-w-150">
                    <thead>
                        <tr className="border-b border-muted">
                            <th className="h-10 px-2 text-left align-middle text-muted-foreground font-medium">Sessão</th>
                            <th className="h-10 px-2 text-left align-middle text-muted-foreground font-medium">Início</th>
                            <th className="h-10 px-2 text-left align-middle text-muted-foreground font-medium">Fim</th>
                            <th className="h-10 px-2 text-left align-middle text-muted-foreground font-medium">Operador</th>
                            <th className="h-10 px-2 text-left align-middle text-muted-foreground font-medium">Status</th>
                            <th className="h-10 px-2 text-right align-middle text-muted-foreground font-medium">Ação</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sessions.map((session) => (
                            <tr key={session.id} className="hover:bg-muted/50 border-b border-muted transition-colors">
                                <td className="p-2 align-middle font-medium">#{String(session.id).padStart(3, "0")}</td>
                                <td className="p-2 align-middle">{session.inicio}</td>
                                <td className="p-2 align-middle">{session.fim}</td>
                                <td className="p-2 align-middle truncate max-w-30">{session.operador}</td>
                                <td className="p-2 align-middle">
                                    <span
                                        className={`inline-flex items-center justify-center rounded-md px-2 py-0.5 text-xs font-medium ${
                                            statusStyles[session.status] ||
                                            "bg-muted text-muted-foreground"
                                        }`}
                                    >
                                        {session.status}
                                    </span>
                                </td>
                                <td className="p-2 align-middle text-right">
                                    <Link to={`/gestor/sessoes/${session.id}`}>
                                        <button className="inline-flex items-center justify-center text-sm font-bold h-8 rounded-md px-3 text-primary hover:bg-primary/10">
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                width="16"
                                                height="16"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="2"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                className="h-4 w-4 mr-1"
                                                aria-hidden="true"
                                            >
                                                <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path>
                                                <circle cx="12" cy="12" r="3"></circle>
                                            </svg>
                                            <span className="hidden sm:inline">Detalhar</span>
                                        </button>
                                    </Link>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* Paginação */}
                <div className="mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <p className="text-sm text-muted-foreground">
                        Mostrando {from} a {to} de {total} sessões
                    </p>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => onPageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                            className="inline-flex items-center justify-center text-sm font-medium h-8 rounded-md px-3 border border-border bg-background hover:bg-accent disabled:opacity-50 disabled:pointer-events-none gap-1"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="h-4 w-4"
                            >
                                <path d="m15 18-6-6 6-6"></path>
                            </svg>
                            <span className="hidden sm:inline">Anterior</span>
                        </button>
                        <div className="flex items-center gap-1">
                            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                                <button
                                    key={page}
                                    onClick={() => onPageChange(page)}
                                    className={`inline-flex items-center justify-center text-sm font-medium h-8 rounded-md px-3 min-w-9 ${
                                        page === currentPage
                                            ? "bg-primary text-primary-foreground hover:bg-primary/90"
                                            : "border border-border bg-background hover:bg-accent"
                                    }`}
                                >
                                    {page}
                                </button>
                            ))}
                        </div>
                        <button
                            onClick={() => onPageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                            className="inline-flex items-center justify-center text-sm font-medium h-8 rounded-md px-3 border border-border bg-background hover:bg-accent disabled:opacity-50 disabled:pointer-events-none gap-1"
                        >
                            <span className="hidden sm:inline">Próximo</span>
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="h-4 w-4"
                            >
                                <path d="m9 18 6-6-6-6"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}