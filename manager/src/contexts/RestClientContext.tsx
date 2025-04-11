/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-refresh/only-export-components */
// src/contexts/RestClientContext.tsx

import type { IRestClient } from '@/lib/rest';
import {
    QueryClient,
    QueryClientProvider,
} from '@tanstack/react-query';
import React, { createContext, useCallback, useContext, useState } from 'react';
// Import a factory method that returns a concrete implementation of the IRestClient interface
import { createRestClient, ProgressEvent } from '@/lib/rest';

/**
 * Creates a React context to store and provide a shared instance of the RestClient.
 * This avoids passing the client explicitly through props.
 * 
 * The default is set to `undefined` to enforce usage only within a valid provider.
 */
const RestClientContext = createContext<IRestClient | undefined>(undefined);

/**
     * Initialize your REST client instance.
     * You can later enhance this with tokens, request interceptors, dynamic base URLs, etc.
     */
const restClient = createRestClient("http://localhost:8976");

// Create a client
const queryClient = new QueryClient()

/**
 * RestClientProvider
 * 
 * A React context provider that supplies the REST client instance to all
 * descendant components in the component tree.
 * 
 * This allows any component to use the `useRestClient` hook to perform HTTP operations.
 * 
 * Example:
 * ```tsx
 * <RestClientProvider>
 *   <App />
 * </RestClientProvider>
 * ```
 */
export const RestClientProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <RestClientContext.Provider value={restClient}>
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    </RestClientContext.Provider>
);

/**
 * useRestClient
 * 
 * Custom React hook to access the shared RestClient instance.
 * Must be used within a `RestClientProvider`.
 * 
 * Throws an error if used outside the provider to help catch misuse early.
 * 
 * Example usage:
 * ```ts
 * const client = useRestClient();
 * const users = await client.fetchMany<User>('/users');
 * ```
 */
export const useRestClient = (): IRestClient => {
    const context = useContext(RestClientContext);
    if (!context) {
        throw new Error('useRestClient must be used within a RestClientProvider');
    }
    return context;
};

// ===============================
// 🎯 Resource-based CRUD Hooks
// ===============================

/**
 * Fetch a single resource by ID
 * 
 * @example
 * const { fetch, loading, error } = useFetchOne<User>('users');
 * useEffect(() => {
 *   fetch('123').then(setUser);
 * }, []);
 */
export const useFetchOne = <T,>(resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);
    const fetch = useCallback(async (id: string | number, queryParams?: Record<string, any>): Promise<T | null> => {
        setLoading(true);
        setError(null);
        try {
            const data = await client.fetchOne<T>(resourceUrl, id, queryParams);
            return data;
        } catch (err) {
            setError(err);
            return null;
        } finally {
            setLoading(false);
        }
    }, [client, resourceUrl]);

    return { fetch, loading, error };
};

/**
 * Fetch a list of resources
 * 
 * @example
 * const { fetchAll, loading, error } = useFetchMany<User>('users');
 * useEffect(() => {
 *   fetchAll().then(setUsers);
 * }, []);
 */
export const useFetchMany = <T,>(resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);

    const fetchAll = useCallback(async (queryParams?: Record<string, any>): Promise<T[] | null> => {
        setLoading(true);
        setError(null);
        try {
            return await client.fetchMany<T>(resourceUrl, queryParams);
        } catch (err) {
            setError(err);
            return null;
        } finally {
            setLoading(false);
        }
    }, [client, resourceUrl]);

    return { fetchAll, loading, error };
};

/**
 * Create a new resource
 * 
 * @example
 * const { create, loading, error } = useCreate<User>('users');
 * const handleSubmit = async () => {
 *   const result = await create({ name: 'John' });
 * };
 */
export const useCreate = <T,>(resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);

    const create = useCallback(async (data: Partial<T>): Promise<T | null> => {
        setLoading(true);
        setError(null);
        try {
            return await client.create<T>(resourceUrl, data);
        } catch (err) {
            setError(err);
            return null;
        } finally {
            setLoading(false);
        }
    }, [client, resourceUrl]);

    return { create, loading, error };
};

/**
 * Update a resource by ID
 * 
 * @example
 * const { update, loading, error } = useUpdate<User>('users');
 * await update(1, { name: 'Updated' });
 */
