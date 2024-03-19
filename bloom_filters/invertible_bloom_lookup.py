import hashlib
from pybloom_live import BloomFilter


def string_to_int(s):
    return hash(s)

class InvertibleBloomFilter:
    def __init__(self, size, error_rate=0.1):
        self.size = size
        self.cells = [None] * size
        self.bloom = BloomFilter(capacity=size, error_rate=error_rate)

    def _hash(self, key, i):
        h = hashlib.sha256()
        h.update(str(key).encode('utf-8'))
        h.update(str(i).encode('utf-8'))
        return int(h.hexdigest(), 16) % self.size

    def insert(self, key, value):
        for i in range(3):
            index = self._hash(key, i)
            self.bloom.add(index)
            if self.cells[index] is None:
                self.cells[index] = (key, value, 1)
            else:
                k, v, count = self.cells[index]
                self.cells[index] = (k ^ key, v ^ value, count + 1)

    def delete(self, key, value):
        for i in range(3):
            index = self._hash(key, i)
            if index in self.bloom:
                k, v, count = self.cells[index]
                self.cells[index] = (k ^ key, v ^ value, count - 1)

    def get(self, key):
        for i in range(3):
            index = self._hash(key, i)
            if index in self.bloom:
                k, v, count = self.cells[index]
                if k == key and count == 1:
                    return v
        return None

    def contains(self, key):
        for i in range(3):
            index = self._hash(key, i)
            if index not in self.bloom:
                return False
            k, _, count = self.cells[index]
            if k == key and count == 1:
                return True
        return False


if __name__ == '__main__':
    # Example usage:
    ibf = InvertibleBloomFilter(size=100, error_rate=0.1)
    key = string_to_int("example_key")
    value = string_to_int("example_value")

    ibf.insert(string_to_int('key1'), string_to_int('value1'))
    ibf.insert(string_to_int('key2'), string_to_int('value2'))

    print(ibf.contains(string_to_int('key1')))  # Output: True
    print(ibf.contains(string_to_int('key2')))  # Output: True
    print(ibf.contains(string_to_int('key3')))  # Output: False

    print(ibf.get(string_to_int('key1')))  # Output: value1
    print(ibf.get(string_to_int('key2')))  # Output: value2

    ibf.delete(string_to_int('key1'), string_to_int('value1'))
    print(ibf.get(string_to_int('key1')))  # Output: None
