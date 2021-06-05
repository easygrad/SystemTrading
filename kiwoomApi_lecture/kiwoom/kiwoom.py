from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *
from config.errorCode import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()

        print("Kiwoom 클래스 입니다.")

        ### eventloop 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ###

        ### 스크린번호 모음
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        ###

        ### 변수 모음
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        ###

        ### 계좌 관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ###

        ### 종목 분석용
        self.calcul_data = []
        ###

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()
        self.detail_account_mystock()
        self.not_concluded_account()

        self.calculator_fnc() # 종목 분석용, 임시용

    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot) # [OnEventConnect()이벤트] 로그인 처리 이벤트입니다. 성공이면 인자값 nErrCode가 0이며 에러는 다음과 같은 값이 전달됩니다.
        self.OnReceiveTrData.connect(self.trdata_slot) # [OnReceiveTrData() 이벤트] 요청했던 조회데이터를 수신했을때 발생됩니다. 앞으로 모든 TR데이터는 여기에 받을 것

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

    def detail_account_info(self):
        print("예수금을 요청하는 부분")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, String, String)", "예수금상세현황요청", "opw00001", "0", self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    # 매수한 종목들 불러오기
    def detail_account_mystock(self, sPrevNext="0"): # 0은 초기값이고, 만약 다음 페이지 있으면 첫 페이지 탐색 후 2로 지정해주는 코드 만들어줘야함
        print("계좌평가 잔고내역 요청")

        self.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(String, String)", "비밀번호", "")
        self.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.dynamicCall("CommRqData(String, String, String, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    # [ opt10075 : 미체결요청 ]
    def not_concluded_account(self, sPrevNext="0"):
        print("미체결 요청")

        self.dynamicCall("SetInputValue(QString, Qstring)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, Qstring)", "매매구분", "0") # 0: 전체
        self.dynamicCall("SetInputValue(QString, Qstring)", "체결구분", "1") # 1: 미체결
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): # sScrNo 스크린번호, sRQName 내가 요청했을때 지은 이름, sTrCode 요청 id tr코드, sRecordName 사용안함, sPrevNext 다음 페이지가 있는지(다음 페이지 없으면 0, 보유종목 20개 이상일 경우 2)
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % deposit)
            print("예수금 형변환 %s" % int(deposit))

            # 예수금 중 매수할 금액 액수
            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 %s" % ok_deposit)
            print("출금가능금액 형변환 %s" % int(ok_deposit))

            self.detail_account_info_event_loop.exit()

        if sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            
            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            

            # 계좌에 있는 보유 종목 정보 가져오기 KOA [GetRepeatCnt() 함수] 데이터 수신시 멀티데이터의 갯수(반복수)를 얻을수 있습니다. 
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName) # 최대 20개밖에 카운트 못 함
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "종목번호")
                code = code.strip()[1:] # 종목코드 앞에 알파벳 하나 붙는 거 빼고 필요함

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "종목명")
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "보유수량")
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "매입가")
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "수익률(%)")
                current_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "현재가")
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "매매가능수량")

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})                
                
                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity)

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({"매매가능수량": possible_quantity})

                cnt += 1 # 종목 몇개인지 확인하기 위해

            print("계좌에 가지고 있는 종목 %s개" % cnt)
            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                print("총매입금액 %s" % total_buy_money_result)
                print("총수익률(%%) %s" % total_profit_loss_rate_result) # %는 문자열 반환하는데 쓰이기 때문에 %%로 표기, %로 쓰면 오류 발생
                # print("총수익률(%s) %s" % ("%", total_profit_loss_rate_result))
                # 총수익률 000000000.00 이런 식으로 반환되는데, int로 변환이 안되는듯?? 0일 때만 그런건가? float 사용해주면 될듯?
                print("계좌에 가지고 있는 종목 %s" % self.account_stock_dict)

                self.detail_account_info_event_loop.exit()

        if sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)\
            
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "종목코드") # 계좌평가잔고내역과 다르게 앞에 알파벳 안 붙는다고 함
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "주문상태")
                order_quntity = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "주문구분")
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "체결량")

                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quntity = int(order_quntity.strip())
                order_price = int(order_price.strip().lstrip('+').lstrip('-'))
                order_gubun = order_gubun.strip()
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())
                
                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                self.not_account_stock_dict[order_no].update({"종목코드": code})
                self.not_account_stock_dict[order_no].update({"종목명": code_nm})
                self.not_account_stock_dict[order_no].update({"주문번호": order_no})
                self.not_account_stock_dict[order_no].update({"주문상태": order_status})
                self.not_account_stock_dict[order_no].update({"주문수량": order_quntity})
                self.not_account_stock_dict[order_no].update({"주문가격": order_price})
                self.not_account_stock_dict[order_no].update({"주문구분": order_gubun})
                self.not_account_stock_dict[order_no].update({"미체결수량": not_quantity})
                self.not_account_stock_dict[order_no].update({"체결량": ok_quantity})

                print("미체결 종목: %s" % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()

        if "주식일봉차트조회" == sRQName:
            
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print(cnt)

            # 한 번 조회하면 600일치 조회 가능
            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, Qstring)", sTrCode, sRQName, i, "저가")

                data.append("") # 나중에 GetCommDataEx 로 600일 한 번에 불러올 때 받는 데이터와 형태 맞춰주기 위함. 굳이 안 해도 된다고 함
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())

                self.calcul_data.append(data.copy())


            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:

                # 이벤트 루프 종료 전 조건에 맞는 종목 뽑고 종료
                print("총 일수 %s" % len(self.calcul_data))
                
                pass_success = False
                
                # 120일 이평선을 그릴 만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120

                    # 오늘 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        print("오늘 주가가 120일 이평선에 걸쳐있는지 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])

                    # 과거 일봉들이 120일 이평선볻가 밑에 있는지 확인하다가 120일 이평선보다 위에 있으면 계산 진행
                    if bottom_stock_price == True:
                        moving_average_price_prev = 0
                        price_top_moving = False

                        idx = 1
                        while True:
                            if len(self.calcul_data[idx:]) < 120: # 120일치가 있는지 계속 확인
                                print("120일치가 없음!")
                                break
                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20: # 20일 정도 밑에 있었는지 확인
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                print("120일 이평선 위에 있는 일봉 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                        # 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선의 가격이 최근일자 이평선 가격보다 낮은 것 확인됨")
                                print("포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨")
                                pass_success = True

                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print("조건부 통과 못함")

                self.calcul_data.clear()

                self.calculator_event_loop.exit()


    # KOA 개발가이드 기타함수 종목정보관련함수 [GetCodeListByMarket() 함수]
    def get_code_list_by_market(self, market_code):
        
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1] # 마지막 값은 지우겠다

        return code_list

    # 종목분석 실행용 함수
    def calculator_fnc(self):
        
        code_list = self.get_code_list_by_market("10") # 10: 코스닥
        print("코스닥 개수 %s" % len(code_list))

        for idx, code in enumerate(code_list):

            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # 이전 스크린번호 요청 끊고 간다고?
            print("%s / %s : 코스닥 종목 코드 : %s 업데이트 중" % (idx+1, len(code_list), code))

            self.day_kiwoom_db(code = code)


    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

        QTest.qWait(3600) # PyQt에서 time sleep 사용시 GUI 멈춤 현상, 이벤트 실행을 중지하기 때문에 QTest.qWait(msec) 사용 -> from PyQt5.QtTest import *

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
        
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)

        self.calculator_event_loop.exec_()
        