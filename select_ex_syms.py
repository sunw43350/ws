import pickle




data = pickle.load(open('your_file.pk', 'rb')); 



print(data)
with open('your_file.pk', 'rb') as f:
    data = pickle.load(f)

print(data)