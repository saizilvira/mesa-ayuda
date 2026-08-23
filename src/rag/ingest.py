import logging
from pathlib import Path

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("rag.ingest")

POLITICAS_DIR = Path("data/politicas")
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "politicas"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def extraer_texto_pdf(ruta: Path) -> list[dict]:
    # Extrae texto página por página.
    reader = PdfReader(str(ruta))
    paginas = []
    for i, page in enumerate(reader.pages, start=1):
        texto = page.extract_text() or ""
        if texto.strip():
            paginas.append({
                "documento": ruta.name,
                "pagina": i,
                "texto": texto.strip(),
            })
    return paginas


def fragmentar(paginas: list[dict], chunk_size: int = 500, chunk_overlap: int = 80) -> list[dict]:
    #Divide el texto en fragmentos.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    fragmentos = []
    for pag in paginas:
        chunks = splitter.split_text(pag["texto"])
        for idx, chunk in enumerate(chunks):
            fragmentos.append({
                "documento": pag["documento"],
                "pagina": pag["pagina"],
                "chunk_id": f"{pag['documento']}_p{pag['pagina']}_c{idx}",
                "texto": chunk,
            })
    return fragmentos


def crear_coleccion(fragmentos: list[dict]):
    # Genera embeddings y los guarda en ChromaDB.
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=ChromaSettings(anonymized_telemetry=False),
    )

    # Eliminar colección anterior si existe
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    logger.info("Cargando modelo de embeddings: %s", EMBEDDING_MODEL)
    model = SentenceTransformer(EMBEDDING_MODEL)

    textos = [f["texto"] for f in fragmentos]
    ids = [f["chunk_id"] for f in fragmentos]
    metadatas = [
        {"documento": f["documento"], "pagina": f["pagina"]}
        for f in fragmentos
    ]

    logger.info("Generando embeddings de %d fragmentos...", len(textos))
    embeddings = model.encode(textos, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=textos,
        metadatas=metadatas,
    )

    logger.info("Ingesta completada. Fragmentos indexados: %d", len(fragmentos))
    return collection


def ejecutar_ingesta():
    if not POLITICAS_DIR.exists():
        raise FileNotFoundError(f"No se encontró la carpeta {POLITICAS_DIR}")

    pdfs = list(POLITICAS_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError("No hay PDFs en data/politicas/")

    logger.info("PDFs encontrados: %s", [p.name for p in pdfs])

    todas_paginas = []
    for pdf in pdfs:
        logger.info("Extrayendo: %s", pdf.name)
        todas_paginas.extend(extraer_texto_pdf(pdf))

    logger.info("Total páginas con texto: %d", len(todas_paginas))
    fragmentos = fragmentar(todas_paginas)
    logger.info("Total fragmentos: %d", len(fragmentos))

    crear_coleccion(fragmentos)
    print("Ingesta finalizada correctamente.")


if __name__ == "__main__":
    ejecutar_ingesta()