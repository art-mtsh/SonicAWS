import os
import shutil


def organize_folders(input_folder):
    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)
        print(f"Existed folder: {folder_path}")

        if os.path.isdir(folder_path):
            symbol = folder_name.split('-')[0]
            symbol_folder_path = os.path.join(input_folder, symbol)
            print(f"Created folder: {symbol_folder_path}")
            print('')

            # Create new folder for the symbol if it doesn't exist
            if not os.path.exists(symbol_folder_path):
                os.makedirs(symbol_folder_path)

            # Move all ssv files to the symbol folder
            for file_name in os.listdir(folder_path):
                print(f"File name: {file_name}")

                if file_name.endswith('.csv'):
                    ssv_file_path = os.path.join(folder_path, file_name)
                    shutil.move(ssv_file_path, os.path.join(symbol_folder_path, file_name))

            # Remove the old folder
            shutil.rmtree(folder_path)


# Replace 'path/to/your/folders' with the actual path to your folders
organize_folders(r'D:\bidata')
