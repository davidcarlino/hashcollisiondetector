import hashlib
import os

# --- Configuration ---
TEXT1_PATH = 'text_files/text1.txt'
TEXT2_PATH = 'text_files/text2.txt'
RESULTS_DIR = 'results'
MAX_SEARCH_ITERATIONS = 2_000_000 # Max variations to try for each file

# --- Main Script ---
def find_best_collision(max_digits=8, min_digits=3):
    """
    Finds the best possible hash collision by searching from max_digits down to min_digits.
    """
    with open(TEXT1_PATH, 'r') as f:
        base_text1 = f.read()

    with open(TEXT2_PATH, 'r') as f:
        base_text2 = f.read()

    for num_digits in range(max_digits, min_digits - 1, -1):
        print(f"\n--- Attempting to find a collision for {num_digits} hex digits ---")
        hashes = {}
        
        # Phase 1: Generate hashes for the first file
        print(f"Phase 1: Generating up to {MAX_SEARCH_ITERATIONS:,} hashes for the first file...")
        for nonce1 in range(MAX_SEARCH_ITERATIONS):
            text_to_hash = base_text1 + str(nonce1)
            hashed_text = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()
            hash_suffix = hashed_text[-num_digits:]
            if hash_suffix not in hashes:
                hashes[hash_suffix] = nonce1

        # Phase 2: Search for a collision with the second file
        print(f"Phase 2: Searching for a {num_digits}-digit collision with the second file...")
        for nonce2 in range(MAX_SEARCH_ITERATIONS):
            text_to_hash = base_text2 + str(nonce2)
            hashed_text = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()
            hash_suffix = hashed_text[-num_digits:]

            if hash_suffix in hashes:
                matching_nonce1 = hashes[hash_suffix]
                colliding_text1 = base_text1 + str(matching_nonce1)
                colliding_text2 = base_text2 + str(nonce2)

                hash1 = hashlib.sha256(colliding_text1.encode('utf-8')).hexdigest()
                hash2 = hashlib.sha256(colliding_text2.encode('utf-8')).hexdigest()

                print("\nCollision found!")
                
                result_content = (
                    f"Collision found with {num_digits} matching hex digits: {hash_suffix}\n"
                    f"--------------------------------------------------\n"
                    f"File 1 :\n"
                    f"Content: {colliding_text1}\n"
                    f"Full Hash: {hash1}\n"
                    f"--------------------------------------------------\n"
                    f"File 2 :\n"
                    f"Content: {colliding_text2}\n"
                    f"Full Hash: {hash2}\n"
                )
                
                print(result_content)
                
                with open(os.path.join(RESULTS_DIR, 'collision_results.txt'), 'w') as f:
                    f.write(result_content)
                
                print(f"Results saved to {os.path.join(RESULTS_DIR, 'collision_results.txt')}")
                return # Exit after finding the best possible collision

    print("\nCould not find a collision within the specified search limits.")


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
