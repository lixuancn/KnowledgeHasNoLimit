from langchain.document_loaders import TextLoader

docs = TextLoader('../tests/state_of_the_union.txt').load()
print(type(docs[0]))
print(docs[0].page_content[:100])

# from langchain.document_loaders import ArxivLoader
# query = "2005.14165"
# docs = ArxivLoader(query=query, load_max_docs=5).load()
# print(len(docs))
# print(docs[0].metadata)  # meta-information of the Document

from langchain.document_loaders import UnstructuredURLLoader
urls = [
    "https://react-lm.github.io/",
]
loader = UnstructuredURLLoader(urls=urls)
data = loader.load()
print(data[0].page_content)
print(data[0].metadata)
loader = UnstructuredURLLoader(urls=urls, mode="elements")
new_data = loader.load()
print(new_data[0].page_content)
print(len(new_data))
print(new_data[1].page_content)
