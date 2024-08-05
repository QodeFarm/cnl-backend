import os
import shutil

def delete_pycache(root_directory):
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for dirname in dirnames:
            if dirname == '__pycache__':
                pycache_path = os.path.join(dirpath, dirname)
                print(f"Deleting: {pycache_path}")
                shutil.rmtree(pycache_path)

if __name__ == "__main__":
    project_directory = "D:/ERP_16_apr/CNL/cnl-backend/"
    delete_pycache(project_directory)
    print("All __pycache__ directories have been deleted.")
