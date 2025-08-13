import argparse
import os
from model_crypter import ModelEncrypter

def main():
    parser = argparse.ArgumentParser(description="A tool to encrypt and decrypt machine learning model weights.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Encrypt command ---
    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt a model file.")
    parser_encrypt.add_argument("--input", "-i", type=str, required=True, help="Path to the model file to encrypt.")
    parser_encrypt.add_argument("--key", "-k", type=str, required=True, help="The secret key for encryption.")

    # --- Decrypt command ---
    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt a model file.")
    parser_decrypt.add_argument("--input", "-i", type=str, required=True, help="Path to the .secret file to decrypt.")
    parser_decrypt.add_argument("--output", "-o", type=str, required=True, help="Path to save the decrypted model file.")
    parser_decrypt.add_argument("--key", "-k", type=str, required=True, help="The secret key for decryption.")
    
    args = parser.parse_args()

    # --- Input file validation ---
    if not os.path.exists(args.input):
        print(f"Error: Input file not found at '{args.input}'")
        return
        
    encrypter = ModelEncrypter(key=args.key)

    if args.command == "encrypt":
        encrypter.encrypt(args.input)
    elif args.command == "decrypt":
        try:
            decrypted_data = encrypter.decrypt(args.input)
            encrypter._save_file(args.output, decrypted_data)
            print(f"✅ Decrypted model saved successfully to: {args.output}")
        except Exception as e:
            print(f"❌ Decryption failed: {e}")

if __name__ == "__main__":
    main()
