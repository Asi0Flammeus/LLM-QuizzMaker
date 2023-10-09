from controller import Controller
from view import ViewCLI

def main():
    view = ViewCLI()
    while True:
        controller = Controller()
        controller.create_course_based_quizzes()

        if view.user_request_stop():
            break

if __name__ == "__main__":
    main()
