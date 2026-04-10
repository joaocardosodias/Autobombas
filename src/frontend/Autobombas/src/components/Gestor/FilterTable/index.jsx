export function FilterCard({
    bombas = [],
    selectedBombaId = "all",
    onBombaChange = () => {},
    selectedStatus = "all",
    onStatusChange = () => {},
}) {
    return (
        <div data-slot="card" className="bg-card text-card-foreground flex flex-col gap-6 rounded-xl py-6 mb-6 border-0 shadow-sm">
            <div data-slot="card-content" className="px-6 py-4">
                <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
                    <div className="flex items-center gap-2 text-muted-foreground">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4" aria-hidden="true">
                            <path d="M10 20a1 1 0 0 0 .553.895l2 1A1 1 0 0 0 14 21v-7a2 2 0 0 1 .517-1.341L21.74 4.67A1 1 0 0 0 21 3H3a1 1 0 0 0-.742 1.67l7.225 7.989A2 2 0 0 1 10 14z"></path>
                        </svg>
                        <span className="text-sm font-medium">Filtros</span>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 flex-1">
                        <select
                            value={selectedBombaId}
                            onChange={(e) => onBombaChange(e.target.value)}
                            className="rounded-md px-3 py-2 text-sm h-9 w-full sm:w-40 bg-muted/50 border-2 outline-none"
                        >
                            <option value="all">Todos</option>
                            {bombas.map((b) => (
                                <option key={b.id} value={String(b.id)}>
                                    {b.nome}
                                </option>
                            ))}
                        </select>
                        <select
                            value={selectedStatus}
                            onChange={(e) => onStatusChange(e.target.value)}
                            className="rounded-md px-3 py-2 text-sm h-9 w-full sm:w-40 bg-muted/50 border-2 outline-none"
                        >
                            <option value="all">Todas</option>
                            <option value="Em Andamento">Em Andamento</option>
                            <option value="Finalizada">Finalizada</option>
                            <option value="Alerta">Alerta</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
}