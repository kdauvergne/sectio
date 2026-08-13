const CLE_ACCESS = "sectio_access";
const CLE_REFRESH = "sectio_refresh";

export function getAccessToken(): string | null {
  return localStorage.getItem(CLE_ACCESS);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(CLE_REFRESH);
}

export function saveTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(CLE_ACCESS, accessToken);
  localStorage.setItem(CLE_REFRESH, refreshToken);
}

export function deleteTokens(): void {
  localStorage.removeItem(CLE_ACCESS);
  localStorage.removeItem(CLE_REFRESH);
}
