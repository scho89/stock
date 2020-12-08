from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *



class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스 입니다.")

        ###### Event loops
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_mystock_event_loop = None
        self.detail_account_mystock_event_loop = QEventLoop()    
        ########

        #### Variables
        self.account_num = None
        self.use_money = 0
        self.use_money_rate = 0.5 #예수금 사용 비율
        self.stock_counts = 2 # 거래할 종목 수
        self.account_stock_dict ={}

        #### Screen number
        self.screen_my_info = "2000"
        self.screen_chart_data = "4000"




        ######################

        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()
        self.detail_account_mystock()

        self.calculator_fnc() # 종목 분석용, 임시로 실행



    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')


    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)


    def login_slot(self,errCode):
        print(errCode)
        print(errors(errCode))

        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()


    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(";")[0]

        print("나의 보유 계좌번호 %a" % self.account_num)




    def detail_account_info(self):
        print("예수금을 요청하는 부분")
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분","2")
        self.dynamicCall("CommRqData(String, String, int, String)","예수금상세현황요청","opw00001","0",self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()


    def detail_account_mystock(self,sPrevNext="0") :
        print("계좌평가 잔고내역 요청 부분")
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분","2")
        self.dynamicCall("CommRqData(String, String, int, String)","계좌평가잔고내역요청","opw00018",sPrevNext,self.screen_my_info)

        
        self.detail_account_mystock_event_loop.exec_()

    def trdata_slot(self,sScrNo, sRQName,sTrCode,SRecordName,sPrevNext):
        '''
        :param sScrNo : 스크린번호
        :param sRQName: 요청에서 지은 이름
        :param sTrCode: 요청 id / tr코드
        :param sRecordName :사용안함
        :param sPrevNext: 다음 페이지 유무 ?
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "예수금")
            print('예수금 %s' % int(deposit))

            self.use_money = int(deposit) * self.use_money_rate
            self.use_money = self.use_money * self.stock_counts




            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "출금가능금액")
            print(ok_deposit)

            joomoon = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "주문가능금액")
            print("주문가능금액 %s"% int(joomoon))

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총 매입금액 %s" %total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            print("총 수익률 %s" %total_profit_loss_rate_result)

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode,sRQName)
            cnt = 0
            for i in range(rows):
                stock_code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"종목번호")
                stock_name = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"종목명")                
                stock_margin = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"평가손익")
                stock_profit = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"수익률(%)")
                stock_buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"매입가")
                stock_quntity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"보유수량")
                stock_avail_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"매매가능수량")
                stock_total_cost = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"수수료합")

                stock_code = stock_code.strip()[1:]
                stock_name = stock_name.strip()
                stock_margin = int(stock_margin.strip())
                stock_profit = float(stock_profit.strip())
                stock_buy_price = int(stock_buy_price.strip())
                stock_quntity = int(stock_quntity.strip())
                stock_avail_quantity = int(stock_avail_quantity.strip())
                stock_total_cost = int(stock_total_cost.strip())

                if stock_code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict[stock_code]={}
                    self.account_stock_dict[stock_code]['종목명'] = stock_name
                    self.account_stock_dict[stock_code]['평가손익'] = stock_margin
                    self.account_stock_dict[stock_code]['수익률(%)'] = stock_profit
                    self.account_stock_dict[stock_code]['매입가'] = stock_buy_price
                    self.account_stock_dict[stock_code]['보유수량'] = stock_quntity
                    self.account_stock_dict[stock_code]['매매가능수량'] =stock_avail_quantity
                    self.account_stock_dict[stock_code]['수수료합'] = stock_total_cost

                    cnt+=1
            print("계좌에 가지고 있는 종목 수 : %s" %cnt)
            print(self.account_stock_dict)

            if sPrevNext =="2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_mystock_event_loop.exit()

        elif sRQName == "주식일봉차트조회":
            print("일봉데이터 요청")


    def get_code_list_by_market(self, market_code):
        '''
        return stock code list
        '''
        
        code_list = self.dynamicCall("GetCodeListByMarket(QString)",market_code)
        code_list = code_list.split(";")[:-1]

        return code_list


    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10")
        print("코스닥 종목 수 %s" %len(code_list))

        for idx,code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)",self.screen_chart_data)
            print("%s / %s : KOSDAQ stock code : %s is updating..."%(idx+1,len(code_list),code))
            
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext = "0"):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)


        self.dynamicCall("CommRqData(QString, QString, int, QString)","주식일봉차트조회","opw10081",sPrevNext,self.screen_chart_data)



        

            


