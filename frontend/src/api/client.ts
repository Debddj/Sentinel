"""Axios client with auth interceptor."""
import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000/api',
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Refresh token logic
    }
    return Promise.reject(error);
  }
);

export default client;
