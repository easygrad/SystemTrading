from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("Kiwoom 클래스 입니다.")

        ### eventloop 모음
        self.login_event_loop = None
        ###

        ### 변수 모음
        self.account_num = None
        ###

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) # [OnEventConnect()이벤트] 로그인 처리 이벤트입니다. 성공이면 인자값 nErrCode가 0이며 에러는 다음과 같은 값이 전달됩니다.

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_() # 이벤트 루프 안에서 활성화되고 로그인 완료될 때까지 다음 코드 실행 안 됨
    # 오류: opstarter 핸들값이 없습니다. 키움에 로그인 요청했는데 프로그램 상에서는 로그인을 요청했으니 할 일 끝났고 다음 코드로 넘어가려고 함. 로그인 성공이 된 게 슬롯 자체가 반환이 안됐음. 다음 게 실행되려고 하니깐 핸들 오류가 남
    # 해결: 이 때 필요한게 pyqt에서 제공해주는 이벤트루프 클래스 from PyQt5.QtCore import *

    def login_slot(self, errCode):
        print(errors(errCode))
        
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)", "ACCNO") # [LONG GetLoginInfo()] 로그인 후 사용할 수 있으며 인자값에 대응하는 정보를 얻을 수 있습니다. "ACCLIST" 또는 "ACCNO" : 구분자 ';'로 연결된 보유계좌 목록을 반환합니다. 예시 CString   strAcctList = GetLoginInfo("ACCLIST"); 여기서 strAcctList는 ';'로 분리한 보유계좌 목록임
        
        self.account_num = account_list.split(';')[0]
        print("나의 보유 계좌번호 %s "% self.account_num)
        # 모의투자 계좌번호는 뒤에 11이 붙음