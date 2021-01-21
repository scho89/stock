import os
import sys

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from config.kiwoomType import *
from PyQt5.QtTest import *



class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스 입니다.")

        self.realType = RealType()
        
        ###### Event loops
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_mystock_event_loop = None
        self.detail_account_mystock_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()    
        ########

        #### Variables
        self.account_num = None
        self.use_money = 0
        self.use_money_rate = 0.5 #예수금 사용 비율
        self.stock_counts = 2 # 거래할 종목 수
        self.account_stock_dict ={}
        self.request_waiting_time = 3600 # 일봉 데이터 요청 시 딜레이

        self.calcul_data = [] # 종목 분석을 위한 데이터 저장용
        self.portfolio_stock_dict={}
        self.jango_dict={}
        self.not_account_stock_dict={}

        #### Screen number
        self.screen_my_info = "2000"
        self.screen_chart_data = "4000"
        self.screen_real_stock="5000" # 종목별 할당할 스크린 번호
        self.screen_meme_stock="6000" # 종목별 할당할 주문용 스크린 번호
        self.screen_start_stop_real ="1000" #장 시작여부 확인

        self.screen_condition_search = "7000"

        ######################

        self.get_ocx_instance()
        self.event_slots()
        self.realtime_event_slots()

        ####

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() # 예수금 요청
        self.detail_account_mystock() # 계좌평가 잔고내역 요청
        self.not_concluded_account() # 미체결 요청
        

        #self.calculator_fnc() # 종목 분석용, 임시로 실행

        self.read_code()
        self.screen_number_setting()

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',self.realType.REALTYPE['장시작시간']['장운영구분'],'0') #장 시작 여부

        for code in self.portfolio_stock_dict.keys():
            screen_num = self.portfolio_stock_dict[code]['스크린번호']
            fids = self.realType.REALTYPE['주식체결']['체결시간']
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code,fids,'1') #장 시작 여부
            print("실시간 등록 : %s, 스크린번호: %s, fid번호: %s" %(code,screen_num, fids))


    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')


    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)
        self.OnReceiveMsg.connect(self.msg_slot)


    def realtime_event_slots(self):
        self.OnReceiveRealData.connect(self.realtime_data_slot)
        self.OnReceiveChejanData.connect(self.chejan_slot)
        #self.OnReciveHoga.connect(self.hoga_slot)


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


    def not_concluded_account(self, sPrevNext='0'):
        self.dynamicCall("SetInputValue(QString, QString)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)","체결구분",'1')
        self.dynamicCall("SetInputValue(QString, QString)","매매구분",'0')
        self.dynamicCall("CommRqData(QString, QString, int, QString)","실시간미체결요청",'opt10075',sPrevNext,self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

        
        
        



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
            print("출금가능금액 %s"% int(ok_deposit))

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
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"보유수량")
                stock_avail_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"매매가능수량")
                stock_total_cost = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"수수료합")

                stock_code = stock_code.strip()[1:]
                stock_name = stock_name.strip()
                stock_margin = int(stock_margin.strip())
                stock_profit = float(stock_profit.strip())
                stock_buy_price = int(stock_buy_price.strip())
                stock_quantity = int(stock_quantity.strip())
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
                    self.account_stock_dict[stock_code]['보유수량'] = stock_quantity
                    self.account_stock_dict[stock_code]['매매가능수량'] =stock_avail_quantity
                    self.account_stock_dict[stock_code]['수수료합'] = stock_total_cost

                    cnt+=1
            print("계좌에 가지고 있는 종목 수 : %s" %cnt)
            print(self.account_stock_dict)

            if sPrevNext =="2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_mystock_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            rows = self.dynamicCall('GetRepeatCnt(QString, QString)',sTrCode,sRQName)

            for i in range(rows):
                stock_code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"종목코드")
                stock_name = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"주문상태")
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"주문구분")
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"체결량")

                stock_code = stock_code.strip()
                stock_name = stock_name.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no]={}                


                self.not_account_stock_dict[order_no]['종목코드']=stock_code
                self.not_account_stock_dict[order_no]['종목명']=stock_name
                self.not_account_stock_dict[order_no]['주문번호']=order_no
                self.not_account_stock_dict[order_no]['주문상태']=order_status
                self.not_account_stock_dict[order_no]['주문수량']=order_quantity
                self.not_account_stock_dict[order_no]['주문가격']=order_price
                self.not_account_stock_dict[order_no]['주문구분']=order_gubun
                self.not_account_stock_dict[order_no]['미체결수량']=not_quantity
                self.not_account_stock_dict[order_no]['체결량']=ok_quantity

                print('미체결 종목 : %s' % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()


        elif sRQName == "주식일봉차트조회":
            
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,0,"종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청"% code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode,sRQName)
            print("%s 일 봉 조회 완료" % cnt)

            for i in range(cnt) :
                data = []
                current_price = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"현재가")
                trading_volume = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"거래대금")
                trading_date = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"일자")
                start_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"시가")
                high_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"고가")
                low_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"저가")
                end_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"전일종가")
                
                data.append("")
                data.append(current_price.strip())
                data.append(trading_volume.strip())
                data.append(trading_value.strip())
                data.append(trading_date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append(end_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            print(self.calcul_data)

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code,sPrevNext=sPrevNext)

            else:
                self.calculator_event_loop.exit()



    def get_code_list_by_market(self, market_code):
        '''
        return stock code list
        '''
        
        code_list = self.dynamicCall("GetCodeListByMarket(QString)",market_code)
        code_list = code_list.split(";")[:-1]

        return code_list


    def calculator_fnc(self):
        #종목 분석 알고리즘이 들어간다.

        code_list = self.get_code_list_by_market("10")
        print("코스닥 종목 수 %s" %len(code_list))

        for idx,code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)",self.screen_chart_data)
            print("%s / %s : KOSDAQ stock code : %s is updating..."%(idx+1,len(code_list),code))
            
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext = "0"):

        QTest.qWait(self.request_waiting_time)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)


        self.dynamicCall("CommRqData(QString, QString, int, QString)","주식일봉차트조회","opt10081",sPrevNext,self.screen_chart_data)

        self.calculator_event_loop.exec_()


    def read_code(self):
        if os.path.exists("files/condition_stocks.txt"):
            f = open("files/condition_stocks.txt","r",encoding="utf8")

            lines = f.readlines()
            for line in lines:

                if line !="":
                    ls = line.split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = abs(int(ls[2].strip()))

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name,"현재가":stock_price}})
            print(self.portfolio_stock_dict)    
            f.close()

    def screen_number_setting(self):
        screen_overwrite=[]

        #계좌평가잔고내역에 있는 종목
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        #for order_number in 

        
        #포트폴리오에 있는 종목
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)


        #스크린번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt%50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt%50) == 0:
                meme_screen +=1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code]["스크린번호"]=str(self.screen_real_stock)
                self.portfolio_stock_dict[code]["주문용스크린번호"]=str(self.screen_meme_stock)

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code]={}
                self.portfolio_stock_dict[code]["스크린번호"]=str(self.screen_real_stock)
                self.portfolio_stock_dict[code]["주문용스크린번호"]=str(self.screen_meme_stock)

            cnt+=1

        print(self.portfolio_stock_dict)

    def realtime_data_slot(self,sCode,sRealType,sRealData):
        print(sCode,sRealType,sRealData)
        if sRealType == "장시작시간":
            print('sRealType 장시작시간')
            fid = self.realType.REALTYPE['장시작시간']['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)",sCode,fid)

            if value =='0':
                print('장 시작 전')
            elif value =='3':
                print('장 시작')
            elif value =='2':
                print('장 종료 / 동시호가')
            elif value =='4':
                print('3시30분 장 종료')  


                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(String, String)", self.portfolio_stock_dict[code]['스크린번호'])

                    QTest.qWait(5000)               

                
                #self.file_delete()
                #self.calculator_fnc()

                sys.exit()


            else:
                print('그외.......... 한밤중인가?')

        elif sRealType == "주식체결":
            print(sCode)
            a=self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['체결시간']) ## HHMMSS string
            b=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['현재가']))) 
            c=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['전일대비'])))
            d=float(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['등락율']))
            e=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])))
            f=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])))
            g=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['거래량'])))
            h=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['누적거래량'])))
            i=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['고가'])))
            j=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['시가'])))
            k=abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode, self.realType.REALTYPE[sRealType]['저가'])))
            
            if sCode not in self.portfolio_stock_dict:
                self.portfolio_stock_dict['sCode']={}

            self.portfolio_stock_dict[sCode].update({"체결시간": a})            
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})        

            print(self.portfolio_stock_dict[sCode])

            # 계좌 잔고 평가 내역에 있고 오늘 산 잔고에는 없을 경우
            if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                print('%s %s'%('신규매도를 한다',sCode))

                order_stock = self.account_stock_dict[sCode]

                meme_rate = (b - order_stock['매입가']) /order_stock['매입가'] * 100

                
                if order_stock['매매가능수량'] > 0 and ( meme_rate >5 or meme_rate < -5):
                    order_success = self.dynamicCall("SendOrder(QString,QString,QString, int,QString, int, int, QString,QString)",["신규매도" ,self.portfolio_stock_dict[sCode]['주문용스크린번호'],self.account_num, 2, sCode, order_stock['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'],""])

                    if order_success ==0:
                        print("매도주문 전달 성공")
                        del self.account_stock_dict[sCode]

                    else:
                        print("매도주문 전달 실패")

            #오늘 산 잔고에 있을경우
            elif sCode in self.jango_dict.keys():
                print('%s %s'%('신규매도를 한다2',sCode))

                jd = self.jango_dict[sCode]

                meme_rate = (b - jd['매입단가']) /jd['매입단가'] * 100

                
                if jd['주문가능수량'] > 0 and ( meme_rate >5 or meme_rate < -5):
                    order_success = self.dynamicCall("SendOrder(QString,QString,QString, int,QString, int, int, QString,QString)",["신규매도" ,self.portfolio_stock_dict[sCode]['주문용스크린번호'],self.account_num, 2, sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'],""])

                    if order_success ==0:
                        print("매도주문 전달 성공")
                        # self.logging.logger.debug("매도주문 전달 성공")

                    else:
                        print("매도주문 전달 실패")
                        # self.logging.logger.debug("매도주문 전달 실패")


            #등락율 2.0% 이상 / 오늘 산 잔고에 없을 경우
            elif d > 2.0 and sCode not in self.jango_dict.keys():
                print('%s %s'%('신규매수를 한다',sCode))

                quantity= int((self.use_money * 0.1)/e)

                order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",["신규매수" ,self.portfolio_stock_dict[sCode]['주문용스크린번호'],self.account_num, 1, sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'],""])

                if order_success ==0:
                    print("매도주문 전달 성공")
                    # self.logging.logger.debug("매도주문 전달 성공")

                else:
                    print("매도주문 전달 실패")
                    # self.logging.logger.debug("매도주문 전달 실패")



            not_meme_list = list(self.not_account_stock_dict)
            for order_num in not_meme_list:
                code = self.not_account_stock_dict[order_num]['종목코드']
                meme_price = self.not_account_stock_dict[order_num]['주문가격']
                not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
                order_gubun = self.not_account_stock_dict[order_num]['주문구분']
                #meme_gubun = self.not_account_stock_dict[order_num]['매도수구분']

                if order_gubun == '매수' and not_quantity >0 and e > meme_price:
                    print('%s %s'%('매수 취소한다',sCode))

                    order_success = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",["매수취소" ,self.portfolio_stock_dict[sCode]['주문용스크린번호'],self.account_num, 3, sCode, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num])


                    if order_success ==0:
                        print("매도주문 전달 성공")
                        # self.logging.logger.debug("매도주문 전달 성공")

                    else:
                        print("매도주문 전달 실패")
                        # self.logging.logger.debug("매도주문 전달 실패")
                        

                elif not_quantity ==0:
                    del self.not_account_stock_dict[order_num]

    def chejan_slot(self, sGubun, nItemCnt, sFIdList):

        if int(sGubun) ==0:
            print('주문체결')

            account_num = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['원주문번호']) # 출력 : defalt use : "0000000"

            order_number = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['주문번호']) # 출력 : 0112315 마지막 주문번호

            order_status = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['주문상태']) # 접수, 확인, 체결
            
            order_quan = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['주문수량']) # 3
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['주문가격']) # 12000
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['미체결수량']) #출력 15, def: 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['주문구분']) # -매도, +매수
            order_gubun = order_gubun.lstrip('+').lstrip('-')

