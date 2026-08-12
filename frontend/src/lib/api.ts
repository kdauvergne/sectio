import axios from "axios";

/** Client HTTP unique de l'application */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

/** Avant chaque requête, on attache le jeton d'authentification s'il existe. */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sectio_access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
