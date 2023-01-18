import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import urllib.request

url = "https://kream-phinf.pstatic.net/MjAyMjEyMjFfMzAg/MDAxNjcxNTk5NTIyMDM2.BHZ4NRB5XVnfavxKeGG70F_URB7hybeUB9ajh00B-Y8g.YA9Rn31U5bR4Ez9ZiNihQCYE21hsNZK4-KGWBQEbDywg.PNG/a_eb5e7e207bbf4e08942e29b428032c73.png?type=l"
resp = urllib.request.urlopen(url)
image = np.asarray(bytearray(resp.read()), dtype='uint8')
image = cv2.imdecode(image, cv2.IMREAD_COLOR)
image = cv2.resize(image, (128,128), interpolation=cv2.INTER_AREA)

cv2.imshow("img", image)
cv2.waitKey(0)
cv2.destroyAllWindows()