export const useUpdate = <T,>(resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);

    const update = useCallback(async (id: string | number, data: Partial<T>): Promise<T | null> => {
        setLoading(true);
        setError(null);
        try {
            return await client.update<T>(resourceUrl, id, data);
        } catch (err) {
            setError(err);
            return null;
        } finally {
            setLoading(false);
        }
    }, [client, resourceUrl]);

    return { update, loading, error };
};

/**
 * Delete a resource by ID
 * 
 * @example
 * const { remove, loading, error } = useRemove('users');
 * await remove(123);
 */
export const useRemove = (resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);

    const remove = useCallback(async (id: string | number): Promise<boolean> => {
        setLoading(true);
        setError(null);
        try {
            await client.remove(resourceUrl, id);
            return true;
        } catch (err) {
            setError(err);
            return false;
        } finally {
            setLoading(false);
        }
    }, [client, resourceUrl]);

    return { remove, loading, error };
};

/**
 * useUploadFile
 * 
 * Hook to upload a file to a specific resource URL.
 * Useful for uploading media, documents, or any binary data.
 * 
 * @example
 * const { uploadFile, loading, error } = useUploadFile<MyResponse>('uploads');
 * const onUpload = async () => {
 *   const result = await uploadFile(selectedFile, 'file', { userId: 123 });
 * };
 */
export const useUploadFile = <T,>(resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);

    const uploadFile = useCallback((
        file: File | Blob,
        fieldName?: string,
        additionalData?: object,
        onProgress?: (event: ProgressEvent) => void
    ): Promise<T | null> => {
        setLoading(true);
        setError(null);

        return client.uploadFile<T>(resourceUrl, file, fieldName, additionalData, onProgress)
            .then((res) => res)
            .catch((err) => {
                setError(err);
                return null;
            })
            .finally(() => {
                setLoading(false);
            });
    }, [client, resourceUrl]);

    return { uploadFile, loading, error };
};

/**
 * useDownloadFile
 * 
 * Hook to download a file from a specific resource URL.
 * 
 * @example
 * const { downloadFile, loading, error } = useDownloadFile('files');
 * const onDownload = async () => {
 *   const blob = await downloadFile(fileId, 'document.pdf');
 *   const url = URL.createObjectURL(blob);
 *   window.open(url);
 * };
 */
export const useDownloadFile = (resourceUrl: string) => {
    const client = useRestClient();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<any>(null);

    const downloadFile = useCallback((
        id: string | number,
        filename?: string,
        onProgress?: (event: ProgressEvent) => void
    ): Promise<Blob | null> => {
        setLoading(true);
        setError(null);

        return client.downloadFile(resourceUrl, id, filename, onProgress)
            .then((res) => res)
            .catch((err) => {
                setError(err);
                return null;
            })
            .finally(() => {
                setLoading(false);
            });
    }, [client, resourceUrl]);

    return { downloadFile, loading, error };
};
/**
 * useBatch
 * 
 * Hook to execute batch operations.
 */
export const useBatch = <T,>() => {
    const client = useRestClient();
    return useCallback((operations: Array<{ method: string; url: string; data?: any }>): Promise<T[]> => {
        return client.batch<T>(operations);
    }, [client]);
};

/**
 * useSearch
 * 
 * Hook to search resources with custom query parameters.
 */
export const useSearch = <T,>() => {
    const client = useRestClient();
    return useCallback((resourceUrl: string, searchParams: Record<string, any>): Promise<T[]> => {
        return client.search<T>(resourceUrl, searchParams);
    }, [client]);
};

/**
 * useCancelOperation
 * 
 * Hook to cancel a specific in-flight request.
 */
export const useCancelOperation = () => {
    const client = useRestClient();
    return useCallback((operationKey: string, message?: string) => {
        client.cancelOperation(operationKey, message);
    }, [client]);
};

/**
 * useCancelAllOperations
 * 
 * Hook to cancel all in-flight operations.
 */
export const useCancelAllOperations = () => {
    const client = useRestClient();
    return useCallback((message?: string) => {
        client.cancelAllOperations(message);
    }, [client]);
};