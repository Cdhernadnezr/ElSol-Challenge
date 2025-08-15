import logging
import uuid
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBService:
    """
    Servicio para gestionar la interacción con la base de datos vectorial Qdrant.
    """
    def __init__(self, host="qdrant", port=6333):
        logger.info(f"Inicializando conexión con Qdrant en {host}:{port}...")
        # El cliente se conecta al servicio 'qdrant' definido en docker-compose.yml
        self.client = QdrantClient(host=host, port=port)
        
        # Carga un modelo pre-entrenado para convertir texto en vectores (embeddings).
        # 'all-MiniLM-L6-v2' es un modelo ligero y eficiente, ideal para empezar.
        logger.info("Cargando modelo de embeddings 'all-MiniLM-L6-v2'...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Modelo de embeddings cargado.")

        self.collection_name = "patient_conversations"
        self.vector_size = self.embedding_model.get_sentence_embedding_dimension()
        
        # Asegura que la colección exista al iniciar el servicio.
        self.create_collection_if_not_exists()

    def create_collection_if_not_exists(self):
        """
        Crea la colección en Qdrant si no existe.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Colección '{self.collection_name}' no encontrada. Creándola...")
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE # Coseno es bueno para similitud de texto
                    ),
                )
                logger.info(f"Colección '{self.collection_name}' creada exitosamente.")
            else:
                logger.info(f"Colección '{self.collection_name}' ya existe.")
        except Exception as e:
            logger.error(f"Error al verificar/crear la colección en Qdrant: {e}")

    def store_record(self, transcription: str, extracted_data: dict, metadata: dict):
        """
        Genera embeddings y almacena la transcripción y sus metadatos en Qdrant.
        """
        try:
            logger.info("Generando vector de embedding para la transcripción...")
            # El vector se genera a partir de la transcripción completa para capturar el contexto general.
            vector = self.embedding_model.encode(transcription).tolist()

            # El 'payload' son los datos que queremos almacenar junto con el vector.
            # Esto nos permitirá filtrar y recuperar la información completa más adelante.
            payload = {
                "transcription": transcription,
                "extracted_data": extracted_data,
                "processing_metadata": metadata
            }
            
            # Generamos un ID único para este punto de datos.
            record_id = str(uuid.uuid4())

            logger.info(f"Almacenando registro en Qdrant con ID: {record_id}")
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload=payload
                    )
                ],
                wait=True # Espera a que la operación se complete
            )
            logger.info("Registro almacenado exitosamente en Qdrant.")
            return record_id
        except Exception as e:
            logger.error(f"Error al almacenar el registro en Qdrant: {e}")
            raise RuntimeError("No se pudo almacenar la información en la base de datos vectorial.")

# Instancia única del servicio para ser usada por la API
vector_db_service = VectorDBService()
