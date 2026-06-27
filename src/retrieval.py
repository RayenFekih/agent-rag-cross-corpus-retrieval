import time

from google.cloud import discoveryengine_v1 as discoveryengine


def get_struct_field(document, field_name: str):
    return document.struct_data.get(field_name)


def parse_search_result(result, rank: int) -> dict:
    document = result.document
    rank_signals = getattr(result, "rank_signals", None)

    return {
        "rank": rank,
        "result_id": result.id,
        "document_id": document.id,
        "document_name": document.name,

        # Lightweight fields only
        "fatwa_id": get_struct_field(document, "fatwa_id"),
        "fatwa_title": get_struct_field(document, "fatwa_title"),
        "fatwa_tree": get_struct_field(document, "fatwa_tree"),
        "fatwa_date": get_struct_field(document, "fatwa_date"),
        "fatwa_summary": get_struct_field(document, "fatwa_summary"),

        # Rank signals
        "keyword_similarity_score": getattr(rank_signals, "keyword_similarity_score", None),
        "semantic_similarity_score": getattr(rank_signals, "semantic_similarity_score", None),
        "topicality_rank": getattr(rank_signals, "topicality_rank", None),
        "default_rank": getattr(rank_signals, "default_rank", None),
        "boosting_factor": getattr(rank_signals, "boosting_factor", None),
    }


def parse_search_response_fast(response, limit: int | None = None) -> list[dict]:
    parsed_results = []

    for rank, result in enumerate(response, start=1):
        if limit is not None and rank > limit:
            break

        parsed_results.append(parse_search_result(result, rank))

    return parsed_results


def search_agent_search(
    *,
    client: discoveryengine.SearchServiceClient,
    project_id: str,
    location: str,
    app_id: str,
    query: str,
    page_size: int = 10,
    filter_query: str | None = None,
) -> list[dict]:
    serving_config = (
        f"projects/{project_id}/locations/{location}/collections/default_collection/"
        f"engines/{app_id}/servingConfigs/default_search"
    )

    start_time = time.time()
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
        user_pseudo_id="rayen",
        filter=filter_query
    )

    response = client.search(request)
    search_time = time.time() - start_time
    print(f"Search completed in {search_time:.2f} seconds")
    # return response
    return parse_search_response_fast(response, limit=page_size)
