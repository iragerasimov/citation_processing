import os
import json
import re
import glob

ttl_files = glob.glob('src/*.ttl');
terms = {}

for ttl_file in ttl_files:
  if not re.search('realm', ttl_file) and not re.search('phen', ttl_file):
    continue
  print(ttl_file)
  category = None
  with open(ttl_file) as origin_file:
    for line in origin_file:
      #line = re.findall(r'rdfs:label', line)
      if "rdfs:label" in line:
        idx1 = line.find('"')
        idx2 = line.find('"', idx1+1)
        field = line[idx1+1:idx2]
      else:
        continue
      if re.findall(r'SWEET', field):
        category = re.sub('SWEET Ontology ', '', field)
      elif terms.get(field, ''):
        terms[field].append(category)
      else:
        terms[field] = [category]
  #print(terms)
 
     #SWEET Ontology
  #$categories[$category] = @keywords;
  #my $json = encode_json @categories;
  #print "$json"; #$category: @keywords\n";
  #quit()


json_folder_path = '.'
with open(os.path.join(json_folder_path, "terms1.json"), "w") as fp:
  json.dump(terms, fp, indent=4)


