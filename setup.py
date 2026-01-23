"""
Setup script for Sephira Orion
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from example if it doesn't exist"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists() and env_example_path.exists():
        print("📝 Creating .env file from .env.example...")
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file. Please edit it with your API keys.")
        return False
    elif env_path.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False


def create_directories():
    """Create necessary directories"""
    dirs = [
        "data/raw",
        "data/processed",
        "data/chroma",
        "logs"
    ]
    
    print("\n📁 Creating directories...")
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")


def check_csv_file():
    """Check if CSV data file exists"""
    csv_path = Path("data/raw/all_indexes_beta.csv")
    
    print("\n📊 Checking for sentiment data...")
    if csv_path.exists():
        print(f"  ✅ Found data file: {csv_path}")
        return True
    else:
        print(f"  ⚠️  Data file not found: {csv_path}")
        print("  Please copy your all_indexes_beta.csv to data/raw/")
        return False


def run_data_processing():
    """Run data processing"""
    print("\n🔄 Processing data and creating chunks...")
    
    try:
        from backend.services.data_loader import main as process_data
        process_data()
        print("✅ Data processing complete")
        return True
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return False


def generate_embeddings():
    """Generate embeddings and populate vector database"""
    print("\n🧠 Generating embeddings and populating vector database...")
    print("⚠️  This may take several minutes and requires OpenAI API key...")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("⏭️  Skipping embedding generation. You can run it later with:")
        print("   python -m backend.services.embeddings")
        return False
    
    try:
        from backend.services.embeddings import load_and_embed_data
        load_and_embed_data()
        print("✅ Embeddings generated successfully")
        return True
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False


def main():
    """Main setup function"""
    print("="*60)
    print("   🚀 Sephira Orion Setup")
    print("="*60)
    
    # Create directories
    create_directories()
    
    # Create .env file
    has_env = create_env_file()
    
    if not has_env:
        print("\n⚠️  Please edit .env file with your API keys before continuing")
        print("   Required: OPENAI_API_KEY")
        print("   Optional: NEWS_API_KEY, ALPHA_VANTAGE_KEY, FRED_API_KEY")
        sys.exit(0)
    
    # Check for CSV file
    has_csv = check_csv_file()
    
    if not has_csv:
        print("\n⚠️  Please copy your sentiment data CSV before continuing")
        sys.exit(0)
    
    # Process data
    data_processed = run_data_processing()
    
    if not data_processed:
        print("\n❌ Setup incomplete - data processing failed")
        sys.exit(1)
    
    # Generate embeddings
    embeddings_done = generate_embeddings()
    
    # Final instructions
    print("\n" + "="*60)
    print("   ✅ Setup Complete!")
    print("="*60)
    print("\n📖 Next Steps:")
    print("\n1. Start the backend:")
    print("   uvicorn backend.api.main:app --reload --port 8000")
    print("\n2. In a new terminal, start the frontend:")
    print("   streamlit run frontend/app.py")
    print("\n3. Access the application:")
    print("   Frontend: http://localhost:8501")
    print("   API Docs: http://localhost:8000/docs")
    
    if not embeddings_done:
        print("\n⚠️  Remember to generate embeddings before using the system:")
        print("   python -m backend.services.embeddings")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
