from google.cloud import aiplatform
from sys import argv

PROJECT_ID = 'preiss-gchat-bot'
PROJECT_LOCATION = 'us-east1'

# Provided by google documentation
def vector_search_create_streaming_index(
    project: str, location: str, display_name: str, gcs_uri: str = None
) -> aiplatform.MatchingEngineIndex:
    """Create a vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        display_name (str): Required. The index display name
        gcs_uri (str): Optional. The Google Cloud Storage uri for index content

    Returns:
        The created MatchingEngineIndex.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create Index
    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=display_name,
        contents_delta_uri=gcs_uri,
        description=f"{PROJECT_ID} Index",
        dimensions=768,
        approximate_neighbors_count=10,
        leaf_node_embedding_count=100,
        index_update_method="STREAM_UPDATE",  # Options: STREAM_UPDATE, BATCH_UPDATE
        distance_measure_type=aiplatform.matching_engine.matching_engine_index_config.DistanceMeasureType.COSINE_DISTANCE,
    )

    return index

def main():

    if len(argv) < 2:
        print("Usage: python CreateIndex.py <index_display_name> <uri>")

    display_name = argv[1]
    if len(argv) > 2:
        uri = argv[2]
        try:
            vector_search_create_streaming_index(PROJECT_ID, PROJECT_LOCATION, display_name, uri)
            exit(0)
        except Exception as e:
            print(e)
            exit(1)

    try:
        vector_search_create_streaming_index(PROJECT_ID, PROJECT_LOCATION, display_name)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()