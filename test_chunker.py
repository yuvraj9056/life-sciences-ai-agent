from backend.rag.pdf_reader import PDFReader
from backend.rag.chunker import DocumentChunker

pdfs = PDFReader.read_folder("datasets/unstructured")

chunker = DocumentChunker()

chunks = chunker.chunk_documents(pdfs)

print("Total Chunks:", len(chunks))

print("\nFirst Chunk\n")

print(chunks[0])

print("\nChunk Length:", len(chunks[0]["content"]))