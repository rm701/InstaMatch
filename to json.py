import json
import os
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field, field_validator

#  the Pydantic Schema 
class LocalBusinessSchema(BaseModel):
    handle: str = Field(default="@unknown", description="The @handle of the Instagram page")
    business_name: str = Field(default="Unknown Business", description="Name of the business")
    category: str = Field(default="Other", description="Main sector: Food & Desserts, Beauty & Skincare, Home & Decor, Artisan Crafts, Services, Fashion")
    niche_tags: list[str] = Field(default_factory=list, description="Specific styles, products, or aesthetic tags")
    location: str = Field(default="Lebanon", description="City or neighborhood in Lebanon")
    price_tier: str = Field(default="$$", description="Budget tier: $, $$, or $$$")
    offers_delivery: bool = Field(default=False, description="True if delivery is mentioned/available")
    contact_channel: str = Field(default="Instagram DM", description="WhatsApp number or Instagram DM")

    # pre-processing rraw input 
    @field_validator("offers_delivery", mode="before")
    @classmethod
    def parse_delivery_bool(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            clean_str = value.strip().lower()
            if clean_str in ["true", "yes", "1", "available", "yes delivery"]:
                return True
        
        return False



load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)



def convert_doc_to_json(raw_text_filepath: str, output_json_filepath: str):
    with open(raw_text_filepath, "r", encoding="utf-8") as f:
        content = f.read()

    entries = [e.strip() for e in content.split("---") if e.strip()]
    structured_shops = []


    for idx, entry in enumerate(entries):
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a data extraction assistant for Lebanese Instagram small businesses.
Extract the raw input details into a JSON object matching this schema strictly:
{json.dumps(LocalBusinessSchema.model_json_schema(), indent=2)}"""
                    },
                    {"role": "user", "content": entry}
                ],
                temperature=0.1
            )

            raw_json = json.loads(completion.choices[0].message.content)
            validated_shop = LocalBusinessSchema(**raw_json).model_dump()
            
            structured_shops.append(validated_shop)
            print(f"✅ [{idx + 1}/{len(entries)}] Successfully parsed: {validated_shop['business_name']}")

        except Exception as e:
            print(f" [{idx + 1}/{len(entries)}] Error parsing entry: {e}")

    with open(output_json_filepath, "w", encoding="utf-8") as out_file:
        json.dump(structured_shops, out_file, indent=2, ensure_ascii=False)

   

if __name__ == "__main__":
    convert_doc_to_json("raw_data_shops.txt", "shops_database.json")