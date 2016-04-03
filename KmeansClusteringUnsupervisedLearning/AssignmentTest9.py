#import statements.
from flask import Flask, render_template, request, url_for,redirect

import argparse
import os
import tinys3
import sys
import boto
from boto.s3.connection import S3Connection
import pylab
from pylab            import plot,show
from numpy            import vstack,array
from numpy.random     import rand
from scipy.cluster.vq import kmeans, vq, whiten
import csv
import urllib2
application = Flask(__name__)

@application.route('/')
def home():
    #if request.method == 'GET':
    image=""
    return render_template('home.html')

@application.route('/request', methods=['POST'])
def displayResult():
    access_key='AKIAIN3P5BURO6GZKNEQ'
    secret_key='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'
    #conn = tinys3.Connection('AKIAIN3P5BURO6GZKNEQ','1eSWO1AcYvOMi2/R+v0Dj5LAzsNDQS9BnOlWD7KS',tls=True)
    conn1 = boto.connect_s3(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        #host = 'objects.dreamhost.com',
        is_secure=False,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )
   # noOfCluster =input("Please Enter No of Cluster: ")
    #K = 3
    noOfCluster=0
    noOfCluster =long(request.form['cluster'])
    
    data_arr = []
    meal_name_arr = []

    url='https://storage.googleapis.com/cloudbucket786/imptry4.csv'
    response=urllib2.urlopen(url)
    reader = csv.reader(response)
    i=0
    for row in reader:
##        if i==0:
##            i=i+1
##        else:
            if row[5] is None:
                row[5]=0
            if row[5]=='':
                row[5]=0
            if "," in row[6] :  
                rowVal=row[6].split(",")
                row[6]=rowVal[0]+''+rowVal[1]
                row[6]=float(row[6])    
            if row[6]=='':
                row[6]=0
            if row[6]=='N' :
                row[6]=0
                
            data_arr.append([float(x) for x in row[5:]])
            meal_name_arr.append([row[0]])

    
    #print data_arr
    
    data = vstack( data_arr )
    
    meal_name = vstack(meal_name_arr)
    # normalization
    data = whiten(data)#Before running k-means, it is beneficial to rescale each feature dimension of the observation set with whitening.
    #Each feature is divided by its standard deviation across all observations to give it unit variance.

    # computing K-Means with K (clusters)
    centroids, distortion = kmeans(data,noOfCluster)
##    print "distortion = " + str(distortion)
    
    # assign each sample to a cluster
    idx,_ = vq(data,centroids)
    #print "here"
    #print centroids
    # some plotting using numpy's logical indexing
    listOfColor=['ob','or','og','oc','om','ok','oy']
    for index in range(noOfCluster):
        plot(data[idx==index,0], data[idx==index,1],listOfColor[index])
    for index in range(noOfCluster):
        result_names = meal_name[idx==index, 0]
##        print "================================="
##        print "Cluster " + str(index+1)
##        for name in result_names:
##            print name

    plot(centroids[:,0],
         centroids[:,1],
         'oy',markersize=8)
    pylab.savefig('temp.png')
    pylab.clf()
    noOfCluster=0
    index=0
    f = open('temp.png','rb')
   
#Exits the loop
    image=os.path.abspath('temp.png')
    bucket = conn1.get_bucket('cloudabhitejcs6331')
    key=bucket.new_key('cluster.jpg')
    key.set_contents_from_file(f)
    key.set_canned_acl('public-read')
    hello_key=bucket.get_key('cluster.jpg')
    hello_url = hello_key.generate_url(0, query_auth=False, force_http=True)
    image=hello_url
    
    #return redirect("http://localhost:8883")
    return render_template('home.html',image=image)

if __name__ == '__main__':
  application.run( 
        host="localhost",
        port=int("8882"),debug=True
  )
# Run the app :)
##if __name__ == '__main__':
##  application.run(
##        "0.0.0.0",debug=True
##  )

