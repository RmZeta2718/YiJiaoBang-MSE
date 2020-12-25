"""
Remove redundant dependencies.
"""
import os
import shutil


path = './SafeDelete'
dep = set(os.listdir(path))
# print(dep)
dist = './dist/易教帮'
for file in [file for file in os.listdir(dist) if file in dep]:
    filepath = '%s/%s' % (dist, file)
    print("Removing", filepath)
    if os.path.isfile(filepath):
        os.remove(filepath)
    else:
        assert os.path.isdir(filepath)
        shutil.rmtree(filepath)
