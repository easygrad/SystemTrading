import os
import sys
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from config.errorCode import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        # 이벤트루프 모음
        self.login_event_loop = None

        # 스크린번호 모음
        self.screen_my_info = "2000"

        # 파이썬 제어
        self.get_ocx_instance()

        # 로그인
        self.event_slots()
        self.signal_login_commConnect()

        # 계좌정보
        self.get_account_info()


    # 파이썬에서 제어
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    # 이벤트 모음, KOA 개발가이드, void(노란색)
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) # 로그인 버전처리
        self.OnReceiveMsg.connect(self.msg_slot) # 로그인 버전처리
        # self.OnReceiveTrData.connect(self.trdata_slot) # 조회와 실시간데이터처리


    # 로그인 시도
    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect")

        # 이벤트루프 활성화
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    # 로그인 슬롯
    def login_slot(self, errCode):
        print(errors(errCode), "\n")

        # 로그인 완료되면 이벤트루프 종료
        self.login_event_loop.exit()

    # 송수신 메시지
    def msg_slot(self, sScrNo, sRQName, sTrCode, sMsg):
        print("스크린: %s, 요청이름: %s, TR코드: %s, 메시지: %s" % (sScrNo, sRQName, sTrCode, sMsg))

    # 계좌정보, 로그인 후 사용 가능
    def get_account_info(self):
        self.account_cnt = self.dynamicCall("GetLoginInfo(QString)", "ACCOUNT_CNT")

        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
        self.account_list = account_list.split(";")
        self.account_num = self.account_list[0].rstrip("11")
        
        print("계좌수: %s" % self.account_cnt)
        print("계좌번호: %s" % self.account_num, "\n")

    # TR, 예수금 상세현황 요청
    def detail_account_info(self):
        print("예수금 요청")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, QString, QString)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    # TR 슬롯
    # def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        # ㅇ