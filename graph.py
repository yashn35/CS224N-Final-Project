import matplotlib.pyplot as plt
from scipy.stats import pearsonr

x = [69.2, 72, 71, 75.8, 70.8, 74, 76 ,76.6, 74.2, 76.2]
y = [-33 , -33.4 ,-30.8 , -29.6 ,-32 ,-33.8 , -25.8 ,-30.6,-28.4,-27.8]

corr, _ = pearsonr(x, y)
print('Pearsons correlation: %.3f' % corr)
plt.scatter(x, y)
plt.xlabel('Expertise (Ao5)')
plt.ylabel('Influence (Ao5)')
plt.title('Effect of Expertise on Influence')
plt.show()