#            meme_gubun = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['매도수구분']) # 매수:2, 매도:1
#            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            chegual_time_str = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['주문/체결시간']) # 출력 151028
            chegual_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['체결가']) # 출력 2110 / def : ""

            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price=int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['체결량']) # 출력 5 / def:''
            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity=int(chegual_quantity)



            current_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['현재가']) # -6010
            current_price = abs(int(current_price))

            first_sell_price =  self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['(최우선)매도호가']) # 출력 -6010
            first_sell_price = abs(int(first_sell_price))

            first_buy_price =  self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['주문체결']['(최우선)매수호가']) 
            first_buy_price = abs(int(first_buy_price))

            ###### 새로 들어온 주문이면 주문 번호 할당 ???
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict[order_number]={}


            self.not_account_stock_dict[order_number]['종목코드'] = sCode
            self.not_account_stock_dict[order_number]['주문번호'] = order_number
            self.not_account_stock_dict[order_number]['종목명'] = stock_name
            self.not_account_stock_dict[order_number]['주문상태'] = order_status
            self.not_account_stock_dict[order_number]['주문수량'] = order_quan
            self.not_account_stock_dict[order_number]['주문가격'] = order_price
            self.not_account_stock_dict[order_number]['미체결수량'] = not_chegual_quan
            self.not_account_stock_dict[order_number]['원주문번호'] = origin_order_number
            self.not_account_stock_dict[order_number]['주문구분'] = order_gubun
            self.not_account_stock_dict[order_number]['주문/체결시간'] = chegual_time_str
            self.not_account_stock_dict[order_number]['체결가'] = chegual_price
            self.not_account_stock_dict[order_number]['체결량'] = chegual_quantity
            self.not_account_stock_dict[order_number]['현재가'] = current_price
            self.not_account_stock_dict[order_number]['(최우선)매도호가'] = first_sell_price
            self.not_account_stock_dict[order_number]['(최우선)매수호가'] = first_buy_price

            print(self.not_account_stock_dict)

        elif int(sGubun) ==1 :
            print('잔고')

            account_num = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['종목코드'])[1:]
            
            stock_name = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['현재가']) # -6010
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['보유수량']) # 3
            stock_quan = int(stock_quan)

            avail_quan = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['주문가능수량']) # 3
            avail_quan = int(avail_quan)

            buy_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['매입단가']) #
            buy_price = int(buy_price)

            total_buy_price = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['총매입가']) #
            total_buy_price = int(total_buy_price)


