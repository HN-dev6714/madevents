import axios, { type AxiosInstance } from 'axios';

const client: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // <--- CRITICAL: Sends/Receives HttpOnly Cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

export default client;