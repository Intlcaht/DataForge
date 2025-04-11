/* eslint-disable @typescript-eslint/no-explicit-any */
// rest.ts

import axios, {
  AxiosError,
  AxiosInstance,
  AxiosProgressEvent,
  AxiosRequestConfig,
  AxiosResponse,
  CancelTokenSource,
} from 'axios';

// ==================== TYPE DEFINITIONS ====================

/**
 * Extended request configuration that includes our custom options
 */
export interface RequestConfig extends AxiosRequestConfig {
  retry?: {
    maxRetries?: number;
    retryDelay?: number;
    retryStatusCodes?: number[];
  };
  progress?: {
    onUploadProgress?: (event: ProgressEvent) => void;
    onDownloadProgress?: (event: ProgressEvent) => void;
  };
  allowAbsoluteUrls?: boolean;
}

/**
 * Standardized progress event
 */
export interface ProgressEvent {
  loaded: number;
  total: number;
  percentage: number;
}

/**
 * Standardized HTTP error
 */
export class HttpError extends Error {
  public status: number;
  public statusText: string;
  public data: any;
  public originalError: Error | null;

  constructor(
    message: string,
    status: number = 0,
    statusText: string = '',
    data: any = null,
    originalError: Error | null = null
  ) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.statusText = statusText;
    this.data = data;
    this.originalError = originalError;
  }
}
/**
 * Interface for the REST client to be used across the application.
 * Provides a consistent abstraction layer for HTTP operations involving domain objects and collections.
 * Supports CRUD operations, file handling, advanced request patterns, and request cancellation.
 */
export interface IRestClient {
  // ---------------------
  // Core data operations
  // ---------------------

  /**
   * Fetches a single domain object by its ID.
   * @param resourceUrl - The base URL for the resource (e.g., "/users").
   * @param id - The unique identifier of the resource to fetch.
   * @param queryParams - Optional additional query parameters to include in the request.
   * @returns A promise that resolves to a single domain object of type T.
   * 
   * @example
   * const user = await client.fetchOne<User>('/users', 1);
   */
  fetchOne<T>(resourceUrl: string, id: string | number, queryParams?: Record<string, any>): Promise<T>;

  /**
   * Fetches a collection of domain objects.
   * @param resourceUrl - The base URL for the resource (e.g., "/users").
   * @param queryParams - Optional query parameters to filter, sort, or paginate the results.
   * @returns A promise that resolves to an array of domain objects of type T.
   * 
   * @example
   * const users = await client.fetchMany<User>('/users', { role: 'admin' });
   */
  fetchMany<T>(resourceUrl: string, queryParams?: Record<string, any>): Promise<T[]>;

  /**
   * Creates a new domain object.
   * @param resourceUrl - The URL to which the creation request should be sent.
   * @param data - A partial object representing the fields to be set in the new resource.
   * @returns A promise that resolves to the newly created domain object of type T.
   * 
   * @example
   * const newUser = await client.create<User>('/users', { name: 'Alice', email: 'alice@example.com' });
   */
  create<T>(resourceUrl: string, data: Partial<T>): Promise<T>;

  /**
   * Updates an existing domain object completely by its ID.
   * @param resourceUrl - The URL for the resource.
   * @param id - The ID of the resource to update.
   * @param data - A partial object with the fields to overwrite the existing resource.
   * @returns A promise that resolves to the updated domain object.
   * 
   * @example
   * const updatedUser = await client.update<User>('/users', 1, { name: 'Bob' });
   */
  update<T>(resourceUrl: string, id: string | number, data: Partial<T>): Promise<T>;

  /**
   * Applies a partial update to a domain object (PATCH).
   * @param resourceUrl - The resource endpoint.
   * @param id - The ID of the resource to partially update.
   * @param data - Fields to update in the existing object.
   * @returns A promise that resolves to the updated domain object.
   * 
   * @example
   * const patchedUser = await client.partialUpdate<User>('/users', 1, { status: 'active' });
   */
  partialUpdate<T>(resourceUrl: string, id: string | number, data: Partial<T>): Promise<T>;

  /**
   * Removes a domain object by its ID.
   * @param resourceUrl - The base URL for the resource.
   * @param id - The ID of the object to remove.
   * @returns A promise that resolves when the operation is complete.
   * 
   * @example
   * await client.remove('/users', 1);
   */
  remove(resourceUrl: string, id: string | number): Promise<void>;

  // ---------------------
  // File operations
  // ---------------------

