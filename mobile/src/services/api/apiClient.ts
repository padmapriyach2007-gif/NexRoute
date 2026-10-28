/**
 * Typed REST API Client communicating with FastAPI Backend
 * Fallback to configured LAN or cloud endpoint with graceful timeout handling.
 */

const DEFAULT_TIMEOUT_MS = 8000;

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    // Read from Expo environment or fallback to standard Android emulator loopback / LAN
    const envUrl = process.env.EXPO_PUBLIC_API_BASE_URL;
    this.baseUrl = baseUrl || envUrl || 'http://10.0.2.2:8000';
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  public setBaseUrl(url: string): void {
    this.baseUrl = url;
  }

  public async get<T>(path: string, timeoutMs: number = DEFAULT_TIMEOUT_MS): Promise<ApiResponse<T>> {
    return this.request<T>('GET', path, undefined, timeoutMs);
  }

  public async post<T>(path: string, body: unknown, timeoutMs: number = DEFAULT_TIMEOUT_MS): Promise<ApiResponse<T>> {
    return this.request<T>('POST', path, body, timeoutMs);
  }

  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    path: string,
    body?: unknown,
    timeoutMs: number = DEFAULT_TIMEOUT_MS
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal
      });

      clearTimeout(timer);

      if (!response.ok) {
        const errText = await response.text();
        return {
          data: null,
          error: `HTTP ${response.status}: ${errText || response.statusText}`,
          status: response.status
        };
      }

      const data = (await response.json()) as T;
      return {
        data,
        error: null,
        status: response.status
      };
    } catch (err: unknown) {
      clearTimeout(timer);
      const isAbort = (err as Error).name === 'AbortError';
      const msg = isAbort ? `Request timeout after ${timeoutMs}ms` : (err as Error).message || 'Network request failed';
      return {
        data: null,
        error: msg,
        status: 0
      };
    }
  }
}

export const defaultApiClient = new ApiClient();
