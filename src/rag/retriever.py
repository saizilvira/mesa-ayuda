import logging
from dataclasses import dataclass
from typing import Optional

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger("rag.retriever")

CHROMA_DIR = "data/chroma_db"
COLLECTION_NAME = "politicas"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Umbral de similitud. Por debajo de este valor abstención.
UMBRAL_SIMILITUD = 0.35


@dataclass
class Cita:
    documento: str
    pagina: int
    fragmento: str
    score: float


@dataclass
class RespuestaRAG:
    respuesta: str
    citas: list[Cita]
    tiene_evidencia: bool
    mensaje_abstencion: Optional[str] = None


class RetrieverPoliticas:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_collection(COLLECTION_NAME)

    def consultar(self, pregunta: str, top_k: int = 4) -> RespuestaRAG:
        # Recupera los fragmentos más similares y decide si hay info suficiente.
        embedding = self.model.encode([pregunta]).tolist()

        resultados = self.collection.query(
            query_embeddings=embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documentos = resultados["documents"][0]
        metadatas = resultados["metadatas"][0]
        distancias = resultados["distances"][0]

        # Chroma con cosine distance: menor distancia = mayor similitud
        # Convertimos a score de similitud aproximado (1 - distance)
        citas = []
        for doc, meta, dist in zip(documentos, metadatas, distancias):
            score = 1.0 - dist
            if score >= UMBRAL_SIMILITUD:
                citas.append(
                    Cita(
                        documento=meta["documento"],
                        pagina=int(meta["pagina"]),
                        fragmento=doc,
                        score=round(score, 3),
                    )
                )

        if not citas:
            logger.info("Abstención: no se encontró evidencia suficiente para: %s", pregunta)
            return RespuestaRAG(
                respuesta=(
                    "No tengo evidencia suficiente en las políticas internas "
                    "para responder esta pregunta con seguridad."
                ),
                citas=[],
                tiene_evidencia=False,
                mensaje_abstencion="Sin fragmentos por encima del umbral de similitud",
            )

        # Construimos una respuesta simple basada en los fragmentos.
        partes = []
        for i, cita in enumerate(citas, 1):
            partes.append(
                f"[{i}] Según {cita.documento} (página {cita.pagina}):\n{cita.fragmento}"
            )

        respuesta = (
            "Con base en las políticas internas disponibles:\n\n"
            + "\n\n".join(partes)
        )

        return RespuestaRAG(
            respuesta=respuesta,
            citas=citas,
            tiene_evidencia=True,
        )