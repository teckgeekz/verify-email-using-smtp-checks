import { env } from "~/env.mjs";
import { auth } from "~/lib/firebase";

export interface EmailFinderRequest {
  name: string;
  company: string;
  domain: string;
}

export interface EmailFinderResponse {
  name: string;
  company: string;
  linkedin: string;
  title: string;
  emails: Array<[string, boolean]>;
}

export interface SingleVerifyRequest {
  email: string;
}

export interface SingleVerifyResponse {
  email: string;
  status: boolean;
}

export interface BulkVerifyResponse {
  email: string;
  status: boolean;
}

class FlaskAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = env.NEXT_PUBLIC_FLASK_URL;
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      return {
        "Authorization": `Bearer ${token}`,
      };
    }
    return {};
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async findEmails(data: EmailFinderRequest): Promise<EmailFinderResponse> {
    const formData = new FormData();
    formData.append("name", data.name);
    formData.append("company", data.company);
    formData.append("domain", data.domain);

    const response = await fetch(`${this.baseUrl}/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async verifySingleEmail(data: SingleVerifyRequest): Promise<SingleVerifyResponse> {
    const formData = new FormData();
    formData.append("email", data.email);

    const response = await fetch(`${this.baseUrl}/single-verify`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getBulkVerifyStatus(): Promise<{ message: string }> {
    const response = await fetch(`${this.baseUrl}/bulk-verify`, {
      method: "GET",
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async bulkVerifyEmails(file: File): Promise<{ results: BulkVerifyResponse[]; download_link?: string }> {
    const authHeaders = await this.getAuthHeaders();
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/bulk-verify`, {
      method: "POST",
      headers: authHeaders,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async downloadFile(filename: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/download/${filename}`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.blob();
  }
}

export const flaskAPI = new FlaskAPI(); 