  /**
   * Uploads a file to a given endpoint.
   * @param resourceUrl - The upload URL endpoint.
   * @param file - The file or blob to be uploaded.
   * @param fieldName - The field name for the file in the form data (default is usually "file").
   * @param additionalData - Optional additional form fields to send with the file.
   * @param onProgress - Optional callback to track upload progress.
   * @returns A promise that resolves to a response object of type T.
   * 
   * @example
   * const result = await client.uploadFile('/uploads', fileInput.files[0], 'image');
   */
  uploadFile<T>(
    resourceUrl: string,
    file: File | Blob,
    fieldName?: string,
    additionalData?: object,
    onProgress?: (event: ProgressEvent) => void
  ): Promise<T>;

  /**
   * Downloads a file (as a Blob) from a given endpoint.
   * @param resourceUrl - The base URL for the download endpoint.
   * @param id - The ID of the resource to download.
   * @param filename - Optional filename to use for the downloaded file.
   * @param onProgress - Optional callback to track download progress.
   * @returns A promise that resolves to a Blob object representing the file.
   * 
   * @example
   * const blob = await client.downloadFile('/documents', 101, 'report.pdf');
   */
  downloadFile(
    resourceUrl: string,
    id: string | number,
    filename?: string,
    onProgress?: (event: ProgressEvent) => void
  ): Promise<Blob>;

  // ---------------------
  // Request cancellation
  // ---------------------

  // createCancelToken(key: string): CancelTokenSource

  /**
   * Cancels a specific in-progress request.
   * @param operationKey - The unique key associated with the request to cancel.
   * @param message - Optional reason for the cancellation.
   * 
   * @example
   * client.cancelOperation('userSearch');
   */
  cancelOperation(operationKey: string, message?: string): void;

  /**
   * Cancels all pending or in-progress requests.
   * @param message - Optional message describing the reason for the mass cancellation.
   * 
   * @example
   * client.cancelAllOperations('User navigated away');
   */
  cancelAllOperations(message?: string): void;

  // ---------------------
  // Advanced operations
  // ---------------------

  /**
   * Executes multiple API requests in a single batch operation.
   * Each operation is defined by HTTP method, URL, and optional data.
   * @param operations - Array of request definitions to execute in batch.
   * @returns A promise that resolves to an array of results for each operation.
   * 
   * @example
   * const results = await client.batch([
   *   { method: 'POST', url: '/users', data: { name: 'New User' } },
   *   { method: 'DELETE', url: '/users/2' }
   * ]);
   */
  batch<T>(operations: Array<{ method: string; url: string; data?: any }>): Promise<T[]>;

  /**
   * Performs a search with given parameters on a resource collection.
   * @param resourceUrl - The endpoint to apply the search on.
   * @param searchParams - Key-value pairs defining search filters.
   * @returns A promise that resolves to an array of matched domain objects.
   * 
   * @example
   * const results = await client.search<User>('/users/search', { name: 'Alice' });
   */
  search<T>(resourceUrl: string, searchParams: Record<string, any>): Promise<T[]>;
}



/**
 * Implementation of the REST client using Axios
 */
export class RestService implements IRestClient {
  private axios: AxiosInstance;
  private cancelTokens: Map<string, CancelTokenSource> = new Map();
  private defaultConfig: RequestConfig = {
    retry: {
      maxRetries: 3,
      retryDelay: 1000,
      retryStatusCodes: [408, 429, 500, 502, 503, 504],
    },
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    timeout: 30000,
  };

  /**
   * Create a new RestService
   * @param baseURL The base URL for API requests
   * @param config Optional default configuration
   */
  constructor(baseURL: string, config: RequestConfig = {}) {
    this.axios = axios.create({
      baseURL,
      ...this.defaultConfig,
      ...config,
    });
    this.setupInterceptors();
  }

  // ==================== INTERFACE IMPLEMENTATION ====================

  /**
   * Fetch a single resource by ID
   * @param resourceUrl The resource endpoint
   * @param id The resource identifier
   * @param queryParams Optional query parameters
   * @returns Promise with the domain model
   */
  public async fetchOne<T>(
    resourceUrl: string,
    id: string | number,
    queryParams?: Record<string, any>
  ): Promise<T> {
    return this.get<T>(`${resourceUrl}/${id}`, { params: queryParams });
  }

