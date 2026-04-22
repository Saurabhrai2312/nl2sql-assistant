from groq import Groq
import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Cache for schema
_schema_cache = None

def get_database_schema():
    """Fetch the entire database schema from Snowflake"""
    global _schema_cache
    if _schema_cache:
        return _schema_cache
    
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    cursor = conn.cursor()
    
    # Get all tables in the database
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = CURRENT_SCHEMA() 
        AND TABLE_TYPE = 'BASE TABLE'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_info = "Database Schema:\n\n"
    
    for table in tables:
        schema_info += f"Table: {table}\n"
        schema_info += "Columns:\n"
        
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table}' 
            AND TABLE_SCHEMA = CURRENT_SCHEMA()
            ORDER BY ORDINAL_POSITION
        """)
        
        for col_name, col_type in cursor.fetchall():
            schema_info += f"  - {col_name} ({col_type})\n"
        schema_info += "\n"
    
    conn.close()
    _schema_cache = schema_info
    return schema_info

def run_query(sql):
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return columns, rows

def generate_sql(question, schema):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""You are a Snowflake SQL expert.

Here is the database schema:
{schema}

Write ONLY a valid Snowflake SQL query for this question.
Return just the SQL query, nothing else, no explanation, no markdown, no backticks.

Question: {question}"""
        }]
    )
    return response.choices[0].message.content.strip()

def explain_results(question, columns, rows):
    data = f"Columns: {columns}\nRows: {rows}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""Question asked: "{question}"

Query results:
{data}

Give a clear, friendly 2-3 sentence business answer based on this data."""
        }]
    )
    return response.choices[0].message.content.strip()

def main():
    print("\n🤖 NL2SQL Assistant — Ask questions about your database!")
    print("Type 'quit' to exit\n")
    
    print("⏳ Fetching database schema...")
    try:
        schema = get_database_schema()
        print("✅ Schema loaded successfully!\n")
    except Exception as e:
        print(f"\n❌ Error fetching schema: {e}")
        print("\nPlease verify:")
        print("  1. Your .env file exists with correct credentials")
        print("  2. GROQ_API_KEY is set")
        print("  3. All SNOWFLAKE_* variables are set correctly")
        print("  4. You have permission to access INFORMATION_SCHEMA\n")
        return

    while True:
        question = input("💬 Your question: ").strip()
        if question.lower() == 'quit':
            break
        if not question:
            continue

        try:
            print("\n⏳ Generating SQL...")
            sql = generate_sql(question, schema)
            print(f"\n📝 Generated SQL:\n{sql}")

            print("\n⏳ Running on Snowflake...")
            columns, rows = run_query(sql)
            print(f"📊 {len(rows)} row(s) returned\n")

            # Display results in table format
            if rows:
                print("📋 Raw Results:")
                print("=" * 120)
                # Print column headers
                headers = " | ".join(f"{str(col)[:15].center(15)}" for col in columns)
                print(headers)
                print("=" * 120)
                # Print rows
                for row in rows:
                    formatted_row = " | ".join(f"{str(val)[:15].center(15)}" for val in row)
                    print(formatted_row)
                print("=" * 120 + "\n")
            else:
                print("⚠️  No results found.\n")

            print("\n⏳ Generating answer...")
            answer = explain_results(question, columns, rows)
            print(f"\n✅ Summary: {answer}")
            print("\n" + "─"*50)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try rephrasing your question\n")

if __name__ == "__main__":
    main()