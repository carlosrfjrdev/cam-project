const BASE_URL = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),

  uploadFile: async <T>(path: string, file: File): Promise<T> => {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch(`${BASE_URL}${path}`, { method: "POST", body: form });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail ?? `HTTP ${response.status}`);
    }
    return response.json() as Promise<T>;
  },

  // Multipart genérico: vários arquivos + campos de formulário (Trade/Operation Analyzer).
  uploadForm: async <T>(
    path: string,
    files: Record<string, File | null | undefined>,
    fields?: Record<string, string | number>,
  ): Promise<T> => {
    const form = new FormData();
    for (const [k, f] of Object.entries(files)) {
      if (f) form.append(k, f);
    }
    for (const [k, v] of Object.entries(fields ?? {})) {
      form.append(k, String(v));
    }
    const response = await fetch(`${BASE_URL}${path}`, { method: "POST", body: form });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.error ?? error.detail ?? `HTTP ${response.status}`);
    }
    return response.json() as Promise<T>;
  },
};
