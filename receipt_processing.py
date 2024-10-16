import os
import sqlite3
from langchain.prompts import PromptTemplate
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods, ModelTypes
from ibm_watsonx_ai import Credentials
from langchain_ibm import WatsonxLLM
from langchain.chains import LLMChain

# Global variables
watsonx_llm = None

# Database setup
def setup_database():
    conn = sqlite3.connect('carbon_footprints.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            carbon_footprint REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def insert_receipt_data(conn, item_name, carbon_footprint, category):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO receipts (item_name, carbon_footprint, category)
        VALUES (?, ?, ?)
    ''', (item_name, carbon_footprint, category))
    conn.commit()

def setup_watsonx():
    global watsonx_llm
    try:
        print("Setting up WatsonX...")
        credentials = Credentials(
            url="https://us-south.ml.cloud.ibm.com",
            api_key="yoxxhnuME6orab5ZohM5Y93KTzRrWUP8kSM_Tm44sSd6"
        )

        project_id = os.environ.get("PROJECT_ID", "84b7e606-8040-40f9-a60e-02264e8d20a6")

        model_id = ModelTypes.GRANITE_13B_CHAT_V2
        parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 500,
            GenParams.STOP_SEQUENCES: ["Human:", "Receipt:", "Total"]
        }
        watsonx_llm = WatsonxLLM(
            model_id=model_id.value,
            url=credentials.get("url"),
            apikey=credentials.get("apikey"),
            project_id=project_id,
            params=parameters
        )
        print("WatsonX set up successfully.")
        return True, "WatsonX set up successfully."
    except Exception as e:
        print(f"Error setting up WatsonX: {str(e)}")
        return False, f"Error setting up WatsonX: {str(e)}"

def initialize_system():
    return setup_watsonx()

def process_receipt(receipt_text, receipt_id, conn):
    print("Processing receipt...")

    prompt_template = PromptTemplate(
        input_variables=["receipt"],
        template="""
Analyze the following receipt and perform these tasks:
1. Identify all purchased items (products) from the receipt.
2. For each identified item, calculate its carbon footprint in kg CO2e based on the quantity.
3. Classify each item into one of the following categories based on your knowledge:
   - Personal (groceries, food, and clothing)
   - Flight travel
   - Electricity
   - Vehicle (fuel, maintenance)

When calculating the carbon footprint:
- Use the first number after the identified product without a currency symbol as the weight/quantity.
- If only a cost per unit and total cost are given, calculate the quantity from that.
- Consider the nature of the item (e.g., dairy, meat, produce, packaged goods).
- Factor in typical production and transportation methods for this type of item.

Receipt:
{receipt}

Format your response as follows for each item, with no additional explanation:
Item Name: Carbon Footprint (kg CO2e) : Category
No need to return any calculations just return the final calculated carbon footprints for each of them.

Your response:
"""
    )

    llm_chain = LLMChain(llm=watsonx_llm, prompt=prompt_template)
    response = llm_chain.run(receipt=receipt_text)

    print("Receipt processing complete. Results:")
    return response.strip()

def format_carbon_footprint(data, conn):
    # Initialize total footprint
    total_carbon_footprint = 0
    
    # Split the data into lines
    lines = data.split('\n')
    
    # Iterate through each line
    for line in lines:
        # Split the line into multiple parts if there are multiple "Item Name" entries
        items = line.split("Item Name:")
        
        # Process each item, skipping the first part which might be empty
        for item in items[1:]:
            # Extract item name, carbon footprint, and category
            parts = item.split(':')
            if len(parts) >= 3:
                item_name = parts[0].strip()
                carbon_footprint_str = parts[1].strip().replace("kg CO2e", "").strip()
                category = parts[2].strip()
                
                # Convert to float and handle any possible errors
                try:
                    carbon_footprint = float(carbon_footprint_str)
                    # Insert data into the database
                    insert_receipt_data(conn, item_name, carbon_footprint, category)
                except ValueError:
                    print(f"Error converting carbon footprint for {item_name}: {carbon_footprint_str}")
                    continue
                
                # Print formatted output
                print(f"{item_name}: {carbon_footprint:.3f} kg CO2e - Category: {category}")
                
                # Add to total carbon footprint
                total_carbon_footprint += carbon_footprint
    
    # Print total carbon footprint
    print(f"\nTotal Carbon Footprint: {total_carbon_footprint:.3f} kg CO2e")

if __name__ == "__main__":
    print("Starting script execution...")
    try:
        conn = setup_database()  # Set up the database
        success, message = initialize_system()
        if success:
            print("System initialized. Ready to process receipts.")
            # Example usage; replace with actual receipt extraction logic
            receipt_text = """<Your Receipt Text Here>"""
            receipt_id = 1  # Example receipt ID; replace as needed
            result = process_receipt(receipt_text, receipt_id, conn)
            format_carbon_footprint(result, conn)

        else:
            print(f"Failed to initialize system: {message}")
    except Exception as e:
        print(f"An error occurred during execution: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    print("Script execution completed.")

