export interface AuthHeaders {
  [key: string]: string;
}

export class APIKeyAuth {
  constructor(private apiKey: string, private headerName: string = 'X-API-Key') {}

  getHeaders(): AuthHeaders {
    return { [this.headerName]: this.apiKey };
  }
}
