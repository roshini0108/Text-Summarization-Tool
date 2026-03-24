"""
Command-line interface for the Text Summarization Tool.
"""

import time
import warnings

from summarizer import compare_summaries_with_timing, summarize_text

warnings.filterwarnings("ignore")


SAMPLE_TEXT = """
Artificial intelligence is transforming the way people work, learn, and communicate.
Businesses use AI-powered tools to automate repetitive tasks, analyze large volumes of
data, and support decision-making. In education, intelligent tutoring systems help
students learn at their own pace by adapting lessons to individual strengths and
weaknesses. Healthcare providers rely on AI for faster diagnosis, medical image analysis,
and patient monitoring. At the same time, researchers and policymakers are discussing the
ethical risks of AI, including bias, privacy concerns, job displacement, and the need for
transparent systems. As adoption grows, the challenge is not only to make AI more
powerful, but also to ensure that it is used responsibly and benefits society as a whole.
""".strip()


def read_multiline_text():
    """
    Read multi-line text from the terminal until the user types END.
    """
    print("\nPaste or type your text below.")
    print("Type 'END' on a new line when you are finished.")
    print("Press Enter without typing anything to use the sample text.\n")

    lines = []

    while True:
        line = input()

        if not lines and not line.strip():
            return SAMPLE_TEXT, "Using sample text"

        if line.strip().upper() == "END":
            break

        lines.append(line)

    return "\n".join(lines).strip(), "User input"


def choose_method():
    """
    Ask the user which summarization method to use.
    """
    print("\n--- Select Summarization Method ---")
    print("1. Transformer summarization")
    print("2. NLTK extractive summarization")
    print("3. Compare both models")

    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice in {"1", "2", "3"}:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def choose_length():
    """
    Ask the user which summary length to generate.
    """
    print("\n--- Select Summary Length ---")
    print("1. Short")
    print("2. Medium")
    print("3. Long")

    length_map = {"1": "short", "2": "medium", "3": "long"}

    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice in length_map:
            return length_map[choice]
        print("Invalid choice. Please enter 1, 2, or 3.")


def get_method_name(method):
    """
    Convert the selected method into a readable name.
    """
    method_names = {
        "1": "Transformer",
        "2": "NLTK",
        "3": "Compare Both",
    }
    return method_names.get(method, "Unknown")


def print_single_result(original_text, summary, method_name, summary_length, input_type, elapsed_time):
    """
    Print a single summary result in a clear format.
    """
    label = "🤖 TRANSFORMER SUMMARY" if method_name == "Transformer" else "📊 NLTK SUMMARY"

    print("\n---")
    print(f"({input_type})")
    print(f"[Method: {method_name}]")
    print(f"[Length: {summary_length.title()}]")
    print(f"⏱ Time taken: {elapsed_time:.2f} seconds")
    print("\n📝 ORIGINAL TEXT")
    print(original_text)
    print("\n---")
    print(label)
    print(summary)


def print_comparison_result(original_text, results, summary_length, input_type):
    """
    Print both model summaries in a consistent format.
    """
    print("\n---")
    print(f"({input_type})")
    print("[Method: Compare Both]")
    print(f"[Length: {summary_length.title()}]")
    print(f"⏱ Transformer time: {results['transformer_time']:.2f} seconds")
    print(f"⏱ NLTK time: {results['nltk_time']:.2f} seconds")
    print("\n📝 ORIGINAL TEXT")
    print(original_text)
    print("\n---")
    print("🤖 TRANSFORMER SUMMARY")
    print(results["transformer"])
    print("\n---")
    print("📊 NLTK SUMMARY")
    print(results["nltk"])


def main():
    print("=== TEXT SUMMARIZATION TOOL ===")

    try:
        text, input_type = read_multiline_text()

        if not text.strip():
            print("\nNo input text provided.")
            return

        method = choose_method()
        summary_length = choose_length()
        method_name = get_method_name(method)

        print("\n--- Selected Options ---")
        print(f"Method: {method_name}")
        print(f"Length: {summary_length.title()}")
        print(f"Input: {input_type}")
        print("\nGenerating summary...")

        if method == "3":
            result = compare_summaries_with_timing(text, summary_length)
            print_comparison_result(text, result, summary_length, input_type)
        else:
            start_time = time.perf_counter()
            summary = summarize_text(
                text=text,
                method=method,
                summary_length=summary_length,
            )
            elapsed_time = time.perf_counter() - start_time

            print_single_result(
                original_text=text,
                summary=summary,
                method_name=method_name,
                summary_length=summary_length,
                input_type=input_type,
                elapsed_time=elapsed_time,
            )

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except Exception as error:
        print(f"\nAn unexpected error occurred: {error}")


if __name__ == "__main__":
    main()


# Instructions:
# 1. Install dependencies:
#    pip install -r requirements.txt
#
# 2. Run the script:
#    python main.py