  /**
   * Fetch multiple resources
   * @param resourceUrl The resource endpoint
   * @param queryParams Optional query parameters for filtering/pagination
   * @returns Promise with an array of domain models
   */
  public async fetchMany<T>(
    resourceUrl: string,
    queryParams?: Record<string, any>
  ): Promise<T[]> {
    return this.get<T[]>(resourceUrl, { params: queryParams });
  }

  /**
   * Create a new resource
   * @param resourceUrl The resource endpoint
   * @param data The data to create
   * @returns Promise with the created domain model
   */
  public async create<T>(resourceUrl: string, data: Partial<T>): Promise<T> {
    return this.post<T>(resourceUrl, data);
  }

  /**
   * Update a resource completely
   * @param resourceUrl The resource endpoint
   * @param id The resource identifier
   * @param data The updated data
   * @returns Promise with the updated domain model
   */
  public async update<T>(
    resourceUrl: string,
    id: string | number,
    data: Partial<T>
  ): Promise<T> {
    return this.put<T>(`${resourceUrl}/${id}`, data);
  }

  /**
   * Update a resource partially
   * @param resourceUrl The resource endpoint
   * @param id The resource identifier
   * @param data The partial data to update
   * @returns Promise with the updated domain model
   */
  public async partialUpdate<T>(
    resourceUrl: string,
    id: string | number,
    data: Partial<T>
  ): Promise<T> {
    return this.patch<T>(`${resourceUrl}/${id}`, data);
  }

  /**
   * Remove a resource
   * @param resourceUrl The resource endpoint
   * @param id The resource identifier
   */
  public async remove<T>(resourceUrl: string, id: string | number): Promise<void> {
    await this.delete<T>(`${resourceUrl}/${id}`);
  }

  /**
   * Upload a file to the server
   * @param resourceUrl The resource endpoint
   * @param file The file to upload
   * @param fieldName The field name for the file (default: 'file')
   * @param additionalData Additional form data
   * @param onProgress Progress callback
   * @returns Promise with the response data
   */
  public async uploadFile<T>(
    resourceUrl: string,
    file: File | Blob,
    fieldName: string = 'file',
    additionalData: object = {},
    onProgress?: (event: ProgressEvent) => void
  ): Promise<T> {
    return this._uploadFile<T>(resourceUrl, file, fieldName, additionalData, {
      progress: {
        onUploadProgress: onProgress,
      },
    });
  }

  /**
   * Download a file from the server
   * @param resourceUrl The resource endpoint
   * @param id The resource identifier
   * @param filename Optional filename
   * @param onProgress Progress callback
   * @returns Promise with the file blob
   */
  public async downloadFile(
    resourceUrl: string,
    id: string | number,
    filename?: string,
    onProgress?: (event: ProgressEvent) => void
  ): Promise<Blob> {
    return this._downloadFile(`${resourceUrl}/${id}${filename ? `/${filename}` : ''}`, {
      progress: {
        onDownloadProgress: onProgress,
      },
      responseType: 'blob',
    });
  }

  /**
   * Cancel a specific operation by key
   * @param operationKey The operation key
   * @param message Optional cancellation message
   */
  public cancelOperation(operationKey: string, message?: string): void {
    this.cancelRequest(operationKey, message);
  }

  /**
   * Cancel all pending operations
   * @param message Optional cancellation message
   */
  public cancelAllOperations(message?: string): void {
    this.cancelAllRequests(message);
  }

  /**
   * Execute multiple operations in a single request
   * @param operations Array of operations to perform
   * @returns Promise with array of results
   */
  public async batch<T>(
    operations: Array<{ method: string; url: string; data?: any }>
  ): Promise<T[]> {
    return this.post<T[]>('/batch', { operations });
  }

  /**
   * Search for resources with complex search parameters
   * @param resourceUrl The resource endpoint
   * @param searchParams Search parameters
   * @returns Promise with matching resources
   */
  public async search<T>(
    resourceUrl: string,
    searchParams: Record<string, any>
  ): Promise<T[]> {
    return this.post<T[]>(`${resourceUrl}/search`, searchParams);
  }

  // ==================== CORE HTTP METHODS ====================

