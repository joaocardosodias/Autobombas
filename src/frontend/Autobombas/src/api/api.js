import axios from "axios";

export const http = axios.create({
  baseURL: "http://localhost:5000",
  headers: {
    "Content-Type": "application/json",
  },
});

http.interceptors.request.use(function (config) {
  const stored = localStorage.getItem("user");
  if (stored) {
    const user = JSON.parse(stored);
    config.headers.Authorization = `Bearer ${user.token}`
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;

    if (status === 401) {
      localStorage.clear();
      window.location.href = "/auth/login";
    }

    if (status === 500) {
      console.error("Erro interno no servidor", error.response?.data);
    }
    return Promise.reject(error);
  },
);
