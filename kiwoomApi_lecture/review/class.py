# 유튜브 프로그램 동산
# class 기초

class B_school(): # class name은 일반적으로 대문자로 시작
    def __init__(self): # init은 B_class를 실행했을 때 무조건 실행됨
        print("B 클래스 입니다.")

        print(dir(self)) # 함수들 불러옴

    def stock(self): # 클래스 안에는 self가 자동으로 생성됨, stock3에서 설명
        print("증권분석과 입니다.")
        # init은 무조건 실행이 되는 반면에 stock은 실행이 안 됨! 접근을 따로 시켜줘야 함

        return "증권"

    def stock2(self, student_name):
        print("증권분석과 입니다.")
        print(student_name)

        return "증권"

    def stock3(self): # self는 장바구니 같은 것, stock3가 만들어짐과 동시에 self에 포함됨
        print("증권분석과 입니다.")

bb = B_school() # 변수명 지정 : instance화? 객체화
print(bb)

bb_stock = bb.stock() # stock으로 접근 시켜줌
print(bb_stock)

bb_stock2 = bb.stock2("원빈")
print(bb_stock2)

B_school()

class C_school():
    def __init__(self):
        print("C 클래스 입니다.")

        self.student_name = "원빈" # stock 처럼 함수를 만들 수도 있지만 이런식으로 장바구니에 넣어줄 수도 있음
        # self. 안 써주면 student_name 못 불러옴, ~~ has no attribute~~ 이런 식으로 오류 뜸
        
        self.stock() # stock 함수 실행, stock2 함수는 저장되어 있긴 하지만 실행은 안 됨
        self.english()

    def stock(self):
        print("증권분석과 입니다.")
        print("%s 전학생 입니다." % self.student_name) # 저장해놓은 student_name을 꺼내옴

    def stock2(self):
        print("증권분석과 입니다.")
        print("%s 전학생 입니다." % self.student_name)

    def english(self):
        print("%s 영어과 입니다." % self.student_name)

cc = C_school()
print(cc.student_name) # self. : 장바구니에 담았기 때문에 가져올 수 있는 것

class A_school():
    def __init__(self):
        print("A 클래스 입니다.")

        cc = C_school()
        self.student_name_a = cc.student_name

        print(self.student_name_a)

A_school()

# 상속
class Parent():
    def __init__(self):
        print("부모 클래스!")

        self.money = 5000000000
    
    def book(self):
        print("부모의 서재입니다.")

class Child_1(Parent): # 상속
    def __init__(self):
        super().__init__() # 부모의 초기값이 가져와짐, super().는 법적인 절차를 마쳤다 라고 생각할 수 있음
        print("첫 번째 자식입니다.")
        print(self.money) # 부모의 초기값을 가져왔기 떄문에 가져올 수 있음. Child_2는 안 됨
        self.book()

class Child_2(Parent): # 상속 하려고 했지만 법적인 절차를 마치지 않음
    def __init__(self):
        print("두 번째 자식입니다.")
        self.book() # 부모의 init(초기값)에 있는 money는 받을 수 없지만, 서재는 가져올 수 있음

Child_1()
Child_2()

print(__name__)