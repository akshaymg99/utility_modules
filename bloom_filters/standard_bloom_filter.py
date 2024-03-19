
import pybloomfilter

# 1 % false positive rate
bf = pybloomfilter.BloomFilter(1000, 0.01)

bf.add("apple")
bf.add("banana")
bf.add("orange")

print("apple" in bf)
print("grape" in bf)
print("banana" in bf)
