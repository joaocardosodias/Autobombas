import { useEffect, useState } from "react";
import { Clock, Calendar } from "lucide-react"


export function DashboardHeader({ statusSlot, title }) {
    const [now, setNow] = useState(() => new Date())

    useEffect(() => {
        const id = setInterval(() => setNow(new Date()), 1000)
        return () => clearInterval(id)
    }, [])

      const timeString = now
    ? now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
    : "--:--"

  const dateString = now
    ? now.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" })
    : ""

    return (
        <header className="flex items-center justify-between px-6 py-4 bg-card/50 backdrop-blur-sm border-b border-primary/5 shrink-0">
            <div>
                <h1 className="text-xl font-bold text-primary">
                    {title}
                </h1>
                <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1.5">
                        <Clock size={14} />
                        {timeString}
                    </span>
                    {dateString && (
                        <span className="flex items-center gap-1.5 capitalize">
                            <Calendar size={14} />
                            {dateString}
                        </span>
                    )}
                </div>
            </div>
            {statusSlot && <div>{statusSlot}</div>}
        </header>
    )
}