  /**
   * Main request method that handles all HTTP requests
   * @param config Request configuration
   * @returns Promise resolving to response data
   */
  public async request<T = any>(config: RequestConfig): Promise<T> {
    try {
      config = this.handleAbsoluteUrls(config);
      
      // Set up cancel token if not provided
      if (!config.cancelToken) {
        const cancelKey = `${config.method || 'GET'}_${config.url}_${Date.now()}`;
        const source = this.createCancelToken(cancelKey);
        config.cancelToken = source.token;
      }
      
      // Set up progress handlers
      if (config.progress) {
        if (config.progress.onUploadProgress) {
          config.onUploadProgress = (event: AxiosProgressEvent) => {
            if (config.progress?.onUploadProgress) {
              config.progress.onUploadProgress(RestService.normalizeProgressEvent(event));
            }
          };
        }
        
        if (config.progress.onDownloadProgress) {
          config.onDownloadProgress = (event: AxiosProgressEvent) => {
            if (config.progress?.onDownloadProgress) {
              config.progress.onDownloadProgress(RestService.normalizeProgressEvent(event));
            }
          };
        }
        
        // Remove our custom progress config to avoid Axios warnings
        delete config.progress;
      }
      
      const response = await this.executeRequestWithRetry<T>(config);
      return response.data;
    } catch (error) {
      throw this.normalizeError(error as AxiosError | HttpError);
    }
  }

