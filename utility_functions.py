
# json to csv iterative converter
import csv, json, sys

json_file = '/data/akshay/UMM_test/debug/final_res_Croma_Assortment_Amazon.json'
csv_file = '/data/akshay/UMM_test/debug/final_res_Croma_Assortment_Amazon.csv'

count = 0    

with open(json_file) as f_ptr, open(csv_file, "w") as csv_ptr:
    csvwriter = csv.writer(csv_ptr)
    for line in tqdm(f_ptr):
        json_record = json.loads(line)
        
        if count == 0:
            header = json_record.keys()
            csvwriter.writerow(header)
            count += 1
        
        csvwriter.writerow(json_record.values())
        
        
# gz file uncompressed, change to generic form from UT
def uncompress_file(gz_name, job_id):
    """
    uncompresses gz files and saves in data_download directory
    Doesn't return, just saves uncompressed file in same data dir
    """
    if gz_name.endswith('.gz'):
        try:
            gz_name = os.path.join(AggregatorEnum.get_data_directory_path(job_id), gz_name)
            save_filename = gz_name.replace('.gz', '')
            with gzip.open(gz_name, "rb") as f_in, open(save_filename, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(gz_name)  # delete gz file
            logger.info("Uncompressed {} file successfully".format(gz_name))
        except Exception as e:
            logger.exception("Error while uncompressing {} file".format(gz_name))
            raise e
    else:
        return
        
       
# csv to json conversion, change to generic form from UT
def convert_to_json(filename, job_id):
    """
    converts csv to json file
    Doesn't return, saves the converted file in data_download directory
    """
    if filename.endswith('csv'):
        try:
            filename = os.path.join(AggregatorEnum.get_data_directory_path(job_id), filename)
            filename_json = str(filename.replace('csv', 'json'))

            with open(filename, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                with open(filename_json, 'w') as json_file:
                    for row in reader:
                        json_file.write(json.dumps(row) + '\n')
            logger.info("Converted {} file from csv to json".format(filename))
        except Exception as e:
            logger.exception("Error while converting csv to json file: {}".format(filename))
            raise e
    else:
        return     
        
   
        
# sending post request to an api
import requests
import json

url = ""  

req_data = {
  "seed_path": "seed_swigg_sample.csv",
  "comp_path": "comp_swigg_sample.csv"
}

response = requests.post(url, data= json.dumps(req_data))







