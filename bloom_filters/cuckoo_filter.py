import cuckoofilter

cf = cuckoofilter.CuckooFilter(capacity=100)

cf.insert("apple")
cf.insert("banana")
cf.insert("orange")

print(cf.contains("apple"))
print(cf.contains("grape"))

#cf.insert("apple")

cf.delete("apple")

print(cf.contains("apple"))