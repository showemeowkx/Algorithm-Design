import os
import tempfile
import heapq
from typing import List, Tuple, TextIO
import math

class AdaptiveExternalSort:
    def __init__(self, max_memory_mb: int = 250):
        """
        Initialize the external sorter.
        
        Args:
            max_memory_mb: Maximum memory to use in MB (default 250MB, leaving buffer)
        """
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.temp_file1 = None
        self.temp_file2 = None
        
    def parse_line(self, line: str) -> Tuple[int, str]:
        """Parse a line and return (key, original_line) tuple."""
        key = int(line.split(' - ')[0])
        return (key, line.rstrip('\n'))
    
    def estimate_lines_per_chunk(self, filepath: str) -> int:
        """
        Estimate how many lines can fit in memory based on file size.
        """
        # Sample first 1000 lines to estimate average line size
        sample_size = 0
        line_count = 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 1000:
                    break
                sample_size += len(line.encode('utf-8'))
                line_count += 1
        
        if line_count == 0:
            return 1000
        
        avg_line_size = sample_size / line_count
        # Account for tuple overhead and parsed data structure
        # Each line becomes (int, str) tuple with additional overhead
        memory_per_line = avg_line_size + 100  # Add overhead for structures
        
        lines_per_chunk = int(self.max_memory_bytes / memory_per_line)
        return max(1000, lines_per_chunk)  # Minimum 1000 lines per chunk
    
    def create_sorted_chunks(self, input_file: str) -> Tuple[int, int]:
        """
        Phase 1: Read input file in chunks, sort each chunk, and write to temp files.
        Returns (number_of_chunks, lines_per_chunk).
        """
        lines_per_chunk = self.estimate_lines_per_chunk(input_file)
        chunk_count = 0
        
        # Create temporary files
        temp_dir = tempfile.gettempdir()
        self.temp_file1 = os.path.join(temp_dir, f'sort_temp1_{os.getpid()}.txt')
        self.temp_file2 = os.path.join(temp_dir, f'sort_temp2_{os.getpid()}.txt')
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(self.temp_file1, 'w', encoding='utf-8') as outfile:
            
            while True:
                # Read chunk into memory
                chunk = []
                for _ in range(lines_per_chunk):
                    line = infile.readline()
                    if not line:
                        break
                    chunk.append(self.parse_line(line))
                
                if not chunk:
                    break
                
                # Sort chunk in memory
                chunk.sort(key=lambda x: x[0])
                
                # Write sorted chunk with chunk marker
                outfile.write(f"#CHUNK#{chunk_count}\n")
                for _, original_line in chunk:
                    outfile.write(original_line + '\n')
                
                chunk_count += 1
                chunk.clear()  # Free memory
        
        return chunk_count, lines_per_chunk
    
    def merge_chunks(self, num_chunks: int, output_file: str):
        """
        Phase 2: Merge sorted chunks using two-way merge with heap.
        Uses alternating temp files to minimize disk usage.
        """
        if num_chunks == 0:
            return
        
        if num_chunks == 1:
            # Only one chunk, just copy it back
            self._copy_chunk_to_output(self.temp_file1, 0, output_file)
            return
        
        current_input = self.temp_file1
        current_output = self.temp_file2
        
        chunks_remaining = num_chunks
        merge_level = 0
        
        while chunks_remaining > 1:
            merged_chunks = 0
            
            with open(current_output, 'w', encoding='utf-8') as outfile:
                chunk_idx = 0
                
                while chunk_idx < chunks_remaining:
                    # Merge two consecutive chunks at a time
                    chunk1_data = list(self._read_chunk(current_input, chunk_idx))
                    chunk2_data = []
                    
                    if chunk_idx + 1 < chunks_remaining:
                        chunk2_data = list(self._read_chunk(current_input, chunk_idx + 1))
                    
                    # Merge using heap
                    outfile.write(f"#CHUNK#{merged_chunks}\n")
                    self._merge_two_chunks(chunk1_data, chunk2_data, outfile)
                    
                    chunk_idx += 2
                    merged_chunks += 1
            
            # Swap input and output files
            current_input, current_output = current_output, current_input
            chunks_remaining = merged_chunks
            merge_level += 1
        
        # Final chunk is in current_input, copy to output
        self._copy_chunk_to_output(current_input, 0, output_file)
    
    def _read_chunk(self, filepath: str, chunk_index: int) -> List[Tuple[int, str]]:
        """Read a specific chunk from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            current_chunk = -1
            for line in f:
                if line.startswith('#CHUNK#'):
                    current_chunk = int(line.strip().split('#')[2])
                    if current_chunk > chunk_index:
                        break
                    continue
                
                if current_chunk == chunk_index:
                    yield self.parse_line(line)
    
    def _merge_two_chunks(self, chunk1: List[Tuple[int, str]], 
                          chunk2: List[Tuple[int, str]], outfile: TextIO):
        """Merge two sorted chunks using heap."""
        i, j = 0, 0
        len1, len2 = len(chunk1), len(chunk2)
        
        while i < len1 and j < len2:
            if chunk1[i][0] <= chunk2[j][0]:
                outfile.write(chunk1[i][1] + '\n')
                i += 1
            else:
                outfile.write(chunk2[j][1] + '\n')
                j += 1
        
        # Write remaining elements
        while i < len1:
            outfile.write(chunk1[i][1] + '\n')
            i += 1
        
        while j < len2:
            outfile.write(chunk2[j][1] + '\n')
            j += 1
    
    def _copy_chunk_to_output(self, temp_file: str, chunk_index: int, output_file: str):
        """Copy a specific chunk from temp file to output."""
        with open(temp_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            current_chunk = -1
            for line in infile:
                if line.startswith('#CHUNK#'):
                    current_chunk = int(line.strip().split('#')[2])
                    continue
                
                if current_chunk == chunk_index:
                    outfile.write(line)
    
    def sort_file(self, input_file: str):
        """
        Main sorting function. Sorts the file in-place.
        
        Args:
            input_file: Path to the input file to sort
        """
        try:
            print(f"Starting external sort of {input_file}")
            print(f"Memory limit: {self.max_memory_bytes / (1024*1024):.0f} MB")
            
            # Phase 1: Create sorted chunks
            print("Phase 1: Creating sorted chunks...")
            num_chunks, lines_per_chunk = self.create_sorted_chunks(input_file)
            print(f"Created {num_chunks} chunks ({lines_per_chunk} lines per chunk)")
            
            # Phase 2: Merge chunks
            print("Phase 2: Merging chunks...")
            self.merge_chunks(num_chunks, input_file)
            print("Sort complete!")
            
        finally:
            # Cleanup temporary files
            self._cleanup()
    
    def _cleanup(self):
        """Remove temporary files."""
        for temp_file in [self.temp_file1, self.temp_file2]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


# Example usage
if __name__ == "__main__":
    import time
    
    # Create a test file (optional - for testing)
    def create_test_file(filename: str, num_lines: int = 100000):
        """Create a test file with random data."""
        import random
        import string
        from datetime import datetime, timedelta
        
        print(f"Creating test file with {num_lines} lines...")
        with open(filename, 'w') as f:
            for _ in range(num_lines):
                key = random.randint(1, 1000000)
                text = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 20)))
                days_ago = random.randint(0, 365)
                date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                f.write(f"{key} - {text} - {date}\n")
        print(f"Test file created: {filename}")
    
    # Example: Sort a file
    test_file = "data_to_sort.txt"
    
    # Uncomment to create a test file:
    # create_test_file(test_file, 1000000)  # 1 million lines (~70MB)
    
    # Sort the file
    sorter = AdaptiveExternalSort(max_memory_mb=250)
    
    start_time = time.time()
    sorter.sort_file(test_file)
    end_time = time.time()
    
    print(f"\nSorting completed in {end_time - start_time:.2f} seconds")