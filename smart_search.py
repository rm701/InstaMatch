import json
import chromadb
from chromadb.utils import embedding_functions

# local ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

#  open-source multilingual embedding model
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


collection = chroma_client.get_or_create_collection(
    name="lebanese_businesses",
    embedding_function=embedding_func
)

def populate_database(json_filepath: str):
    with open(json_filepath, "r", encoding="utf-8") as f:
        shops = json.load(f)


    for i, shop in enumerate(shops):
        searchable_text = f"""
        Business Name: {shop['business_name']}
        Category: {shop['category']}
        Niche Specialties: {', '.join(shop['niche_tags'])}
        Location: {shop['location']}
        Price Tier: {shop['price_tier']}
        """

        # Add to Vector Store
        collection.add(
            documents=[searchable_text],
            metadatas=[{
                "handle": shop['handle'],
                "business_name": shop['business_name'],
                "category": shop['category'],
                "location": shop['location'],
                "offers_delivery": str(shop['offers_delivery']),
                "contact": shop['contact_channel']
            }],
            ids=[f"shop_{i+1}"]
        )

    

populate_database("shops_database.json")