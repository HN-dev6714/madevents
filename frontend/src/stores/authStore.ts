import { defineStore } from 'pinia';
import client from '@/api/client';
import type { AuthPayload, User, ApiMessage } from '@/types/auth';
import { AxiosError } from 'axios';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  actions: {
    async register(payload: AuthPayload): Promise<boolean> {
      this.loading = true;
      this.error = null;
      try {
        await client.post<ApiMessage>('/users', payload);
        return true;
      } catch (err: unknown) {
        if (err instanceof AxiosError) {
          this.error = err.response?.data?.detail || 'Registration failed';
        } else {
          this.error = 'An unexpected error occurred';
        }
        return false;
      } finally {
        this.loading = false;
      }
    },

    async login(payload: AuthPayload): Promise<boolean> {
      this.loading = true;
      this.error = null;
      try {
        await client.post<ApiMessage>('/login', payload);
        
        // Cookie is set automatically by browser. 
        // We assume success means logged in.
        this.isAuthenticated = true;
        this.user = { Username: payload.Username }; 
        return true;
      } catch (err: unknown) {
        if (err instanceof AxiosError) {
          this.error = err.response?.data?.detail || 'Login failed';
        }
        this.isAuthenticated = false;
        this.user = null;
        return false;
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await client.post<ApiMessage>('/logout');
      } catch (e) {
        console.error('Logout failed on server', e);
      } finally {
        this.user = null;
        this.isAuthenticated = false;
      }
    },
    
    // async checkSession() {
    //   // TODO: Get cookie from header
    //   // Go over session table and grab user id
    //   // Then query get_current_user
    //   this.loading = true;
    //   try {
    //     const response = await client.get<User>('/users/me'); // TODO: Replace with some sort of user get function?
        
    //     this.user = response.data;
    //     this.isAuthenticated = true;
    //   } catch (err) {
    //     this.user = null;
    //     this.isAuthenticated = false;
    //   } finally {
    //     this.loading = false;
    //   }
    // }
}
});