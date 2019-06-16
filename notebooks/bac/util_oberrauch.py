def get_array_dif(a):
	return a[1:] - a[:-1];

def get_array_mid(a):
	return a[:-1] + get_array_dif(a)/2;