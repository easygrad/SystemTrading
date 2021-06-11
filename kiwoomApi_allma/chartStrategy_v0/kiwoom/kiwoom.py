import os
import sys
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from config.errorCode import *

import numpy as np
import matplotlib.pyplot as plt


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        # 이벤트루프 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.target_stock_event_loop = QEventLoop()
        self.chart_event_loop = QEventLoop()

        # 스크린번호 모음
        self.screen_my_info = "2000"
        self.screen_my_hold_stock = "2001"
        self.screen_my_target_stock = "2002"
        self.screen_my_chart = "3000"

        # 변수 모음
        self.chartData_my_target_stock = {}

        # 타겟종목
        self.my_target_stock_list = ["122630", "233740"]

        # 파이썬 제어
        self.get_ocx_instance()

        # 로그인
        self.event_slots()
        self.signal_login_commConnect()

        # 계좌정보
        self.get_account_info()

        # TR 요청
        self.detail_account_info()
        self.my_target_stock()

        for i in range(len(self.my_target_stock_list)):
            self.minute_chart(i)


    # 파이썬에서 제어
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    # 이벤트 모음, KOA 개발가이드, void(노란색)
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) # 로그인 버전처리
        self.OnReceiveMsg.connect(self.msg_slot) # 로그인 버전처리
        self.OnReceiveTrData.connect(self.trdata_slot) # 조회와 실시간데이터처리


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
        self.account_num_11 = self.account_list[0]
        
        print("계좌수: %s" % self.account_cnt)
        print("계좌번호: %s" % self.account_num, "\n")

    # TR, 예수금 상세현황 요청
    # [CommRqData() 함수] 조회요청 함수입니다. (sRQName // 사용자 구분명 임의 지정, sTrCode // 조회하려는 TR이름, nPrevNext // 연속조회여부, sScreenNo // 화면번호)
    def detail_account_info(self):
        print("예수금상세현황")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num_11)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, QString, QString)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()


    # 관심종목정보요청
    # [CommKwRqData() 함수] 한번에 100종목까지 조회할 수 있는 복수종목 조회함수 입니다. 함수인자로 사용하는 종목코드 리스트는 조회하려는 종목코드 사이에 구분자';'를 추가해서 만들면 됩니다.
    # CommKwRqData(BSTR sArrCode // 조회하려는 종목코드 리스트, BOOL bNext // 연속조회 여부 0:기본값, 1:연속조회(지원안함), int nCodeCount // 종목코드 갯수 int nTypeFlag // 0:주식 종목, 3:선물옵션 종목, BSTR sRQName // 사용자 구분명, BSTR sScreenNo // 화면번호)
    def my_target_stock(self):
        print("관심종목정보")
        my_target_stock_codes = ""
        for i in range(len(self.my_target_stock_list)):
            my_target_stock_codes += self.my_target_stock_list[i].strip()
            if i+1 == len(self.my_target_stock_list):
                my_target_stock_codes = my_target_stock_codes
            elif i+1 < len(self.my_target_stock_list):
                my_target_stock_codes += ";"
        self.dynamicCall("CommKwRqData(QString, QString, int, int, QString, QString)", my_target_stock_codes, "0", len(my_target_stock_codes), 0, "관심종목정보요청", self.screen_my_target_stock)

        self.target_stock_event_loop.exec_()


    # 실시간, 분봉차트조회요청
    def minute_chart(self, i):
        print("주식분봉차트조회 [ %s ]" % str(i+1))

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.my_target_stock_list[i])
        self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, QString, QString)", "주식분봉차트조회요청", "opt10080", "0", self.screen_my_chart)

        self.chart_event_loop.exec_()


    # TR 슬롯
    # [GetCommData() 함수] OnReceiveTRData()이벤트가 발생될때 수신한 데이터를 얻어오는 함수, (strTrCode // TR 이름, strRecordName // 레코드이름(sRQName으로 사용하기도 하나봄..), nIndex // nIndex번째, strItemName // TR에서 얻어오려는 출력항목이름)
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        # 예수금상세현황
        if sRQName == "예수금상세현황요청":
            # 예수금
            curr_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            curr_deposit = int(curr_deposit)
            print("예수금: %s" % curr_deposit)

            # 출금가능금액
            withdraw_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            withdraw_deposit = int(withdraw_deposit)
            print("출금가능금액: %s" % withdraw_deposit)

            # 주문가능금액
            possible_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "주문가능금액")
            possible_deposit = int(possible_deposit)
            print("주문가능금액: %s" % possible_deposit)

            print("\n")
            self.detail_account_info_event_loop.exit()

        if sRQName == "관심종목정보요청":
            
            # 관심종목수
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            target_stocks = [] # 타겟종목 리스트 생성

            # 타겟종목 코드, 이름 입력
            for i in range(cnt):
                target_stock = []
                
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code = code.strip()
                name = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                name = name.strip()

                target_stock.append(code)
                target_stock.append(name)
                
                target_stocks.append(target_stock)

            print("타겟종목: %s" % target_stocks)

            print("\n")
            self.target_stock_event_loop.exit()

        if sRQName == "주식분봉차트조회요청":
            
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("종목코드: %s" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("분봉개수: %s" % cnt)

            # 분봉데이터 입력
            stock_price_series_minute = []
            for i in range(cnt):
                stock_price_minute = []

                time = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결시간")
                stock_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                
                stock_price_minute.append(time.strip())
                stock_price_minute.append(stock_price.strip().lstrip("+").lstrip("-"))
                stock_price_minute.append(volume.strip())
                stock_price_series_minute.append(stock_price_minute)

            print("분봉데이터: \n%s" % stock_price_series_minute[:10])

            # 딕셔너리 지정
            self.chartData_my_target_stock.update({code: stock_price_series_minute})

            # 차트 그리기 오류 발생...
            # plt.title("주가")
            # plt.xlabel("시간")
            # plt.ylabel("주가")
            # plt.grid()
            
            # y_value = np.array(stock_price_series_minute).T[1]
            # plt.plot(y_value)
            # plt.show()
            
            print("\n")
            self.chart_event_loop.exit()