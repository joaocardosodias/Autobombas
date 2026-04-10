import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Login } from "../pages/Login";
import { Dashboard } from "@/pages/Dashboard";
import About from "@/pages/About";
import Configuracoes from "@/pages/Configuracoes";
import Sensores from "@/pages/Sensores";
import { RotaGestor } from "@/components/RotaGestor";
import { Register } from "@/pages/Register";
import { DashGestorSessions } from "@/pages/DashGestorSessions";
import { DashGestor } from "@/pages/DashGestor";

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/auth/login"/>} />
        <Route path="/auth/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />}/>
        <Route path="/sobre" element={<About />}/>
        <Route path="/configuracoes" element={<Configuracoes />}/>
        <Route path="/sensores" element={<Sensores />}/>
        <Route element={<RotaGestor />} >
        <Route path="/criar-user" element={<Register />} />
        <Route path="/gestor" element={<DashGestor />} />
        <Route path="/gestor/sessoes/:id" element={<DashGestorSessions />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
