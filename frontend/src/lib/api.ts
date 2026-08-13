import axios from "axios";
import type { AxiosError, InternalAxiosRequestConfig } from "axios";

export const URL_API = import.meta.env.VITE_API_URL;

const config = {
  baseURL: URL_API,
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
};

export const api = axios.create(config);

export const publicApi = axios.create(config);

let onSessionExpired: (() => void) | null = null;

/** Callback declenché quand la session est definitivement perdue */
export function setOnSessionExpired(callback: () => void): void {
  onSessionExpired = callback;
}

type RetriableRequest = InternalAxiosRequestConfig & { _retry?: boolean };

let refreshPromise: Promise<void> | null = null;

async function refreshSession(): Promise<void> {
  await publicApi.post("/token/refresh/");
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequest | undefined;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry
    ) {
      return Promise.reject(error);
    }
    originalRequest._retry = true;

    try {
      refreshPromise ??= refreshSession();
      await refreshPromise;
      return api(originalRequest);
    } catch (refreshError) {
      onSessionExpired?.();
      return Promise.reject(refreshError);
    } finally {
      refreshPromise = null;
    }
  },
);
