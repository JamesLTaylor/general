ratio = 1.0/3
(rows, cols, _) = rotated.shape

if edgeType[0]==0 and edgeType[2]==0:
    y1 = rows * ratio/(1+2*ratio)
    y2 = rows - y1
elif edgeType[0]==0 and not edgeType[2]==0:
    y1 = rows * ratio/(1+ratio)
    y2 = rows-1
elif not edgeType[0]==0 and edgeType[2]==0:
    y1 = 1
    y2 = rows-ratio/(1+ratio)
else:
    y1 = 1
    y2 = rows-1
    