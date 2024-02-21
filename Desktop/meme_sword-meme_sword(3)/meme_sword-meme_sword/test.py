import os

def print_directory_tree(startpath, indent=0):
    for item in os.listdir(startpath):
        path = os.path.join(startpath, item)
        if os.path.isdir(path):
            print(' ' * indent + '└── ' + item)
            print_directory_tree(path, indent + 4)
        else:
            print(' ' * indent + '└── ' + item)

# Replace '/your/directory/path' with the path of the directory you want to print
print_directory_tree('./app')
