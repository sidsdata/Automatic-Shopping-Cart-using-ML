import os

def cart():
	
	# print(source)
	base = os.getcwd()
	file_path = os.path.join(base , 'detectvid_new1.py')
	os.system( "python {}".format(file_path))
	
	


print(os.getcwd())