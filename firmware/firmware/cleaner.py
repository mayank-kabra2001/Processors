import sys

lookup = '0:'
test_input = sys.argv[1]

with open(test_input + ".txt") as file:
	f = open(test_input + "_cleaned1.txt" , "w")
	for line in file:
		if not line.isspace():
			f.write(line)
	f.close()

with open(test_input + "_cleaned1.txt") as myFile:
	#print("y")
	for val, line in enumerate(myFile, 1):
		if lookup in line:
			break
	#print(val)
	#lines = myFile.readlines()
	ptr = 1
	f2 = open(test_input + "_cleaned2.txt", "w")
	f = open(test_input + "_cleaned1.txt")
	lines = f.readlines()
	for line in lines:
		#print(ptr)
		#print(line)
		if (ptr >= val):
			f2.write(line)
		ptr += 1
	f.close() 
	f2.close()

f3 = open(test_input + "_cleaned2.txt")
lines = f3.readlines()
data = []  
for line in lines:
	#print(line)
	data.append(line.split())
#print(data)

f4 = open(test_input + "_binary.txt" , "w") 
for i in range(len(data) - 1): 
	f4.write(data[i][1])
	f4.write("\n")

f3.close() 
f4.close()


