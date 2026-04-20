# Character-level tokenizer for our model

import json
from pathlib import Path

class CharacterTokenizer:
    def __init__(self, stoi: dict[str, int], itos: dict[int, str]) -> None:
        # stoi = string-to-index, itos = index-to-string
        # Keeping both mappings makes encoding and decoding straightforward
        self.stoi = stoi
        self.itos = itos
        self.vocab_size = len(stoi)
        
    @classmethod
    def from_text(cls, text: str) -> "CharacterTokenizer":
        # Build the vocabulary from all unique characters in sorted order
        # Sorting keeps tokenizer creation deterministic
        chars = sorted(set(text))
        
        stoi = {char: index for index, char in enumerate(chars)}
        itos = {index: char for char, index in stoi.items()}
        
        return cls(stoi=stoi, itos=itos)
    
    def encode(self, text: str) -> list[int]:
        # Convert each character into its integer ID
        # This will raise a KeyError if the tokenizer sees an unknown character
        return [self.stoi[char] for char in text]
    
    def decode(self, token_ids: list[int]) -> str:
        # Convert integer IDs back into characters, then join them into text
        return "".join(self.itos[token_id] for token_id in token_ids)

    def save(self, path: str | Path) -> None:
        # Save the vocabulary so training and generation use the exact same tokenizer
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        payload = {
            "stoi": self.stoi,
        }
        
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        
    @classmethod
    def load(cls, path: str | Path) -> "CharacterTokenizer":
        # Rebuild the tokenizer from a saed vocabulary file
        path = Path(path)
        
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
            
        stoi = {char: int(index) for char, index in payload["stoi"].items()}
        itos = {index: char for char, index in stoi.items()}
        
        return cls(stoi=stoi, itos=itos)