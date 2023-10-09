import os

class ViewCLI():
    def __init__(self):
        pass

    def get_folder_to_course_path(self):
        root_dir = "./inputs/"
        folders = [f.path for f in os.scandir(root_dir) if f.is_dir()]

        print()
        print("Select a folder to translate:")
        for i, folder in enumerate(folders):
            print(f"{i+1}. {folder}")

        choice = int(input("Enter the number of the folder: "))
        folder_path = folders[choice-1]

        return folder_path

    def get_initial_quizz_index(self):
        while True:
            try:
                # Prompt the user for input
                index = int(input("Enter the initial quiz index (between 0 and 9000): "))

                # Check if the input is between 0 and 9000
                if 0 <= index <= 9000:
                    return index
                else:
                    print("Error: Please enter a number between 0 and 9000.")
            except ValueError:
                # Handle invalid input such as strings or other non-integer values
                print("Error: Please enter a valid number.")

    def update_progress_bar(self, current, total):
        progress = current / total * 100
        print(f'Quizz Creation in Progress: [{current}/{total}] {progress:.2f}%')

    def work_in_progress(self, task):
        print()
        print(f"{task}...")

    def work_done(self, task):
        print()
        print(f"{task} done!")

    def estimated_remaining_time(self, seconds_remaining):
        m, s = divmod(seconds_remaining, 60)
        h, m = divmod(m, 60)
        print(f'Estimated time remaining: {int(h)} hours, {int(m)} minutes, and {int(s)} seconds')

    def user_request_stop(self):
        response = input("Do you want me to create other Quizzes? (y/n): ")
        return response.lower() == "n"
