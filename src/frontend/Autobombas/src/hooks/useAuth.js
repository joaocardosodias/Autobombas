import { useState } from "react";
import { http } from "../api/api";


function getStoredUser() {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
}
export const useAuth = () => {
    const [user, setUser] = useState(getStoredUser);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    async function login(email, senha) {
        setIsLoading(true);
        setError(null);

        try {
            const { data } = await http.post("/auth/login", {
                email,
                senha,
            });
            const userData = {
                id: data.usuario_id,
                nome: data.nome,
                role: data.role,
                token: data.token,
            };

            localStorage.setItem("user", JSON.stringify(userData));
            setUser(userData);
            return userData;
        } catch(error) {
            setError(error.response?.data?.detail || "Erro ao fazer login");
        } finally {
            setIsLoading(false);
        }
    }

    function logout() {
        localStorage.removeItem("user");
        setUser(null);
    }

    return {
        user,
        login,
        logout,
        isLoading,
        error
    }


}