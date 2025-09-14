import hashlib
import os
import sys

# Platform-specific modules for non-blocking input
try:
    import termios
    import tty
    import select
    UNIX_SYSTEM = True
except ImportError:
    UNIX_SYSTEM = False
    try:
        import msvcrt
    except ImportError:
        msvcrt = None # msvcrt is not available on this system

# --- Configuration ---
TEXT1_PATH = 'text_files/text1.txt'
TEXT2_PATH = 'text_files/text2.txt'
RESULTS_DIR = 'results'
MAX_SEARCH_ITERATIONS = 1_000_000 # Max newlines to try for each file

# --- Main Script ---
def is_q_pressed():
    """Check if 'q' has been pressed without blocking, in a cross-platform way."""
    if UNIX_SYSTEM:
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            char = sys.stdin.read(1)
            return char.lower() == 'q'
    elif msvcrt:
        if msvcrt.kbhit():
            char = msvcrt.getch()
            return char.lower() == b'q'
    return False

def find_best_collision(max_digits=8, min_digits=3):
    """
    Finds the best possible hash collision by adding newlines.
    """
    old_settings = None
    if UNIX_SYSTEM:
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    try:
        if UNIX_SYSTEM or msvcrt:
            print("*** Press 'q' at any time to cancel the search ***")
        else:
            print("*** Non-blocking input not supported. Cannot cancel search with 'q'. ***")

        with open(TEXT1_PATH, 'r') as f:
            base_text1 = f.read()

        with open(TEXT2_PATH, 'r') as f:
            base_text2 = f.read()

        for num_digits in range(max_digits, min_digits - 1, -1):
            print(f"\n--- Attempting to find a collision for {num_digits} hex digits using newlines ---")
            hashes = {}
            
            # Phase 1: Generate hashes for the first file
            print(f"Phase 1: Generating up to {MAX_SEARCH_ITERATIONS:,} hashes for the first file... PRESS Q TO CANCEL")
            for nonce1 in range(MAX_SEARCH_ITERATIONS):
                if nonce1 % 10000 == 0 and is_q_pressed():
                    print("\nSearch cancelled by user.")
                    return
                # Add newlines instead of numbers
                text_to_hash = base_text1 + ('\n' * nonce1)
                hashed_text = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()
                hash_suffix = hashed_text[-num_digits:]
                if hash_suffix not in hashes:
                    hashes[hash_suffix] = nonce1

            # Phase 2: Search for a collision with the second file
            print(f"Phase 2: Searching for a {num_digits}-digit collision with the second file... PRESS Q TO CANCEL")
            for nonce2 in range(MAX_SEARCH_ITERATIONS):
                if nonce2 % 10000 == 0 and is_q_pressed():
                    print("\nSearch cancelled by user.")
                    return
                # Add newlines instead of numbers
                text_to_hash = base_text2 + ('\n' * nonce2)
                hashed_text = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()
                hash_suffix = hashed_text[-num_digits:]

                if hash_suffix in hashes:
                    matching_nonce1 = hashes[hash_suffix]
                    colliding_text1 = base_text1 + ('\n' * matching_nonce1)
                    colliding_text2 = base_text2 + ('\n' * nonce2)

                    hash1 = hashlib.sha256(colliding_text1.encode('utf-8')).hexdigest()
                    hash2 = hashlib.sha256(colliding_text2.encode('utf-8')).hexdigest()

                    print("\nCollision found!")
                    
                    result_content = (
                        f"Collision found with {num_digits} matching hex digits: {hash_suffix}\n"
                        f"(Method: Adding newlines)\n"
                        f"--------------------------------------------------\n"
                        f"File 1:\n"
                        f"Newlines Added: {matching_nonce1}\n"
                        f"Full Hash: {hash1}\n"
                        f"--------------------------------------------------\n"
                        f"File 2:\n"
                        f"Newlines Added: {nonce2}\n"
                        f"Full Hash: {hash2}\n"
                    )
                    
                    print(result_content)
                    
                    with open(os.path.join(RESULTS_DIR, 'collision_results.txt'), 'w') as f:
                        f.write(result_content)
                    
                    print(f"Results saved to {os.path.join(RESULTS_DIR, 'collision_results.txt')}")
                    return # Exit after finding the best possible collision

        print("\nCould not find a collision within the specified search limits.")

    finally:
        if UNIX_SYSTEM and old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def main():
    """Main function to set up and run the collision search."""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    # Wipe previous results if they exist
    result_file_path = os.path.join(RESULTS_DIR, 'collision_results.txt')
    if os.path.exists(result_file_path):
        os.remove(result_file_path)
        print("Wiped previous collision results.")

    find_best_collision()

if __name__ == "__main__":
    main()
