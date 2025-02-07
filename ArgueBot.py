import os
import argparse
import subprocess
import time
import re
import sys

def call_ollama(model_identifier, prompt):
    """
    Calls the Ollama CLI to generate text using a given model identifier.
    The prompt is passed via standard input.
    """
    full_cmd = ["ollama", "run", model_identifier]
    try:
        output = subprocess.check_output(full_cmd, input=prompt, text=True)
        return output.strip()
    except subprocess.CalledProcessError as e:
        print("Error calling Ollama:", e)
        return ""

def print_cool_text(text, char_delay=0.05, line_delay=0.8):
    """
    Prints text letter by letter with a delay, making it appear 'typed out'.
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(char_delay)
    print()  # Newline after the full sentence
    time.sleep(line_delay)

def get_first_three_sentences(response, model_name=""):
    """
    Splits the response into sentences and returns exactly the first three.
    Also removes self-references like 'Model A:'
    """
    # Strip unintended references to model names
    response = re.sub(rf'\b{model_name}\b[:]', '', response, flags=re.IGNORECASE)

    # Extract sentences
    sentences = re.split(r'(?<=[.!?])\s+', response)
    if len(sentences) >= 3:
        return " ".join(sentences[:3])  # Return first 3 sentences
    else:
        # If response is too short, force it to expand
        return response + " Expand on this idea. Provide more reasoning."

def debate_conversation(model_a_id, model_b_id, meta_prompt, perspective_a, perspective_b):
    """
    Simulates an **endless** debate between two LLMs running via Ollama.
    The meta prompt is **introduced first** to set the framing, then the user provides an argument.
    """
    # Start conversation with the meta prompt to establish debate framework
    conversation = meta_prompt
    print("\n=== Debate Framework Established ===")
    print("Meta Prompt:\n" + meta_prompt)

    # Build full debate context
    conversation += "\nModel A Perspective: " + perspective_a
    conversation += "\nModel B Perspective: " + perspective_b

    # Prompt the user for their initial debate argument.
    user_initial = input("\nEnter your initial debate argument: ").strip()
    if not user_initial:
        user_initial = "Let the debate begin!"

    # Add user input to the debate conversation.
    conversation += "\nUser Argument: " + user_initial
    print_cool_text("\nUser Argument: " + user_initial, char_delay=0.03)

    print("\n=== Debate Start ===")
    print("Model A Perspective:\n" + perspective_a)

    # Get the first argument from Model A using the **meta prompt + user input**
    print("\nCalling Model A for the initial argument...")
    initial_response = call_ollama(model_a_id, conversation)
    concise_initial = get_first_three_sentences(initial_response, "Model A")  # Remove self-references
    print("\nModel A initial response:")
    conversation += "\nModel A: " + concise_initial
    print_cool_text(concise_initial, char_delay=0.05)
    print("\nModel B Perspective:\n" + perspective_b)

    # Infinite debate loop
    turn = 1
    while True:
        print(f"\n--- Turn {turn} ---")

        print("Model B generating response...")
        response_b = call_ollama(model_b_id, conversation)
        concise_b = get_first_three_sentences(response_b, "Model B")  # Ensure 3 sentences
        print("Model B:")
        print_cool_text(concise_b, char_delay=0.05)
        conversation += "\nModel B: " + concise_b
        time.sleep(1)

        print("Model A generating response...")
        response_a = call_ollama(model_a_id, conversation)
        concise_a = get_first_three_sentences(response_a, "Model A")  # Ensure 3 sentences, remove self-references
        print("Model A:")
        print_cool_text(concise_a, char_delay=0.05)
        conversation += "\nModel A: " + concise_a
        time.sleep(1)

        turn += 1  # Infinite loop

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Debate between two LLMs via Ollama. The debate runs endlessly and expands logically."
    )
    parser.add_argument("--model_a", type=str,
                        default="llama3",
                        help="Ollama model identifier for Model A (e.g., Llama3).")
    parser.add_argument("--model_b", type=str,
                        default="llama3", 
                        help="Ollama model identifier for Model B (e.g., Llama3.")
    parser.add_argument("--meta_prompt_file", type=str,
                        default="/Users/miles/Code/ArgueBot-Royale/meta_prompt.txt", #REPLACE WITH YOUR DIR
                        help="Path to the meta prompt file.")
    parser.add_argument("--perspective_a_file", type=str,
                        default="/Users/miles/Code/ArgueBot-Royale/A_prompt.txt",
                        help="Path to perspective prompt for Model A.")
    parser.add_argument("--perspective_b_file", type=str,
                        default="/Users/miles/Code/ArgueBot-Royale/B_prompt.txt",
                        help="Path to perspective prompt for Model B.")

    args = parser.parse_args()

    def read_file(path):
        try:
            with open(path, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return ""

    meta_prompt = read_file(args.meta_prompt_file)
    perspective_a = read_file(args.perspective_a_file)
    perspective_b = read_file(args.perspective_b_file)

    debate_conversation(args.model_a, args.model_b, meta_prompt, perspective_a, perspective_b)
