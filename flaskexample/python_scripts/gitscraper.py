import requests
from requests.auth import HTTPBasicAuth
import json

# base directory is from ./run.py
auth = open('utils/auth.txt').read()
username, pw = auth.split()[0], auth.split()[1]

def scrape_readme_single(dir, r):
    git_path = r.split('repos/')[1]
    url = 'https://raw.githubusercontent.com/%s/master/README'%git_path
    try:
        readme = requests.get('%s.md'%url,
                              headers={"Accept":"application/vnd.github.mercy-preview+json"},
                              auth=HTTPBasicAuth(username, pw))
        if(readme.ok):
            readme = readme.text
        else:
            readme = requests.get('%s.rst'%url,
                                  headers={"Accept":"application/vnd.github.mercy-preview+json"},
                                  auth=HTTPBasicAuth(username, pw)).text
        
        # write to file
        readme_corpus = open('%s/%s.txt'%(dir, git_path.split('/')[1]), 'w')
        readme_corpus.write(str(readme.encode('utf8')))
        readme_corpus.close()
    except:
        print('No README file for %s. Skipping'%repo)

# Class for each Github Profile
class Github_Profile:
    def __init__(self, pckgs):
        self.user = ''
        self.url = ''
        
        # metrics
        self.classes = 0
        self.defs = 0
        self.packages = {}
        for p in pckgs:
            self.packages[p] = 0

# get frequency of desired packages in python code
def get_package_freq(text, GProfile):
    for p in GProfile.packages.keys():
        if text.find(p) != -1:    # is package even in script at all?
            
            # direct import, e.g. 'import numpy (as np)'
            string = 'import %s'%p
            loc = text.find(string)
            if loc != -1:
                # last word in line is call_name
                call_name = text[loc:].partition('\n')[0].split()[-1].split('\n')[0].split('\\')[0]
                GProfile.packages[p] += text.count('%s.'%call_name)
        
            # indirect import, e.g. 'from numpy.X import vectorize (as vec)'
            string_from = 'from %s'%p
            loc_from = text.find(string_from)
            ext = ['(', '.']  # check both X() and X.y()
            while loc_from != -1: # iterate same package imported mult. times on different lines
                try:
                    call_names = text[loc_from:].partition('\n')[0].split(' import ')[1]
                    if call_names.count(',') != 0:  # iterate mulitple imports on same line
                        call_names = call_names.replace('(','').replace(')','').replace(" ", "").split(',')
                        for call_name in call_names:
                            if call_name == "": # skip bad entries
                                continue
                            GProfile.packages[p] += sum(text.count('%s%s'%(call_name, x)) for x in ext)
                    else:
                        call_name = call_names.split()[-1]
                        GProfile.packages[p] += sum(text.count('%s%s'%(call_name, x)) for x in ext)
                except:
                    pass
                loc_from = text.find(string_from, loc_from + 1) # get next instance, e.g. 'from numpy.X import b'

def update_metrics(item, GProfile):
    text = requests.get(item['download_url'],
                        headers={"Accept":"application/vnd.github.mercy-preview+json"},
                        auth=HTTPBasicAuth(username, pw)).text
                        
    # metrics
    get_package_freq(text, GProfile)
    # get_def_class_freq(text, GProfile)  #still need to create this

# recursive, main functions
def digest_repo(repo_url, GProfile):
    r = requests.get('%s'%repo_url, headers={"Accept":"application/vnd.github.mercy-preview+json"},
                     auth=HTTPBasicAuth(username, pw))
    repoItems = json.loads(r.text or r.content)
                     
    for item in repoItems:
        if (item['type'] == 'file' and (item['name'][-3:] == '.py' or item['name'][-6:] == '.ipynb')
            and 'ipynb_checkpoints' not in item['download_url']):
            print(item['download_url'])
            update_metrics(item, GProfile)
        elif item['type'] == 'dir':
            digest_repo(item['url'], GProfile)

def main(git_user, packages, readme_dir='candidate'):
    GProfile = Github_Profile(packages)
    GProfile.url = 'https://api.github.com/users/%s/repos'%git_user
    r = requests.get(GProfile.url, headers={"Accept":"application/vnd.github.mercy-preview+json"},
                     auth=HTTPBasicAuth(username, pw))
    userItems = json.loads(r.text or r.content)
                     
    for item in userItems:
        if item['fork'] == False:  # for now ignore forks
            if 'DeepMoon' in item['url']:   #### TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                repo_url = '%s/contents'%item['url']
                scrape_readme_single(readme_dir, item['url'])
                digest_repo(repo_url, GProfile)
    return GProfile

if __name__ == '__main__':
    main('silburt', ['numpy'], 'candidate')
