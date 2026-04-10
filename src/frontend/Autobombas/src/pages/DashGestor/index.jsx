import { SideBar } from "@/components/Sidebar";
import { FilterCard } from "@/components/Gestor/FilterTable";
import { SessionsTable } from "@/components/Gestor/SessionsTable";
import { useGestor } from "@/hooks/useGestor";
import { DashboardHeader } from "@/components/DashboardHeader";

export function DashGestor() {
    const {
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
    } = useGestor();

    return (
        <div className="flex h-screen bg-background overflow-hidden">
            <SideBar />
            <main className="flex-1 flex flex-col min-h-0 overflow-y-auto">
                <DashboardHeader title="Dashboard de Gestão"/>
                <div className="flex-1 p-6">
                    <FilterCard
                        bombas={bombas}
                        selectedBombaId={selectedBombaId}
                        onBombaChange={setSelectedBombaId}
                        selectedStatus={selectedStatus}
                        onStatusChange={setSelectedStatus}
                    />
                    {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
                    {isLoading ? (
                        <p className="mt-3 text-sm text-muted-foreground">Carregando sessoes...</p>
                    ) : (
                        <SessionsTable
                            sessions={sessions}
                            total={total}
                            currentPage={currentPage}
                            totalPages={totalPages}
                            pageSize={pageSize}
                            onPageChange={onPageChange}
                        />
                    )}
                </div>
            </main>
        </div>
    );
}