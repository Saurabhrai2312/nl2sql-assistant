# NL2SQL Assistant

Ever wished you could just ask your database a question instead of writing SQL? That's what this does. You ask in English, it writes the SQL, runs it on Snowflake, and gives you the answer.

## What Can You Do

- **Ask questions in plain English** - No need to know SQL syntax
- **Works with your entire database** - Not just one table, the whole thing
- **Handles multi-table queries** - If your question needs data from multiple tables, it figures it out
- **See both the data and the summary** - Get the raw results plus a human-friendly explanation

## What You Need

- Python 3.8 or higher
- A Snowflake account with some data in it
- A Groq API key (free, grab it from https://console.groq.com)

## Getting Started

1. **Clone this repo**
   ```bash
   git clone https://github.com/Saurabhrai2312/nl2sql-assistant.git
   cd nl2sql-assistant
   ```

2. **Install the packages**
   ```bash
   pip install groq snowflake-connector-python python-dotenv
   ```

3. **Create a `.env` file** and add your credentials:
   ```env
   GROQ_API_KEY=your_key_here
   
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_WAREHOUSE=your_warehouse
   ```

4. **Run it**
   ```bash
   python main.py
   ```

## How to Use It

Just run the script and start asking questions:

```
🤖 NL2SQL Assistant — Ask questions about your database!

💬 Your question: Who are the top 10 customers by total spending?
```

### Example Questions

Single table stuff:
- "How many pending orders do we have?"
- "What's the total revenue from laptop sales?"
- "Show me all customers from the North region"

Join multiple tables:
- "Give me orders with customer names and what they bought"
- "Show me top customers and their purchase history"
- "Find all customers from the North region with completed orders"

### What You'll Get

It shows you:
1. The SQL it wrote
2. All the results in a nice table
3. A summary explaining what the data means

## How It Actually Works

1. You ask a question
2. It grabs your entire database schema
3. Groq's AI (llama model) reads your question + schema and writes the SQL
4. SQL runs on Snowflake
5. You get the raw results + a friendly explanation

Pretty simple. The smarter your table names and column names are, the better it works.

## What's Inside

- `main.py` - The main script. That's it.
- `get_database_schema()` - Fetches all your tables and columns
- `generate_sql()` - Asks AI to write the query
- `run_query()` - Runs it on Snowflake
- `explain_results()` - Explains what the data means

## Environment Variables (.env)

```
GROQ_API_KEY              - Your Groq API key
SNOWFLAKE_USER            - Your Snowflake username
SNOWFLAKE_PASSWORD        - Your Snowflake password
SNOWFLAKE_ACCOUNT         - Your account ID (from Snowflake)
SNOWFLAKE_DATABASE        - The database you want to query
SNOWFLAKE_SCHEMA          - Usually "PUBLIC"
SNOWFLAKE_WAREHOUSE       - Which warehouse to use
```

## Tips for Better Results

- Use descriptive names for your tables and columns. `customer_name` is better than `cn`
- Be specific. "Top 10 customers by spending" works better than "top customers"
- Mention table names if you're not sure. "From ORDERS table, show me..." helps
- Give context. "In the last 30 days" or "from North region" helps narrow things down

## Troubleshooting

**Schema fetch fails?**
- Double-check your credentials in `.env`
- Make sure you have permission to read `INFORMATION_SCHEMA`
- Is your warehouse actually running?

**AI picked the wrong table?**
- Ask more specifically or mention the table name in your question
- Check your table names - obvious names help the AI

**SQL error when running?**
- Check the SQL it generated - is it valid?
- Do those tables and columns actually exist?
- Do you have permission to select from them?

## What It Uses

- Groq API (the llama model) for SQL generation
- Snowflake for running queries
- Python with some basic libraries

## What It Can't Do (Yet)

- Only SELECT queries, no INSERT/UPDATE/DELETE
- Limited by Snowflake's normal query limits
- Only as good as your database schema names

## What Could Be Cool to Add

- Support for writing data (INSERT/UPDATE)
- Caching so repeated questions are faster
- Export to CSV
- Maybe a web interface?

## License

MIT - use it how you want

## Got Issues?

Check your credentials are right, make sure your Snowflake connection works, and that the Groq API is responding.

Made by [Saurabh Rai](https://github.com/Saurabhrai2312)
