from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        separators=[";", "\n\n", "\n", " "],
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text)