import boto3

s3 = boto3.resource('s3')

# Get list of objects for indexing
images=[('afridi.jpg','Shahid Afridi'),
        ('sakib.jpg','Sakib Al Hasan'),
        ('kohli.jpg','Birat Kohli'),
        ('masrafi.jpg','Mashrafe Bin Mortaza'),
        ('ganguli.jpg','Sourav Ganguly')
       ]

# Iterate through list to upload objects to S3   
for image in images:
    file = open(image[0],'rb')
    object = s3.Object('taifur12345bucket',image[0])
    ret = object.put(Body=file,
                    Metadata={'FullName':image[1]}
                    )
    #print(image[0])
    #print(image[1])
