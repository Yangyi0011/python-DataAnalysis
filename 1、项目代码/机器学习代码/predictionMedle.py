import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# 中文问题
from matplotlib.font_manager import FontProperties
# 深度学习模块sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


font = FontProperties(fname="/Users/apple/PycharmProjects/text1/msyh.ttc",size=10)

data = pd.read_csv("datas.csv")
data1=data[['directorCapacity','screenwriterCapacity','starringCapacity','movie_rating','boxOffice（万元）']]
data2=data[['directorCapacity','screenwriterCapacity','starringCapacity','boxOffice（万元）']]
x =data[['directorCapacity','screenwriterCapacity','starringCapacity']]
y =data[['movie_rating']]
y1 =data[['boxOffice（万元）']]
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=0)
x_train1,x_test1,y_train1,y_test1 = train_test_split(x,y1,test_size=0.2,random_state=0)
# 评分线性模型
model = LinearRegression()
model.fit(x_train,y_train)

# 票房预测模型
model1 = LinearRegression()
model1.fit(x_train1,y_train1)
# 《爱情公寓》评分预测
directorCapacity=6.2666667
starring = 6
screen = 6.8
X=[[directorCapacity,starring,screen]]
print(model.score(x_test,y_test))
print(model.predict(X))
print(model1.score(x_test1,y_test1))
print(model1.predict(X))

# 最佳阵容
daoyan = 8.2212
yanyuan = 8.994 
bianju = 8.555528
X1=[[daoyan,yanyuan,bianju]]
print(model.predict(X1))
print(model1.predict(X1))
