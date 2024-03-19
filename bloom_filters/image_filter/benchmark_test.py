import time
import random
import string
import matplotlib.pyplot as plt
from image_emb_filter import ImageFilter_Rhash
import psutil
from tqdm import tqdm
import os

# Initialize your class
image_filter = ImageFilter_Rhash()

# Prepare some test data
num_operations = 100000
thumbnails = [''.join(random.choices(string.ascii_lowercase, k=150)) for _ in range(num_operations)]
modelnames = [''.join(random.choices(string.ascii_lowercase, k=150)) for _ in range(num_operations)]
start_date = 0  # replace with your start date
end_date = 0  # replace with your end date

# Measure the time and memory it takes to insert
print("Inserting data...")
start_time = time.time()
start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
for thumbnail, modelname in tqdm(zip(thumbnails, modelnames)):
    image_filter.insert(thumbnail, modelname)
insert_time = time.time() - start_time
insert_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2 - start_memory
print("Insertion time for {} operations: {} seconds".format(num_operations, insert_time))
print("Insertion memory for {} operations: {} MB".format(num_operations, insert_memory))

# Measure the time it takes to check if a key exists
print("Checking if keys exist...")
start_time = time.time()
for thumbnail, modelname in tqdm(zip(thumbnails, modelnames)):
    image_filter.exists(thumbnail, modelname)
exists_time = time.time() - start_time
print("Key exist-checking time for {} operations: {} seconds".format(num_operations, exists_time))

# Measure the time it takes to get thumbnails by date range
print("Getting thumbnails by date range...")
start_time = time.time()
for modelname in tqdm(modelnames):
    image_filter.get_thumbnail_by_date_range(start_date, end_date, modelname)
get_thumbnail_time = time.time() - start_time
print("Thumbnail retrieval time for {} operations: {} seconds".format(num_operations, get_thumbnail_time))

# Measure the time it takes to get modelnames by date range
print("Getting modelnames by date range...")
start_time = time.time()
for thumbnail in tqdm(thumbnails):
    image_filter.get_modelname_by_date_range(start_date, end_date, thumbnail)
get_modelname_time = time.time() - start_time
print("Modelname retrieval time for {} operations: {} seconds".format(num_operations, get_modelname_time))

# Plot the results
# Plot the results
fig, ax1 = plt.subplots()

color = 'tab:blue'
ax1.set_xlabel('Operation')
ax1.set_ylabel('Time (seconds)', color=color)
ax1.bar(['Insert', 'Exists', 'Get Thumbnail', 'Get Modelname'], [insert_time, exists_time, get_thumbnail_time, get_modelname_time], color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Memory (MB)', color=color)
ax2.bar(['Insert'], [insert_memory], color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()

# Save the plot to a file
plt.savefig('benchmark_results.png')


