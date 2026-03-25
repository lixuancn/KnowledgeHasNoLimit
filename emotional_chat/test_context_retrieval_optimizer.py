from backend.services.context_retrieval_optimizer import ContextRetrievalOptimizer

if __name__ == "__main__":
    optimizer = ContextRetrievalOptimizer()
    results = optimizer.retrieve_relevant_context("你好，我今天很开心")
    print(results)
