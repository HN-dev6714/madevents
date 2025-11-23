export interface User {
  Username: string;
}

export interface AuthPayload {
  Username: string;
  Password: string;
}

export interface ApiMessage {
  msg: string;
}