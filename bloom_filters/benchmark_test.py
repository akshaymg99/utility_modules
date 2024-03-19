import time
import random
import csv
import pandas as pd
import string
import matplotlib.pyplot as plt
import tracemalloc
from pybloom_live import BloomFilter, ScalableBloomFilter
import cuckoofilter
from invertible_bloom_lookup import InvertibleBloomFilter

def random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def truncate(no, place_digits):
    """
    Truncates a float no place_digits decimal places without rounding
    """
    float_str = '%.{}f'.format(place_digits)
    return float(float_str % no)

def string_to_int(s):
    return hash(s)

def benchmark_filter(type, filter_obj, items, test_items):
    start = time.time()
    for item in items:
        if type == "standard":
            filter_obj.add(item)
        elif type == "cuckoo":
            filter_obj.insert(item)
    insert_time = time.time() - start

    start = time.time()
    false_positives = 0
    for item in test_items:
        if type == "standard" and item in filter_obj and item not in items:
            false_positives += 1
        elif type == "cuckoo" and filter_obj.contains(item) and item not in items:
            false_positives += 1
    query_time = time.time() - start

    false_positive_rate = false_positives / len(test_items)
    return insert_time, query_time, false_positive_rate

def benchmark_ibf(filter_obj, keys, values, test_keys, test_values):
    # Measure insert time
    start_time = time.time()
    for key, value in zip(keys, values):
        filter_obj.insert(key, value)
    insert_time = time.time() - start_time

    # Measure query time
    false_positives = 0
    start_time = time.time()
    for test_key in test_keys:
        if filter_obj.contains(test_key) and test_key not in keys:
            false_positives += 1
    query_time = time.time() - start_time

    false_positive_rate = false_positives / len(test_keys)
    return insert_time, query_time, false_positive_rate


# Vary the size of the data
sizes = list(range(1000, 1000001, 100000))
bf_insert_times = []
bf_query_times = []
bf_fp_rates = []
bf_memory_usages = []

cf_insert_times = []
cf_query_times = []
cf_fp_rates = []
cf_memory_usages = []

ibf_insert_times = []
ibf_query_times = []
ibf_fp_rates = []
ibf_memory_usages = []

sbf_insert_times = []
sbf_query_times = []
sbf_fp_rates = []
sbf_memory_usages = []

item_length = 10

for num_item in sizes:
    items = [random_string(item_length) for _ in range(num_item)]
    test_items = [random_string(item_length) for _ in range(num_item)]

    # Standard Bloom Filter
    bf = BloomFilter(capacity=num_item)
    tracemalloc.start()
    bf_insert_time, bf_query_time, bf_fp_rate = benchmark_filter("standard", bf, items, test_items)
    bf_mem_current, bf_mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    bf_insert_times.append(truncate(bf_insert_time, 3))
    bf_query_times.append(truncate(bf_query_time, 3))
    bf_fp_rates.append(truncate(bf_fp_rate*100, 3))
    bf_memory_usages.append(bf_mem_peak)

    # Counting Cuckoo Filter
    cf = cuckoofilter.CuckooFilter(capacity=num_item, fingerprint_size=2)
    tracemalloc.start()
    cf_insert_time, cf_query_time, cf_fp_rate = benchmark_filter("cuckoo", cf, items, test_items)
    cf_mem_current, cf_mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cf_insert_times.append(truncate(cf_insert_time, 3))
    cf_query_times.append(truncate(cf_query_time, 3))
    cf_fp_rates.append(truncate(cf_fp_rate, 3))
    cf_memory_usages.append(cf_mem_peak)

    # Invertible Bloom Filter
    # Generate random keys and values
    keys = [string_to_int(random_string(item_length)) for _ in range(num_item)]
    values = [string_to_int(random_string(item_length)) for _ in range(num_item)]
    test_keys = [string_to_int(random_string(item_length)) for _ in range(num_item)]
    test_values = [string_to_int(random_string(item_length)) for _ in range(num_item)]
    ibf = InvertibleBloomFilter(size=100, error_rate=0.01)
    tracemalloc.start()
    ibf_insert_time, ibf_query_time, ibf_fp_rate = benchmark_ibf(ibf, keys, values, test_keys, test_values)
    ibf_mem_current, ibf_mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ibf_insert_times.append(truncate(ibf_insert_time, 3))
    ibf_query_times.append(truncate(ibf_query_time, 3))
    ibf_fp_rates.append(truncate(ibf_fp_rate, 3))
    ibf_memory_usages.append(ibf_mem_peak)

    # Scalable bloom filter
    sbf = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH, error_rate=0.01)
    tracemalloc.start()
    sbf_insert_time, sbf_query_time, sbf_fp_rate = benchmark_filter("standard", sbf, items, test_items)
    sbf_mem_current, sbf_mem_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    sbf_insert_times.append(truncate(sbf_insert_time, 3))
    sbf_query_times.append(truncate(sbf_query_time, 3))
    sbf_fp_rates.append(truncate(sbf_fp_rate*100, 3))
    sbf_memory_usages.append(sbf_mem_peak)

    print("Bloom Filter: Insert Time = {:.2f}s, Query Time = {:.2f}s, mem current: {}, mem peak: {}, False Positive Rate = {:.2%}".format(bf_insert_time, bf_query_time, bf_mem_current, bf_mem_peak, bf_fp_rate))
    print("Cuckoo Filter: Insert Time = {:.2f}s, Query Time = {:.2f}s, mem current: {}, mem peak: {}, False Positive Rate = {:.2%}".format(cf_insert_time, cf_query_time, cf_mem_current, cf_mem_peak, cf_fp_rate))
    print("IBF: Insert Time = {:.2f}s, Query Time = {:.2f}s, mem current: {}, mem peak: {}, False Positive Rate = {:.2%}".format(ibf_insert_time, ibf_query_time, ibf_mem_current, ibf_mem_peak, ibf_fp_rate))
    print("Scalable Bloom Filter: Insert Time = {:.2f}s, Query Time = {:.2f}s, mem current: {}, mem peak: {}, False Positive Rate = {:.2%}".format(sbf_insert_time, sbf_query_time, sbf_mem_current, sbf_mem_peak, sbf_fp_rate))
    print("num_item completed: {}".format(num_item))


