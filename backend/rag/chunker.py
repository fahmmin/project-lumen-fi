"""
PROJECT LUMEN - Text Chunking
Intelligent text chunking for RAG pipeline
"""

from typing import List, Dict
import re
from backend.config import settings
from backend.utils.logger import logger


class TextChunker:
    """Handles intelligent text chunking with overlap"""

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text:
            return []

        # Clean text
        text = self._clean_text(text)

        # Try sentence-based chunking first
        chunks = self._smart_chunk(text)

        # Add metadata
        chunk_dicts = []
        for idx, chunk_text in enumerate(chunks):
            chunk_dict = {
                'text': chunk_text,
                'chunk_id': idx,
                'char_count': len(chunk_text),
                'metadata': metadata or {}
            }
            chunk_dicts.append(chunk_dict)

        logger.info(f"Created {len(chunk_dicts)} chunks from {len(text)} characters")
        return chunk_dicts

    def _clean_text(self, text: str) -> str:
        """Clean text before chunking"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _smart_chunk(self, text: str) -> List[str]:
        """
        Smart chunking that tries to respect sentence boundaries

        Args:
            text: Input text

        Returns:
            List of text chunks
        """
        # Split into sentences
        sentences = self._split_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If single sentence exceeds chunk size, split it
            if sentence_length > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # Split long sentence into smaller parts
                sub_chunks = self._split_long_sentence(sentence)
                chunks.extend(sub_chunks)
                continue

            # Check if adding sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size:
                # Save current chunk
                chunks.append(' '.join(current_chunk))

                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(' '.join(current_chunk))
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with spaCy/NLTK)
        sentence_endings = re.compile(r'([.!?])\s+')
        sentences = sentence_endings.split(text)

        # Recombine sentences with their punctuation
        result = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i] + sentences[i + 1]
            result.append(sentence.strip())

        # Add last sentence if exists
        if len(sentences) % 2 == 1:
            result.append(sentences[-1].strip())

        return [s for s in result if s]

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """
        Split a sentence that exceeds chunk size

        Args:
            sentence: Long sentence

        Returns:
            List of sub-chunks
        """
        words = sentence.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space

            if current_length + word_length > self.chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _get_overlap(self, chunk_sentences: List[str]) -> str:
        """
        Get overlap text from previous chunk

        Args:
            chunk_sentences: List of sentences in current chunk

        Returns:
            Overlap text
        """
        if not chunk_sentences:
            return ""

        overlap_text = ""
        overlap_length = 0

        # Take sentences from end until we reach overlap size
        for sentence in reversed(chunk_sentences):
            if overlap_length + len(sentence) <= self.chunk_overlap:
                overlap_text = sentence + " " + overlap_text
                overlap_length += len(sentence)
            else:
                break

        return overlap_text.strip()


# Convenience function
def chunk_document(text: str, metadata: Dict = None) -> List[Dict]:
    """
    Chunk a document with default settings

    Args:
        text: Document text
        metadata: Optional metadata

    Returns:
        List of chunks
    """
    chunker = TextChunker()
    return chunker.chunk_text(text, metadata)
