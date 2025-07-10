class Sematic_Search:
    def __init__(self, user : str) -> None:
        self.user : str = user
    
    def run(self, retriever) -> str:    
        retrieved_nodes = retriever.retrieve(self.user)
        text : str = "\n".join([retrieved_nodes[sub].text for sub in range(len(retrieved_nodes))])        

        return text


