# K-Means Clustering Algorithm

# Take the points from dataset

We load our points from dataset and plot them.

<img src="https://mubaris.com/static/output_3_1-4c6211a1b91ae3ee4db8398827c7b1bd-6d179.png"/>

# Take K random centroids

Now we take K random centroids for the first iteration and plot them (green stars).

<img src="https://mubaris.com/static/output_6_1-f56d3eb34d9f5af08e06e39f2b66b234-6d179.png"/>

# Iterate while error is zero

At this point, foreach K clusters, we take a point P_i that have less distance from centroid C_i. Then we take the point in the same cluster of P_i, and foreach points, we take the mean point, it become the new centroid of the cluster. We iterate this operations while the error ( distance between C_i-1 and C_i ) is different from zero.

<img src="https://mubaris.com/static/output_8_1-22829fe4b686e2e588529dd6a8df75b6-6d179.png"/>