stat_data = {
    "Bloom Filter Insert times": bf_insert_times,
    "Cuckoo Filter Insert times": cf_insert_times,
    "Inverted BF Insert times": ibf_insert_times,
    "Scaling BF Insert times": sbf_insert_times,
    "Bloom Filter Query times": bf_query_times,
    "Cuckoo Filter Query times": cf_query_times,
    "Inverted BF Query times": ibf_query_times,
    "Scaling BF Query times": sbf_query_times,
    "Bloom Filter Memory usages": bf_memory_usages,
    "Cuckoo Filter Memory usages": cf_memory_usages,
    "Inverted BF Memory usages": ibf_memory_usages,
    "Scaling BF Memory usages": sbf_memory_usages,
    "Bloom Filter False Positive Rates": bf_fp_rates,
    "Cuckoo Filter False Positive Rates": cf_fp_rates,
    "Inverted BF False Positive Rates": ibf_fp_rates,
    "Scaling BF False Positive Rates": sbf_fp_rates,
}

df = pd.DataFrame(stat_data)
df.to_csv("./stats_dir/stats.csv", index=False)

# Plot Insert Times
plt.figure()
plt.plot(sizes, bf_insert_times, label="Bloom Filter")
plt.plot(sizes, cf_insert_times, label="Cuckoo Filter")
plt.plot(sizes, ibf_insert_times, label="Invertible Bloom Filter")
plt.plot(sizes, sbf_insert_times, label="Scalable Bloom Filter")
plt.xlabel("Size of Data")
plt.ylabel("Insert Time (s)")
plt.title("Insert Time vs volume of data")
plt.legend()
plt.savefig('./stats_dir/insert_time.png')

# Plot False Positive Rates
plt.figure()
plt.plot(sizes, bf_fp_rates, label="Bloom Filter")
plt.plot(sizes, cf_fp_rates, label="Cuckoo Filter")
plt.plot(sizes, ibf_fp_rates, label="Invertible Bloom Filter")
plt.plot(sizes, sbf_fp_rates, label="Scalable Bloom Filter")
plt.xlabel("Size of Data")
plt.ylabel("False Positive Rate")
plt.title("False Positive Rate vs volume of data")
plt.legend()
plt.savefig('./stats_dir/false_positive_rate.png')

# Plot Query Times
plt.figure()
plt.plot(sizes, bf_query_times, label="Bloom Filter")
plt.plot(sizes, cf_query_times, label="Cuckoo Filter")
plt.plot(sizes, ibf_query_times, label="Invertible Bloom Filter")
plt.plot(sizes, sbf_query_times, label="Scalable Bloom Filter")
plt.xlabel("Size of Data")
plt.ylabel("Query Time (s)")
plt.title("Query Time vs volume of data")
plt.legend()
plt.savefig('./stats_dir/query_time.png')

# Plot Memory Usage
plt.figure()
plt.plot(sizes, bf_memory_usages, label="Bloom Filter")
plt.plot(sizes, cf_memory_usages, label="Cuckoo Filter")
plt.plot(sizes, ibf_memory_usages, label="Invertible Bloom Filter")
plt.plot(sizes, sbf_memory_usages, label="Scalable Bloom Filter")
plt.xlabel("Size of Data")
plt.ylabel("Memory Usage (bytes)")
plt.title("Memory Usage vs volume of data")
plt.legend()
plt.savefig('./stats_dir/memory_usage.png')
