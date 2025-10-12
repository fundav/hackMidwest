from ragService import get_rag_answer

q = "How do I apply for a farm loan?"
print('Question:', q)
print('\nResponse:')
print(get_rag_answer(q, k=3))
