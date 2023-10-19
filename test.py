# Initialize an empty list
my_list = []

while True:
    value = input("Enter a value (or 's' to stop and create the list): ")
    if value.lower() == 's':
        break
    my_list.append(value)

# Print the resulting list
print("Your list:", my_list)
