from backend.rag.pdf_reader import PDFReader

pdfs = PDFReader.read_folder("datasets/unstructured")

print(f"Total PDFs: {len(pdfs)}")

for pdf in pdfs:

    print("\n", pdf["filename"])

    print("Pages:", len(pdf["pages"]))

    print("First 500 characters:\n")

    print(pdf["pages"][0]["text"][:500])