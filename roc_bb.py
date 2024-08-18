"""
Create a strategy that takes a long position when the Price Rate of Change is above zero and the closing price is above the upper Bollinger Band. 
Take a short position when the Price Rate of Change is below zero and the closing price is below the lower Bollinger Band.

"""

from blueshift.api import (
    symbol,
    schedule_function,
    date_rules,
    time_rules,
    get_datetime,
    order_target_percent
)

from datetime import datetime,time
import numpy as np
import talib

def initialize(context):

    context.security=[symbol('JKCEMENT'),symbol('JSWSTEEL'),symbol('LTIM'),symbol('JUBLFOOD'),symbol('KOTAKBANK'),symbol('LT'),symbol('LTTS')]

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

def handle_data(context,data):

    ct=get_datetime()
    tz=ct.tzinfo
    st= datetime.combine(ct.date(),time(9,30),tzinfo=tz)
    et=datetime.combine(ct.date(),time(15,28),tzinfo=tz)

    if ct>st and ct<et:
        for i in range(0,len(context.security)):
            cp=data.current(context.security[i],'close')
            df=data.history(context.security[i],['open','high','close','low'],30,'1m')
            troc=talib.ROC(df['close'],timeperiod=30)
            roc=troc[-1]
            upper,middle,lower=talib.BBANDS(df['close'],timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
            u=upper[-1]
            l=lower[-1]
            if (context.current_position[i]==0):
                if roc>0 and cp>u:
                    order_target_percent(context.security[i],1/len(context.security))
                    context.current_position[i]=1
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*0.85
                    context.tp[i]=context.entryprice[i]*1.15
                
                elif roc<0 and cp<l:
                    order_target_percent(context.security[i],-1/len(context.security))
                    context.current_position[i]=-1
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*1.15
                    context.tp[i]=context.entryprice[i]*0.85
            
            elif (context.current_position[i]==1):
                if cp>=context.tp[i] or cp<=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
                
                elif cp>context.entryprice[i]:
                    context.sl[i]=cp*0.85
            
            elif (context.current_position[i]==-1):
                if cp<=context.tp[i] or cp>=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
                
                elif cp<context.entryprice[i]:
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

