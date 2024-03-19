from pybloom_live import ScalableCountingBloomFilter

# Create a Scalable Counting Bloom Filter with an initial capacity of 100 and a target false positive rate of 0.1
cbf = ScalableCountingBloomFilter(initial_capacity=100, error_rate=0.1)

# Add some elements to the filter
cbf.add("apple")
cbf.add("banana")
cbf.add("orange")

# Check if an element is in the filter
print("apple" in cbf)  # True
print("grape" in cbf)  # False

# Add more occurrences of an element
cbf.add("apple")

# Remove an element
cbf.remove("apple")

# Check if the removed element is in the filter
print("apple" in cbf)  # False
