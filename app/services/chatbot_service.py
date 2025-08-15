import logging
import httpx
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotService:
    """
    Servicio para manejar la lógica del chatbot usando el patrón RAG.
    """
    def __init__(self, qdrant_host="qdrant", qdrant_port=6333):
        logger.info("Inicializando ChatbotService...")
        # Conexión a la base de datos vectorial
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # Carga del modelo de embeddings (el mismo que usamos para almacenar)
        # La librería lo carga desde el caché, por lo que es instantáneo.
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.collection_name = "patient_conversations"
        self.llm_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={settings.GEMINI_API_KEY}"

    def _retrieve_context(self, query: str, top_k: int = 3) -> list:
        """
        Paso 1: Recuperar contexto relevante de Qdrant.
        """
        try:
            logger.info(f"Buscando contexto para la pregunta: '{query}'")
            # Convierte la pregunta del usuario en un vector
            query_vector = self.embedding_model.encode(query).tolist()
            
            # Busca en Qdrant los 'top_k' vectores más similares
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True # ¡Muy importante para obtener los datos!
            )
            
            # Extrae el payload (los datos guardados) de los resultados
            context = [hit.payload for hit in search_results]
            logger.info(f"Se encontraron {len(context)} documentos de contexto.")
            return context
        except Exception as e:
            logger.error(f"Error al recuperar contexto de Qdrant: {e}")
            return []

    async def _generate_response(self, query: str, context: list) -> str:
        """
        Paso 2: Generar una respuesta usando el LLM con el contexto recuperado.
        """
        if not context:
            return "Lo siento, no pude encontrar información relevante para responder a tu pregunta."

        # Construimos un prompt claro y directo para el LLM
        context_str = "\n---\n".join(json.dumps(doc, indent=2) for doc in context)
        prompt = f"""
        Eres un asistente de IA que responde preguntas sobre conversaciones con pacientes.
        Usa únicamente la siguiente información de contexto para responder la pregunta del usuario.
        Si la respuesta no se encuentra en el contexto, di "No tengo suficiente información para responder".

        Contexto:
        ---
        {context_str}
        ---

        Pregunta del usuario: {query}

        Respuesta:
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}

        logger.info("Enviando petición al LLM para generar la respuesta final...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.llm_api_url, json=payload, headers=headers)
                response.raise_for_status()
                
                # Extrae el texto de la respuesta del LLM
                content = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return content.strip()
            except Exception as e:
                logger.error(f"Error al generar respuesta con el LLM: {e}")
                return "Hubo un error al comunicarme con el servicio de IA para generar la respuesta."

    async def answer_question(self, query: str) -> dict:
        """
        Orquesta el proceso completo de RAG.
        """
        context = self._retrieve_context(query)
        answer = await self._generate_response(query, context)
        
        return {
            "question": query,
            "answer": answer,
            "retrieved_context": context # Opcional: devolver el contexto para depuración
        }

# Instancia única del servicio
chatbot_service = ChatbotService()
