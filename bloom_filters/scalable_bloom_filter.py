import pybloom_live

bf = pybloom_live.BloomFilter(capacity=1000, error_rate=0.001)
[bf.add(x) for x in range(10)]

print(all([(x in bf) for x in range(10)]))

print(10 in bf)
print(5 in bf)
print(bf.error_rate)

sbf = pybloom_live.ScalableBloomFilter(mode=pybloom_live.ScalableBloomFilter.LARGE_SET_GROWTH)  # SMALL_SET_GROWTH takes less memory, but slower
count = 10000
for i in range(0, count):
    sbf.add(i)

print(sbf.error_rate)
