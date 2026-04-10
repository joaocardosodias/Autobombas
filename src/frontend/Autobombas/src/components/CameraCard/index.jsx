import { Video, Circle, Wifi } from "lucide-react";
import { cn } from "@/lib/utils";

  const SESSION_ID = Date.now();

export function CameraCard({ name, feedUrl, location, status }) {
  const isOnline = status !== "offline";
  const finalSrc = feedUrl ? `${feedUrl}?t=${SESSION_ID}` : "";

  return (
    <div className="group relative bg-card rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 border border-primary/10">
      <div className="relative aspect-video bg-linear-to-br from-primary/5 to-primary/10">
        {feedUrl ? (
          <img
            src={finalSrc}
            alt={name}
            loading="lazy" // economizar banda devido ao limite do chrome
            crossOrigin="anonymous"
            className="absolute inset-0 w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Video className="w-8 h-8 text-primary/30 mx-auto mb-2" />
              <span className="text-xs text-muted-foreground">
                Feed ao vivo
              </span>
            </div>
          </div>
        )}

        {/* Hover de overlay */}
        <div className="absolute inset-0 bg-linear-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        {/* Badge de status */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-black/50 backdrop-blur-sm px-2 py-1 rounded-full">
          <Circle
            className={cn(
              "w-2 h-2 fill-current",
              status === "recording"
                ? "text-red-500 animate-pulse"
                : status === "online"
                  ? "text-green-500"
                  : "text-gray-400",
            )}
          />
          <span className="text-[10px] font-medium text-white uppercase tracking-wide">
            {status === "recording" ? "Rec" : status}
          </span>
        </div>
        {/* Icone de conexão */}
        <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm p-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
          <Wifi
            className={cn(
              "w-3 h-3",
              isOnline ? "text-green-400" : "text-gray-400",
            )}
          />
        </div>
        {/* rodapé */}
        <div className="absolute bottom-0 left-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <p className="text-white text-sm font-medium truncate">{name}</p>
          <p className="text-white/70 text-xs">{location}</p>
        </div>
      </div>
      {/* footer do card */}
      <div className="px-4 py-3 border-t border-primary/5 bg-card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-primary">{name}</p>
            <p className="text-xs text-muted-foreground">{location}</p>
          </div>
          <div
            className={cn(
              "text-xs font-medium px-2 py-1 rounded-full",
              isOnline
                ? "bg-green-500/10 text-green-600"
                : "bg-gray-500/10 text-gray-500",
            )}
          >
            {isOnline ? "Ativo" : "Inativo"}
          </div>
        </div>
      </div>
    </div>
  );
}
