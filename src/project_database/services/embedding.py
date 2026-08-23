from json import dumps

import numpy as np
from fastembed import TextEmbedding


def embed(model, s):
    return next(model.embed(s))


def sort_projects_by_search(projects, search):
    # By default this is BAAI/bge-small-en-v1.5
    model = TextEmbedding()
    # Truncate to 500 characters
    # According to https://huggingface.co/BAAI/bge-small-en-v1.5 apparently we get better results with this special prefix?
    search_embedding = embed(
        model,
        f"Represent this sentence for searching relevant passages: {search[:500]}",
    )
    
    try:
        embed_cache = np.load("data/embed_cache.npy", allow_pickle=True).item()
    except Exception as e:
        print(e)
        embed_cache = {}
    
    for i in range(len(projects)):
        # This has a nondeterministic hex address hardcoded in
        del projects[i]["_sa_instance_state"]
        s = dumps(projects[i], sort_keys=True, default=str)
        # Should be a 64-bit hash so don't worry about collisions
        h = hash(s)
        if h not in embed_cache:
            embed_cache[h] = embed(model, s)
        projects[i]["score"] = np.dot(search_embedding, embed_cache[h])

    np.save("data/embed_cache.npy", embed_cache)

    # Reverse the sort order since higher cosine means more similar
    return sorted(projects, key=lambda p: -p["score"])
