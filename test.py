from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model

X = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
vector = [1, 2, 3]
predict= [[2, 2, 2]]

# transform input 
poly = PolynomialFeatures(degree=2)
X_ = poly.fit_transform(X)
predict_ = poly.fit_transform(predict)

# pass to predictor object
clf = linear_model.LinearRegression()
clf.fit(X_, vector)

print clf.predict(predict_)