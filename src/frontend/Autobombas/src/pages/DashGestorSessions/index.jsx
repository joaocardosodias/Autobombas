import { useParams, Link } from "react-router-dom";
import {
    AlertTriangle,
    CalendarDays,
    Filter,
    Flag,
    Timer,
    TrendingUp,
    User,
    ArrowLeft,
    Clock3,
} from "lucide-react";
import { SideBar } from "@/components/Sidebar";
import { useGestorSession } from "@/hooks/useGestorSession";

function getStatusClass(status) {
    if (status === "Finalizada") return "bg-emerald-100 text-emerald-700";
    if (status === "Em Andamento") return "bg-blue-100 text-blue-700";
    return "bg-red-100 text-red-700";
}

function getAlertTagClass(tag) {
    if (tag === "Crítico") return "bg-red-100 text-red-700";
    if (tag === "Atenção") return "bg-amber-100 text-amber-700";
    return "bg-emerald-100 text-emerald-700";
}

function getPhaseColor(tone) {
    if (tone === "search") return "bg-[#0f4a35]";
    if (tone === "mid") return "bg-[#f4a000]";
    return "bg-[#738a82]";
}

function padSession(sessionNumber) {
    return String(sessionNumber || 0).padStart(3, "0")
}

export function DashGestorSessions() {
    const { id } = useParams();

    const { session, phases, cardsError, isLoading} = useGestorSession(id)

    if (isLoading) return <p className="p-6">Carregando detalhes da operação...</p>
    if (!session) return <p className="p-6 text-red-600">Sessão não encontrada</p>
   
    return (
<div className="flex h-screen bg-background overflow-hidden">
            <SideBar systemStatusCount="" />

            <main className="flex-1 min-h-0 overflow-y-auto p-6">
                
                <header className="mb-6">
                    <div className="flex items-start justify-between gap-4">
                        <div>
                            <Link
                                to="/gestor"
                                className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-2"
                            >
                                <ArrowLeft size={16} />
                                Voltar para Gestão
                            </Link>

                            <h1 className="mt-3 text-3xl font-bold text-primary tracking-tight">
                                Sessão #{padSession(session.sessionNumber)}
                            </h1>
                            <p className="text-sm text-muted-foreground">Detalhes da operação</p>

                            <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                                <span className="inline-flex items-center gap-1">
                                    <Clock3 size={14} />
                                    {session.operationTime}
                                </span>
                                <span className="inline-flex items-center gap-1 capitalize">
                                    <CalendarDays size={14} />
                                    {session.operationDayMonth}
                                </span>
                            </div>
                        </div>
                    </div>
                </header>

                {cardsError ? <p className="mb-3 text-sm text-red-600">{cardsError}</p> : null}

                <div className="bg-card rounded-2xl border border-primary/10 p-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                        <div className="rounded-xl border border-primary/10 bg-background/50 p-4">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <CalendarDays size={16} />
                                <span className="text-sm font-medium">Data</span>
                            </div>
                            <div className="mt-2 text-xl font-semibold text-foreground">{session.operationDate}</div>
                        </div>

                        <div className="rounded-xl border border-primary/10 bg-background/50 p-4">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <User size={16} />
                                <span className="text-sm font-medium">Operador</span>
                            </div>
                            <div className="mt-2 text-xl font-semibold text-foreground truncate">
                                {session.operator}
                            </div>
                        </div>

                        <div className="rounded-xl border border-primary/10 bg-background/50 p-4">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Timer size={16} />
                                <span className="text-sm font-medium">Duração</span>
                            </div>
                            <div className="mt-2 text-xl font-semibold text-foreground">{session.duration}</div>
                        </div>

                        <div className="rounded-xl border border-primary/10 bg-background/50 p-4">
                            <div className="flex items-center gap-2 text-muted-foreground">
                                <Flag size={16} />
                                <span className="text-sm font-medium">Status</span>
                            </div>
                            <div className="mt-2">
                                <span
                                    className={`inline-flex rounded-md px-3 py-1 text-xs font-semibold ${getStatusClass(
                                        session.status,
                                    )}`}
                                >
                                    {session.status}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <section className="rounded-xl border border-primary/10 bg-background/30 p-4">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2 text-primary">
                                    <AlertTriangle size={16} />
                                    <h2 className="text-lg font-semibold">Histórico de Alertas</h2>
                                </div>
                                <button className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground">
                                    <Filter size={14} />
                                    Filtrar
                                </button>
                            </div>

                            <div className="space-y-3">
                                {session.alerts.length === 0 ? (
                                    <p className="text-sm text-muted-foreground py-2">Nenhum alerta registrado nesta sessão.</p>
                                ) : (
                                    session.alerts.map((alert, index) => (
                                        <div
                                            key={`${alert.time}-${index}`}
                                            className="rounded-lg border border-primary/10 bg-card/60 px-3 py-2"
                                        >
                                            <div className="flex items-center justify-between gap-3">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-sm text-muted-foreground min-w-10.5">
                                                        {alert.time}
                                                    </span>
                                                    <div>
                                                        <div className="text-base font-semibold text-foreground">
                                                            {alert.title}
                                                        </div>
                                                        <div className="text-sm text-muted-foreground">
                                                            {alert.percent}%
                                                        </div>
                                                    </div>
                                                </div>
                                                <span
                                                    className={`inline-flex rounded-md px-2 py-1 text-xs font-semibold ${getAlertTagClass(
                                                        alert.tag,
                                                    )}`}
                                                >
                                                    {alert.tag}
                                                </span>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </section>

                        <section className="rounded-xl border border-primary/10 bg-background/30 p-4">
                            <div className="flex items-center gap-2 text-primary mb-4">
                                <TrendingUp size={16} />
                                <h2 className="text-lg font-semibold">Fases da Operação</h2>
                            </div>

                            <div className="space-y-5">
                                {phases.length === 0 ? (
                                    <p className="text-sm text-muted-foreground py-2">Sem dados de fases para esta sessão.</p>
                                ) : (
                                    phases.map((phase) => (
                                        <div key={phase.label}>
                                            <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                                                <span>{phase.label}</span>
                                                <span>{Math.round(phase.percent)}% do tempo</span>
                                            </div>
                                            <div className="h-11 w-full rounded-xl bg-muted/60 relative overflow-hidden">
                                                <div
                                                    className={`absolute top-0 h-11 ${getPhaseColor(phase.tone)}`}
                                                    style={{ left: `${phase.left}%`, width: `${phase.width}%` }}
                                                >
                                                    <span className="h-full w-full inline-flex items-center justify-center text-sm font-semibold text-white">
                                                        {Math.round(phase.percent)}%
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>

                            <div className="mt-6">
                                <h3 className="text-base font-semibold text-foreground mb-2">
                                    Linha do Tempo Completa
                                </h3>
                                <div className="h-8 w-full rounded-xl overflow-hidden bg-muted/60 flex">
                                    {phases.map((phase) => (
                                        <div
                                            key={`timeline-${phase.label}`}
                                            className={`${getPhaseColor(
                                                phase.tone,
                                            )} h-8 inline-flex items-center justify-center text-xs font-semibold text-white`}
                                            style={{ width: `${phase.width}%` }}
                                        >
                                            {phase.label}
                                        </div>
                                    ))}
                                </div>

                                <div className="mt-2 flex items-center justify-between text-sm text-muted-foreground">
                                    <span>{session.timelineStart}</span>
                                    <span>{session.timelineEnd}</span>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>
            </main>
        </div>
    );
}

