const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL || "http";
const API_HOST = import.meta.env.VITE_API_HOST || "127.0.0.1";
const API_PORT = import.meta.env.VITE_API_PORT || "8000";
const PORT = import.meta.env.PORT || "5173";

export const API_BASE_URL = `${API_PROTOCOL}://${API_HOST}:${API_PORT}`;
