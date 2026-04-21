export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserMe {
  username: string;
  org_id: number;
  display_name: string;
}

export interface ReportListItem {
  id: number;
  title: string;
  severity: string;
  summary: string;
}

export interface ReportDetail {
  id: number;
  org_id: number;
  title: string;
  severity: string;
  summary: string;
  remediation: string;
}

export interface ApiErrorBody {
  detail?: string | { msg?: string }[];
}
