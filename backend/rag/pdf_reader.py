#1.
#read pdf files and extract text from it

import fitz
from pathlib import Path
from backend.rag.text_cleaner import TextCleaner

class PDFReader:

    @staticmethod
    def read(pdf_path: str):

        doc = fitz.open(pdf_path)

        pages = []

        for page_num, page in enumerate(doc):

            text = TextCleaner.clean(page.get_text())

            pages.append(
                {
                    "page": page_num + 1,
                    "text": text
                }
            )

        doc.close()

        return pages

    @staticmethod
    def read_folder(folder_path: str):

        pdfs = []

        for pdf in Path(folder_path).glob("*.pdf"):

            pdfs.append(
                {
                    "filename": pdf.name,
                    "pages": PDFReader.read(str(pdf))
                }
            )

        return pdfs