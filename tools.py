import os
import glob
import shutil
from dotenv import load_dotenv
from git import Repo
from serpapi import GoogleSearch
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter


load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
PDF_DIR = os.getenv("PDF_DIR")

# ——————————————————————————————————————
# Tools
# ——————————————————————————————————————
def web_search(query: str) -> str:
    params = {"q": query, "api_key": SERPAPI_KEY}
    res = GoogleSearch(params).get_dict()
    snippets = [r.get("snippet", "") for r in res.get("organic_results", [])][:5]
    # print("Query")
    # print(query)
    # print("Results")
    # print("\n\n".join(snippets))
    return "\n\n".join(snippets)

def clone_and_markdown(repo_url: str) -> str:
    tmp = "./tmp_repo"
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    Repo.clone_from(repo_url, tmp)
    md = []
    for root, _, files in os.walk(tmp):
        for f in files:
            if f.endswith((".py", ".md", ".txt")):
                path = os.path.join(root, f)
                with open(path, encoding="utf8", errors="ignore") as fp:
                    content = fp.read()
                    md.append(f"## {os.path.relpath(path, tmp)}\n\n```text\n{content}\n```")
    return "\n\n".join(md)

def load_and_embed_pdfs(query: str, k: int = 5) -> str:
    pdf_dir = PDF_DIR
    filepaths = glob.glob(f"{pdf_dir}/*.pdf")
    all_docs = []

    for path in filepaths:
        loader = PyPDFLoader(path)
        docs = loader.load()
        all_docs.extend(docs)

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(all_docs)

    embedder = OllamaEmbeddings(model="nomic-embed-text:latest")
    vectordb = FAISS.from_documents(chunks, embedder)
    hits = vectordb.similarity_search(query, k=k)

    return "\n\n".join(f"Source: {h.metadata.get('source', '')}\n\n{h.page_content}" for h in hits)