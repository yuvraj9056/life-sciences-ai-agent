import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:

    def __init__(self, chunk_size=1000, chunk_overlap=200):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def _generate_chunk_id(self, filename, page_number, chunk_index):

        unique_string = f"{filename}_{page_number}_{chunk_index}"

        return hashlib.sha256(
            unique_string.encode("utf-8")
        ).hexdigest()

    def chunk_documents(self, pdfs):

        chunks = []

        for pdf in pdfs:

            filename = pdf["filename"]

            for page in pdf["pages"]:

                page_number = page["page"]

                texts = self.splitter.split_text(
                    page["text"]
                )

                texts = [
                    text.strip()
                    for text in texts
                    if len(text.strip()) >= 100
                ]

                for i, chunk in enumerate(texts):

                    chunk_id = self._generate_chunk_id(
                        filename,
                        page_number,
                        i
                    )

                    chunks.append(
                        {
                            "id": chunk_id,
                            "content": chunk,
                            "source": filename,
                            "page": page_number
                        }
                    )

        return chunks