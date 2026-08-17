import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

# Page Configuration
st.set_page_config(
    page_title="InstaMatch Lebanon",
    page_icon="🛍️",
    layout="wide"
)

# ChromaDB & Multilingual Embedding Model
@st.cache_resource
def load_database():
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    collection = chroma_client.get_collection(
        name="lebanese_businesses",
        embedding_function=embedding_func
    )
    return collection

collection = load_database()

# 3. UI Header
st.title("🛍️ InstaMatch Lebanon")
st.subheader("Discover niche local Lebanese Instagram businesses")

# 4. Search Controls
col1, col2 = st.columns([3, 1])

with col1:
    user_query = st.text_input(
        "What are you looking for today?",
        placeholder="e.g., Natural beef tallow skincare, custom pebble gifts, or glycerin soap suppliers..."
    )

with col2:
    category_filter = st.selectbox(
        "Filter Category",
        ["All Categories", "Food & Desserts", "Beauty & Skincare", "Home & Decor", "Artisan Crafts", "Services"]
    )


if user_query:
    st.write(f"🔍 **Searching for:** *\"{user_query}\"*")
    
    # Query ChromaDB for top 3 matching businesses
    results = collection.query(
        query_texts=[user_query],
        n_results=3
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    st.markdown("---")
    st.markdown("🎯 Recommended Matches")

    for idx, (doc, meta) in enumerate(zip(documents, metadatas)):
        
        
        if category_filter != "All Categories" and meta["category"] != category_filter:
            continue

        with st.container():
            card_col1, card_col2 = st.columns([3, 1])
            
            with card_col1:
                st.markdown(f"#### {idx+1}. {meta['business_name']} ({meta['handle']})")
                st.caption(f"🏷️ **Category:** {meta['category']} | 📍 **Location:** {meta['location']}")
                
                
                st.write(doc.strip())
                
            with card_col2:
                st.write(f"🚚 **Delivery:** {'Available' if meta['offers_delivery'] == 'True' else 'Contact Shop'}")
                st.info(f"📞 **Contact:**\n{meta['contact']}")
                
            st.markdown("---")

else:
    st.info("💡 **Try typing queries like:**\n- *'Homemade custom cakes for events'*\n- *'Organic skincare made in Lebanon with no chemicals'*\n- *'Unique personalized gift frames for dad'*")

# Sidebar Metrics
st.sidebar.title("📊 Dataset Overview")
st.sidebar.metric("Indexed Businesses", "20 Shops")
st.sidebar.metric("Primary Region", "Lebanon-wide")