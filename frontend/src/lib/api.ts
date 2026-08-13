import axios from "axios";
import type { AxiosError, InternalAxiosRequestConfig } from "axios";
import {
  deleteTokens,
  saveTokens,
  getAccessToken,
  getRefreshToken,
} from "./tokens";

export const API_URL = import.meta.env.VITE_API_URL;

/** Client HTTP unique de l'application */
export const api = axios.create({
  baseURL: API_URL,
});

/** Avant chaque requête, on attache le jeton d'authentification s'il existe. */
api.interceptors.request.use((config) => {
  const accessToken = getAccessToken();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

/** Config Axios */

type RetriableRequest = InternalAxiosRequestConfig & { _retry?: boolean };

let refreshPromise: Promise<string> | null = null;

async function refreshAccessTokens(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error("Aucun jeton de rafraîchissement disponible.");
  }

  const response = await axios.post(`${API_URL}/token/refresh/`, {
    refresh: refreshToken,
  });
  saveTokens(response.data.access, response.data.refresh);
  return response.data.access;
}

api.interceptors.response.use(
  (response) => response,
  async (erreur: AxiosError) => {
    const requete = erreur.config as RetriableRequest | undefined;

    if (erreur.response?.status !== 401 || !requete || requete._retry) {
      return Promise.reject(erreur);
    }
    requete._retry = true;

    try {
      refreshPromise ??= refreshAccessTokens();
      const newAccess = await refreshPromise;
      requete.headers.Authorization = `Bearer ${newAccess}`;
      return api(requete);
    } catch (echec) {
      deleteTokens();
      window.location.href = "/connexion"; // PROVISOIRE
      return Promise.reject(echec);
    } finally {
      refreshPromise = null;
    }
  },
);
