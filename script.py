#!/usr/local/bin/python3
import csv, sys, re, json
from urllib.request import urlopen

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: ./script.py <osl.csv>')
    exit(1)

  filename = sys.argv[1]
  osl_file = open(filename)

  total_rows = len(osl_file.readlines())
  osl_file.seek(0)

  reader = csv.DictReader(osl_file)
  writer = csv.DictWriter(open('final_' + filename, 'w+'), reader.fieldnames)
  writer.writeheader()

  for i, row in enumerate(reader):
    dep = row["Dependency Name"]
    version = row["Version"]
    completion = (i + 1) * 100 // total_rows
    print("%02d%%: Finding %s..." % (completion, dep))

    dep_type = 'java' if re.search('.*\..*:.*', dep) else 'javascript'
    homepage = None

    if dep_type == 'java':
      parsed_dep = re.match(r'(.*):(.*)', dep)
      url = 'https://mvnrepository.com/artifact/%s/%s' % (parsed_dep.group(1), parsed_dep.group(2))
      url_version = url + '/' + version

      try:
          if urlopen(url).status == 200:
            homepage = url

          try:
            if urlopen(url_version).status == 200:
              homepage = url_version
          except Exception:
            pass
      except Exception:
        pass


    elif dep_type == 'javascript':
      url = 'https://registry.npmjs.com/' + dep
      data = json.load(urlopen(url))
      if 'repository' in data:
        git_url = data['repository']['url']
        github_url = 'https://' + re.sub(r'(.*)((github|gitlab)\.com)(.*)(.git)', r'\2\4', git_url)
        homepage = github_url

        # Check if version exists
        github_url_v1 = github_url + '/tree/' + version
        github_url_v2 = github_url + '/tree/v' + version

        try:
          if urlopen(github_url_v1).status == 200:
            homepage = github_url_v1
        except Exception:
          try:
            if urlopen(github_url_v2).status == 200:
              homepage = github_url_v2
          except Exception:
            pass

    row["Homepage"] = homepage
    writer.writerow(row)
