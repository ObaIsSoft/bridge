const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
        throw new Error(error.detail || response.statusText);
    }

    return response.json();
}

export const bridgesApi = {
    list: () => apiFetch('/bridges'),
    getStats: () => apiFetch('/bridges/stats'),
    create: (data: any) => apiFetch('/bridges', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => apiFetch(`/bridges/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiFetch(`/bridges/${id}`, { method: 'DELETE' }),
    analyze: (url: string) => apiFetch('/bridges/analyze', {
        method: 'POST',
        body: JSON.stringify({ url }),
    }),
    run: (id: string) => apiFetch(`/bridges/${id}/extract`, { method: 'POST' }),
    getLogs: (id: string) => apiFetch(`/bridges/${id}/logs`),
    getAllLogs: () => apiFetch('/bridges/logs'),
    getSecurityPulse: () => apiFetch('/bridges/security/pulse'),
    scan: () => apiFetch('/bridges/scan'),
    scanDeep: () => apiFetch('/bridges/scan/deep', { method: 'POST' }),
    get: (id: string) => apiFetch(`/bridges/${id}`),
};

export const handshakeApi = {
    initiate: (data: any) => apiFetch('/handshake/initiate', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    approve: (id: string) => apiFetch(`/handshake/approve/${id}`, {
        method: 'POST',
    }),
};

export const webhooksApi = {
    list: () => apiFetch('/webhooks'),
    create: (data: any) => apiFetch('/webhooks', {
        method: 'POST',
        body: JSON.stringify(data),
    }),
    delete: (id: string) => apiFetch(`/webhooks/${id}`, { method: 'DELETE' }),
    getLogs: (id: string) => apiFetch(`/webhooks/${id}/logs`),
};

export const keysApi = {
    list: () => apiFetch('/keys'),
    create: (name: string) => apiFetch('/keys', {
        method: 'POST',
        body: JSON.stringify({ name }),
    }),
};

export const systemApi = {
    getHealth: () => apiFetch('/health'),
};
