import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from openai import OpenAI
# Load environment variables from a .env file if present

TEMPLATE_PATH = Path(__file__).parent / "init_db.py"
OUTPUT_SCRIPT = Path("generated_init_db.py")


def create_database(user_request: str, db_path: str) -> tuple[bool, str]:
    """Generate and run a DB init script via OpenAI."""
    print(f"db_path: {db_path}") 
    load_dotenv()  # Load environment variables from .env file if it exists 
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    if not api_key:
        return False, "OPENAI_API_KEY environment variable not set"


    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = (
        "You are an assistant that generates Python scripts to create SQLite databases.\n"
        "Use the following template as a inspiration.\n"
        "The script should write to the path provided in DB_PATH and, if requested, populate it with random data.\n"
        "The DB_PATH should be the first argument to the script.\n"
        "Template:\n" + template + "\n" +
        "User request:\n" + user_request + "\n"
        "Provide only the Python code in your response. The Python code should be a complete script that can be run to create the database.\n"
    )

    try:
        response = client.chat.completions.create(model="gpt-4.1-mini-2025-04-14",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2)
    except Exception as e:
        return False, f"OpenAI API call failed: {e}"

    code = response.choices[0].message.content
    if code.startswith("```python"):
        code = code[10:]
    if code.endswith("```"):
        code = code[:-3]
    try:
        OUTPUT_SCRIPT.write_text(code, encoding="utf-8")
    except Exception as e:
        return False, f"Failed to save generated script: {e}"
    
    try:
        subprocess.run(["python", str(OUTPUT_SCRIPT), db_path], check=True)
    except subprocess.CalledProcessError as e:
        return False, f"Generated script failed: {e}"

    if Path(db_path).exists():
        return True, f"Database created at {db_path}"
    return False, "Script ran but database was not created"


def main():
    target_db = input("Name of the database file to create (e.g. new.db): ").strip()
    if not target_db:
        print("No database name provided")
        return

    user_req = input(
        "Describe the desired database schema and whether to populate it with random data:\n"
    )

    success, msg = create_database(user_req, target_db)
    print(msg)


if __name__ == "__main__":
    main()
