import time
import vertexai
import json
import os
import sys
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput

# inits the project
try:
    vertexai.init(project="preiss-gchat-bot", location="us-east1")
except Exception as e:
    print(f"Failed to initialize Vertex AI: {str(e)}")
    sys.exit(1)


def embed_text(model_name, task_type, text, title=""):
    """Generates a text embedding with a Large Language Model."""
    model = TextEmbeddingModel.from_pretrained(model_name)
    text_embedding_input = TextEmbeddingInput(
        task_type=task_type, title=title, text=text
    )
    embeddings = model.get_embeddings([text_embedding_input])
    return embeddings[0].values


def process_articles(input_dir, output_dir):

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Count the number of .json files in input_dir
    file_count = sum(1 for filename in os.listdir(input_dir) if filename.endswith('.json'))
    print(f"Number of files to process: {file_count}")
    processed_count = 0
    batch_count = 0

    # Process each JSON file in the input directory
    for filename in os.listdir(input_dir):

        # increments batch waiting
        if processed_count >=55:
            batch_count += 1
            processed_count = 0
            time.sleep(60)
            print(f"Waiting for batch {batch_count}...")


        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)

            # Read the article
            with open(input_path, 'r', encoding='utf-8') as f:
                article = json.load(f)

            try:

                # progress indicator
                print(f"Processing article {processed_count + 1} of batch {batch_count}:", article['title'], "")
                processed_count += 1

                # Generate embedding
                embedding = embed_text(
                    model_name="text-embedding-005",
                    task_type="RETRIEVAL_DOCUMENT",
                    text=article['content'],
                    title=article['title']
                )

                # Add embedding to article
                article['embedding'] = embedding

                # Save updated article
                output_path = os.path.join(output_dir, filename.strip('.json') + '_embedded' + '.json')
                print(f"Saving to {output_path}...")
                print(json.dumps(article, indent=4, ensure_ascii=False, sort_keys=True, default=str))
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(article, f, indent=4)

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    
    # check for correct usage
    if len(sys.argv) != 3:
        print("Usage: python generate-embeddings.py <input_directory> <output_directory>")
        sys.exit(1)
        
    process_articles(sys.argv[1], sys.argv[2])