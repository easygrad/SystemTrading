from ui.ui import * # ui 폴더의 ui 파일에서 Ui_class 포함한 모든 class를 다 가져오겠다 *


class Main():
    def __init__(self):
        print("실행할 메인 클래스")

        Ui() # NameError: name 'Ui_class' is not defined

# 이게 실행 파일이다 지정해주는 경우 이렇게 써준다고함..
if __name__=="__main__":
    Main()