#            meme_gubun = self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['매도수구분']) # 매수:2, 매도:1
#            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun]

            first_sell_price =  self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['(최우선)매도호가']) # 출력 -6010
            first_sell_price = abs(int(first_sell_price))

            first_buy_price =  self.dynamicCall("GetChejanData(int)",self.realType.REALTYPE['잔고']['(최우선)매수호가']) 
            first_buy_price = abs(int(first_buy_price))

            ###### 
            if sCode not in self.jango_dict.keys():
                self.jango_dict[sCode]={}


            self.jango_dict[sCode]['현재가'] = current_price
            self.jango_dict[sCode]['종목코드'] = sCode
            self.jango_dict[sCode]['종목명'] = stock_name
            self.jango_dict[sCode]['보유수량'] = stock_quan
            self.jango_dict[sCode]['주문가능수량'] = avail_quan
            self.jango_dict[sCode]['매입단가'] = buy_price
            self.jango_dict[sCode]['총매입가'] = total_buy_price
            # self.jango_dict[sCode]['매도매수구분'] = meme_gubun
            self.jango_dict[sCode]['(최우선)매도호가'] = first_sell_price
            self.jango_dict[sCode]['(최우선)매매호가'] = first_buy_price

            print(self.jango_dict)


            if stock_quan==0:
                del self.jango_dict[sCode]
                self.dynamicCall("SetRealRemove(QString, QString)",self.portfolio_stock_dict[sCode]['스크린번호'],sCode)

    #송수신 메시지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s tr코드: %s ---%s" % (sScrNo, sRQName, sTrCode, msg))

    #파일 삭제
    def file_delete(self):
        if os.path.isfile("files/condition_stock.txt"):
            os.remove("files/condition_stock.txt")


    ########################### 조건검색 관련

    def 



