import { useAuth } from "@/hooks/useAuth";
import { Navigate, Outlet} from "react-router-dom";

export function RotaGestor() {
    const { user } = useAuth()

    if (!user || user.role !== "gestor") {
        return <Navigate to="/dashboard" replace />
    }

    return <Outlet />
}