import heapq

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    heap = [Node(ch, fr) for ch, fr in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        new = Node(None, left.freq + right.freq)
        new.left = left
        new.right = right
        heapq.heappush(heap, new)

    return heap[0], freq

def generate_codes(root, code="", code_map=None):
    if code_map is None:
        code_map = {}

    if root:
        if root.char is not None:
            code_map[root.char] = code
        generate_codes(root.left, code + "0", code_map)
        generate_codes(root.right, code + "1", code_map)

    return code_map

def serialize_tree(node):
    """Serialize tree to JSON-compatible format"""
    if node is None:
        return None
    
    result = {
        "char": node.char if node.char is not None else None,
        "freq": node.freq,
        "left": serialize_tree(node.left),
        "right": serialize_tree(node.right)
    }
    return result