"""
Implement a strategy that takes a long position when the Williams %R crosses above -80 and the ATR is above its 10-day moving average. 
Take a short position when the Williams %R crosses below -20 and the ATR is below its 10-day moving average.

"""

from blueshift.api import (
    symbol,
    schedule_function,
    date_rules,
    time_rules,
    get_datetime,
    order_target_percent
)

import numpy as np
import talib
from datetime import datetime,time

def initialize(context):

    context.security=[symbol('GNFC'),symbol('HCLTECH'),symbol('HDFCAMC'),symbol('HDFCBANK'),symbol('HDFCLIFE'),symbol('HAVELLS'),symbol('HEROMOTOCO')]

    schedule_function(
        square_off,
        date_rule=date_rules.every_day(),
        time_rule=time_rules.market_close(minutes=2)
    )


def before_trading_start(context,data):

    context.current_position=np.zeros(len(context.security))
    context.entryprice=np.zeros(len(context.security))
    context.sl=np.zeros(len(context.security))
    context.tp=np.zeros(len(context.security))
    context.avg=[0 for i in range(0,len(context.security))]
    for i in range(0,len(context.security)):
        df=data.history(context.security[i],['open','high','close','low'],50,'1d')
        atr=talib.ATR(df['high'],df['low'],df['close'],timeperiod=10)
        l=list(atr[-10:])
        a=sum(l)/len(l)
        context.avg[i]=a
        


def handle_data(context,data):
    
    ct=get_datetime()
    tz=ct.tzinfo
    st=datetime.combine(ct.date(),time(9,30),tzinfo=tz)
    et=datetime.combine(ct.date(),time(15,28),tzinfo=tz)
    if ct>st and ct<et:
        for i in range(0,len(context.security)):
            cp=data.current(context.security[i],'close')
            df=data.history(context.security[i],['open','high','close','low'],30,'1m')
            wilr = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=30)
            w=wilr[-1]
            tatr=talib.ATR(df['high'],df['low'],df['close'],timeperiod=30)
            atr=tatr[-1]
            if context.current_position[i]==0:
                if w>=-80 and atr>context.avg[i]:
                    order_target_percent(context.security[i],1/len(context.security))
                    context.current_position[i]=1
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*0.85
                    context.sl[i]=context.entryprice[i]*1.15
                
                elif w<=-20 and atr<context.avg[i]:
                    order_target_percent(context.security[i],-1/len(context.security))
                    context.current_position[i]=-1
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*1.15
                    context.tp[i]=context.entryprice[i]*0.85
            
            elif context.current_position[i]==1:

                if cp>=context.tp[i] or cp<=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
                
                elif cp>context.entryprice[i] and cp<context.tp[i]:
                    context.sl[i]=cp*0.85
            
            elif context.current_position[i]==-1:

                if cp<=context.tp[i] or cp>=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
                
                elif cp<context.entryprice[i] and cp>context.tp[i]:
                    context.sl[i]=cp*1.15
    
    else:
        pass

def square_off(context,data):
    for i in range(0,len(context.security)):
        order_target_percent(context.security[i],0)
        context.current_position[i]=0
        context.entryprice[i]=0
        context.sl[i]=0
        context.tp[i]=0



                

            
