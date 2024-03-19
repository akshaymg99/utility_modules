# install libpostal from here: https://github.com/openvenues/libpostal

from postal.parser import parse_address
from postal.expand import expand_address
import unicodedata


def convert_to_dict(address_list):  
    address_dict = {}
    for value, key in address_list:
        if key not in address_dict:
            address_dict[key] = value
        elif key in address_dict and len(value) > len(str(address_dict[key])):
            address_dict[key] = value
        
    return address_dict


def are_addr_similar(addr1, addr2):
    try:
        addr1 = expand_address(addr1)
        addr2 = expand_address(addr2)

        addr1_parsed = None
        if isinstance(addr1, list) and len(addr1) > 0:
            addr1 = addr1[0]
        if isinstance(addr1, str):
            addr1_parsed = parse_address(addr1)
        
        addr2_parsed = None
        if isinstance(addr2, list) and len(addr2) > 0:
            addr2 = addr2[0]
        if isinstance(addr1, str):
            addr2_parsed = parse_address(addr2)
            
        addr1_dict = convert_to_dict(addr1_parsed)
        addr2_dict = convert_to_dict(addr2_parsed)
        
        for key, value in addr1_dict.items():
            if key in ["road", "near", "level", "suburb"]:
                if get_similarity(value, addr2_dict.get(key, "")) < 75:
                    return False
            elif key in ["house_number", "unit", "entrance"]:
                if str(value) != str(addr2_dict.get(key, "")):
                    return False
                    
        return True
    except Exception as e:
        print("address parser failed: {}".format(e))
        return False


if __name__ == "__main__":
	are_addr_similar("Carrer d'Astúries, 47, 08012 Barcelona, España", "Carrer D'Astúries 47, Barcelona, EMEA 08012")
	print(parse_address("102 Barbu Văcărescu Boulevard, Bucharest 020283, Romania"))

