try:
	with open('../../.password/google-maps/api', 'r') as fp:
		key = fp.readlines()

	key = ''.join(key)

except:
	# Insert your API key here
	key = 'AIzaSyB_i1p-mQkyyhMfhf-OVTFdgppBNq9fCa4'