// Base URL do seu backend
const API_BASE_URL = "http://localhost:3000";

// Função GET genérica
async function apiGet(endpoint) {
  try {
    const response = await axios.get(`${API_BASE_URL}${endpoint}`);
    return response.data;
  } catch (error) {
    console.error("Erro no GET:", error);
    throw error;
  }
}

export { apiGet };