  /**
   * Sends GET request
   * @param url Request URL
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async get<T>(url: string, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'GET', url });
  }

  /**
   * Sends POST request with payload
   * @param url Request URL
   * @param data Optional request payload
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async post<T>(url: string, data?: any, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'POST', url, data });
  }

  /**
   * Sends PUT request for full resource updates
   * @param url Request URL
   * @param data Optional request payload
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async put<T>(url: string, data?: any, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'PUT', url, data });
  }

  /**
   * Sends PATCH request for partial updates
   * @param url Request URL
   * @param data Optional request payload
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async patch<T>(url: string, data?: any, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'PATCH', url, data });
  }

  /**
   * Sends DELETE request
   * @param url Request URL
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async delete<T>(url: string, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'DELETE', url });
  }

  /**
   * Sends HEAD request for headers only
   * @param url Request URL
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async head<T>(url: string, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'HEAD', url });
  }

  /**
   * Sends OPTIONS request for CORS/preflight
   * @param url Request URL
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  public async options<T>(url: string, config: RequestConfig = {}): Promise<T> {
    return this.request<T>({ ...config, method: 'OPTIONS', url });
  }

  // ==================== FILE OPERATIONS ====================

  /**
   * Handles file uploads with multipart/form-data
   * @param url Request URL
   * @param file File or Blob to upload
   * @param fieldName Field name for the file
   * @param additionalData Additional form data fields
   * @param config Optional request configuration
   * @returns Promise resolving to response data
   */
  private async _uploadFile<T>(
    url: string,
    file: File | Blob,
    fieldName: string = 'file',
    additionalData: object = {},
    config: RequestConfig = {}
  ): Promise<T> {
    const formData = new FormData();
    
    // Add the file to form data
    const filename = (file as File).name || `file-${Date.now()}`;
    formData.append(fieldName, file, filename);
    
    // Add any additional data
    for (const [key, value] of Object.entries(additionalData)) {
      if (value !== undefined && value !== null) {
        formData.append(key, value.toString());
      }
    }
    
    return this.post<T>(url, formData, {
      ...config,
      headers: {
        ...config.headers,
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Handles file downloads
   * @param url Request URL
   * @param config Optional request configuration
   * @returns Promise resolving to Blob object
   */
  private async _downloadFile(
    url: string,
    config: RequestConfig = {}
  ): Promise<Blob> {
    return this.get<Blob>(url, {
      ...config,
      responseType: 'blob',
    });
  }

  // ==================== CANCELLATION METHODS ====================

  /**
   * Creates cancellation token for specific request
   * @param key Unique key for the cancellation token
   * @returns CancelTokenSource object
   */
  public createCancelToken(key: string): CancelTokenSource {
    const source = axios.CancelToken.source();
    this.cancelTokens.set(key, source);
    return source;
  }

  /**
   * Cancels specific request by key
   * @param key Unique key for the cancellation token
   * @param message Optional cancellation message
   */
  public cancelRequest(key: string, message?: string): void {
    const source = this.cancelTokens.get(key);
    if (source) {
      source.cancel(message || 'Request cancelled');
      this.cancelTokens.delete(key);
    }
  }

  /**
   * Cancels all pending requests
   * @param message Optional cancellation message
   */
  public cancelAllRequests(message?: string): void {
    for (const [key, source] of this.cancelTokens.entries()) {
      source.cancel(message || 'All requests cancelled');
      this.cancelTokens.delete(key);
    }
  }

  // ==================== PRIVATE METHODS ====================

  /**
   * Configures request/response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor
    this.axios.interceptors.request.use(
      (config) => {
        // Add timestamp to prevent caching for GET requests
        if (config.method?.toUpperCase() === 'GET') {
          config.params = {
            ...config.params,
            _t: Date.now(),
          };
        }
        return config;
      },
      (error) => {
        return Promise.reject(this.normalizeError(error));
      }
    );

    // Response interceptor
    this.axios.interceptors.response.use(
      (response) => response,
      (error) => {
        return Promise.reject(this.normalizeError(error));
      }
    );
  }

  /**
   * Implements retry logic with exponential backoff
   * @param config Request configuration
   * @param retryCount Current retry attempt number
   * @returns Promise resolving to Axios response
   */
  private async executeRequestWithRetry<T>(
    config: RequestConfig,
    retryCount: number = 0
  ): Promise<AxiosResponse<T>> {
    const retryConfig = { ...config };
      
      // Remove retry config to avoid infinite recursion from Axios
      if (retryConfig.retry) {
        const { retry } = retryConfig;
        delete retryConfig.retry;
        
        try {
          return await this.axios.request<T>(retryConfig);
        } catch (error) {
          const axiosError = error as AxiosError;
          
          // Check if we should retry this request
          if (
            retry.maxRetries &&
            retryCount < retry.maxRetries &&
            (
              !axiosError.response || // Network errors
              (axiosError.response && 
               retry.retryStatusCodes?.includes(axiosError.response.status))
            )
          ) {
            // Calculate backoff delay with exponential factor
            const delay = retry.retryDelay 
              ? retry.retryDelay * Math.pow(2, retryCount)
              : 1000 * Math.pow(2, retryCount);
            
            // Wait for the calculated delay
            await new Promise(resolve => setTimeout(resolve, delay));
            
            // Retry the request
            return this.executeRequestWithRetry<T>(
              { ...config, retry },
              retryCount + 1
            );
          }
          
          throw error;
        }
      } else {
        return await this.axios.request<T>(retryConfig);
      }
  }

  /**
   * Converts all errors to standardized HttpError
   * @param error Original error object
   * @returns Normalized HttpError
   */
  private normalizeError(error: AxiosError | HttpError): HttpError {
    // Already normalized
    if (error instanceof HttpError) {
      return error;
    }
    
    // Axios error
    if (axios.isAxiosError(error)) {
      const { response, request, message } = error;
      
      // Server responded with error status code
      if (response) {
        return new HttpError(
          response.statusText || message,
          response.status,
          response.statusText,
          response.data,
          error
        );
      }
      
      // Request made but no response received
      if (request) {
        return new HttpError(
          'No response received from server',
          0,
          '',
          null,
          error
        );
      }
      
      // Request configuration error
      return new HttpError(
        message,
        0,
        '',
        null,
        error
      );
    }
    
    // Unknown error
    return new HttpError(
      'Unknown error',
      0,
      '',
      null,
      new Error(String(error))
    );
  }

  /**
   * Manages baseURL/absolute URL resolution
   * @param config Request configuration
   * @returns Updated request configuration
   */
  private handleAbsoluteUrls(config: RequestConfig): RequestConfig {
    if (!config.url) {
      return config;
    }
    
    const isAbsoluteUrl = /^([a-z][a-z\d+\-.]*:)?\/\//i.test(config.url);
    
    if (isAbsoluteUrl && !config.allowAbsoluteUrls) {
      // Strip the protocol and domain, keeping only the path
      const urlObj = new URL(config.url);
      config.url = urlObj.pathname + urlObj.search + urlObj.hash;
    }
    
    return config;
  }

  /**
   * Standardizes progress event format
   * @param event Axios progress event
   * @returns Standardized progress event
   */
  public static normalizeProgressEvent(event: AxiosProgressEvent): ProgressEvent {
    const total = event.total || 0;
    const loaded = event.loaded || 0;
    const percentage = total > 0 ? Math.round((loaded / total) * 100) : 0;
    
    return {
      loaded,
      total,
      percentage,
    };
  }
}

/**
 * Create default REST client instance
 * @param baseURL API base URL
 * @param defaultConfig Default configuration
 * @returns REST client interface
 */
export function createRestClient(baseURL: string, defaultConfig: RequestConfig = {}): IRestClient {
  return new RestService(baseURL, defaultConfig);
}

// // Expose the main classes and factory function
// export default {
//   createRestClient,
// };