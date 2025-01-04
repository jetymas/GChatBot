'''
Reads in a series of embeddings and creates an index
'''

from sys import argv, exit
import os
import json

def main():
    # Checks for correct usage
    if len(argv) != 3:
        print("Usage: python FormatEmbeddings.py <input-directory> <output-file>\n")
        exit(1)

    input_dir = argv[1]
    output_file = argv[2]

    # Iterates through each JSON file in the given input directory and writes the ID and embeddings
    #   of each article to a JSONL-formatted file
    with open(output_file, 'w', encoding='utf-8') as outfile:  # This creates 'outfile' handle

        # Iterates through each article (stored in a json) in a local directory
        for filename in os.listdir(input_dir):

            # Checks for valid .json file to write to index
            if filename.endswith(".json"):

                filepath = os.path.join(input_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)

                        # Copies id and embedding to new object
                        id_embedding = {
                            "id": str(data["id"]),
                            "title": data["title"],
                            "embedding": data["embedding"]
                        }

                        # Writes new object to JSONL
                        outfile.write(json.dumps(id_embedding) + '\n')  # Use outfile, not output_file

                        print(f"Wrote {filename}")

                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    main()