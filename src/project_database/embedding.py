from fastembed.rerank.cross_encoder import TextCrossEncoder


def sort_projects_by_search(projects, search):
    encoder = TextCrossEncoder(
        model_name="jinaai/jina-reranker-v1-turbo-en", cache_dir="data"
    )
    # Truncate search to 512 characters
    scores = list(encoder.rerank(search[:512], map(str, projects)))
    # Reverse the sort order since higher means more similar
    return [p for _, p in sorted(zip(scores, projects), reverse=True)]
