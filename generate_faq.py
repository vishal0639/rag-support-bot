"""
FAQ Generator: Creates FAQ document from common questions
This script generates a Markdown FAQ document by asking questions to the RAG system
"""
from rag_engine import RAGEngine
from typing import List
import json
import argparse
from datetime import datetime


class FAQGenerator:
    """Generates FAQ documents from a list of questions"""
    
    def __init__(self):
        self.rag_engine = RAGEngine()
    
    def generate_faq(
        self, 
        questions: List[str], 
        output_file: str = "FAQ.md",
        title: str = "Frequently Asked Questions"
    ) -> str:
        """
        Generate FAQ document from list of questions
        
        Args:
            questions: List of questions to answer
            output_file: Output file path (default: FAQ.md)
            title: Document title
            
        Returns:
            Path to generated FAQ file
        """
        # Check if vector store has data
        count = self.rag_engine.vector_store.get_collection_count()
        if count == 0:
            print("ERROR: Vector store is empty. Please run the indexer first!")
            print("Run: python indexer.py --reset")
            return None
        
        print(f"Generating FAQ for {len(questions)} questions...")
        print(f"Vector store has {count} chunks")
        print("=" * 60)
        
        # Build FAQ content
        faq_content = f"# {title}\n\n"
        faq_content += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        faq_content += f"*Based on {count} indexed content chunks*\n\n"
        faq_content += "---\n\n"
        
        # Process each question
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] Processing: {question}")
            
            try:
                # Get answer from RAG engine
                result = self.rag_engine.answer_question(question)
                
                # Add to FAQ
                faq_content += f"## {i}. {question}\n\n"
                faq_content += f"{result['answer']}\n\n"
                
                # Add sources if available
                if result['sources']:
                    faq_content += "**Sources:**\n\n"
                    for source in result['sources']:
                        faq_content += f"- [{source['title']}]({source['url']})\n"
                    faq_content += "\n"
                
                faq_content += "---\n\n"
                
                print(f"✓ Answer generated ({len(result['sources'])} sources)")
                
            except Exception as e:
                print(f"✗ Error: {str(e)}")
                faq_content += f"## {i}. {question}\n\n"
                faq_content += f"*Error generating answer: {str(e)}*\n\n"
                faq_content += "---\n\n"
        
        # Add footer
        faq_content += "\n---\n\n"
        faq_content += "*This FAQ was automatically generated using the RAG Support Bot.*\n"
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(faq_content)
        
        print("\n" + "=" * 60)
        print(f"✓ FAQ generated successfully: {output_file}")
        print("=" * 60)
        
        return output_file
    
    def load_questions_from_file(self, filepath: str) -> List[str]:
        """
        Load questions from a file
        
        Supports:
        - Plain text file (one question per line)
        - JSON file (array of strings)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try JSON first
        try:
            questions = json.loads(content)
            if isinstance(questions, list):
                return questions
        except json.JSONDecodeError:
            pass
        
        # Fall back to plain text (one question per line)
        questions = [line.strip() for line in content.split('\n')]
        questions = [q for q in questions if q and not q.startswith('#')]
        
        return questions


def main():
    """Main entry point for the FAQ generator"""
    parser = argparse.ArgumentParser(
        description='Generate FAQ document from questions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate FAQ from built-in example questions
  python generate_faq.py
  
  # Generate FAQ from questions file
  python generate_faq.py --input questions.txt --output my_faq.md
  
  # Specify custom title
  python generate_faq.py --title "Product FAQ" --output product_faq.md
  
Questions file format (text):
  What is this product?
  How do I get started?
  What are the pricing options?
  
Questions file format (JSON):
  ["What is this product?", "How do I get started?", "What are the pricing options?"]
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input file with questions (txt or json)',
        default=None
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output FAQ file path (default: FAQ.md)',
        default='FAQ.md'
    )
    parser.add_argument(
        '--title', '-t',
        type=str,
        help='FAQ document title',
        default='Frequently Asked Questions'
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = FAQGenerator()
    
    # Get questions
    if args.input:
        print(f"Loading questions from: {args.input}")
        questions = generator.load_questions_from_file(args.input)
    else:
        # Default example questions
        print("Using example questions (use --input to load from file)")
        questions = [
            "What is this website about?",
            "How do I get started?",
            "What are the main features?",
            "Is there a free trial?",
            "How much does it cost?",
            "What payment methods are accepted?",
            "Is there customer support available?",
            "What are the system requirements?",
            "How do I contact support?",
            "Are there any tutorials or documentation?",
        ]
    
    if not questions:
        print("ERROR: No questions found!")
        return
    
    print(f"Found {len(questions)} questions")
    
    # Generate FAQ
    output_file = generator.generate_faq(
        questions=questions,
        output_file=args.output,
        title=args.title
    )
    
    if output_file:
        print(f"\nYou can view the FAQ at: {output_file}")


if __name__ == "__main__":
    main()

