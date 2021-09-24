

# Python program to
# demonstrate reading files
# using for loop

L = ["Geeks\n", "for\n", "Geeks\n"]

# Writing to file
file1 = open('myfile.txt', 'w')
file1.writelines(L)
file1.close()

# Opening file
file1 = open('myfile.txt', 'r')
count = 0

# Using for loop
print("Using for loop")
for keyfile in file1:
	count += 1
    keyfile_list = keyfile.split('/')
    
	print("Line{}: {}".format(count, line.strip()))

# Closing files
file1.close()
