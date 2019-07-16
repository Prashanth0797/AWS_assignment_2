import boto3

ec2 = boto3.resource ( 'ec2', region_name = 'us-east-1' )
ec2Client = boto3.client   ( 'ec2', region_name = globalVars['us-east-1'] )
vpc = ec2.create_vpc ( CidrBlock = '10.240.0.0/22')
print(vpc.id)

#The subnets are created
az1_pvtsubnet = vpc.create_subnet( CidrBlock ='10.240.0.0/24' , AvailabilityZone = 'us-east-1a' )
az1_pubsubnet = vpc.create_subnet( CidrBlock = '10.240.1.0/24', AvailabilityZone = 'us-east-1a' )
az2_pvtsubnet = vpc.create_subnet( CidrBlock ='10.240.2.0/25' , AvailabilityZone = 'us-east-1b' )
az2_pubsubnet = vpc.create_subnet( CidrBlock = '10.240.2.128/25', AvailabilityZone = 'us-east-1b' )
az3_pvtsubnet = vpc.create_subnet( CidrBlock ='10.240.3.0/25' , AvailabilityZone = 'us-west-1c' )
az3_pubsubnet = vpc.create_subnet( CidrBlock = '10.240.3.128/25', AvailabilityZone = 'us-west-1c' )

#Enabling DNS hostnames
ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsSupport = { 'Value': True } )
ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsHostnames = { 'Value': True } )

#Creating an internet gateway
intGateway  = ec2.create_internet_gateway()
intGateway.attach_to_vpc( VpcId = vpc.id )

#Creating a route table for public traffic
pubRouteTable = ec2.create_route_table( VpcId = vpc.id )
pubRouteTable.associate_with_subnet( SubnetId = az1_pubsubnet.id )
pubRouteTable.associate_with_subnet( SubnetId = az2_pubsubnet.id )
pubRouteTable.associate_with_subnet( SubnetId = az3_pubsubnet.id )

# Create another route table for Private traffic
pvtRouteTable = ec2.create_route_table( VpcId = vpc.id )
pvtRouteTable.associate_with_subnet( SubnetId = az1_pvtsubnet.id )
pvtRouteTable.associate_with_subnet( SubnetId = az2_pvtsubnet.id )
pvtRouteTable.associate_with_subnet( SubnetId = az3_pvtsubnet.id )


#Route for the internet gateway.
intRoute = ec2Client.create_route( RouteTableId = pubRouteTable.id , DestinationCidrBlock = '0.0.0.0/0' , GatewayId = intGateway.id )


''''
#Tagging our resources  
vpc.create_tags( Tags = ['Key':'Name', 'Value':globalVars['Project']['Value']+'-vpc'})
az1_pvtsubnet.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-az1-private-subnet'}] )
az1_pubsubnet.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-az1-public-subnet'}] )
az1_sparesubnet.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-az1-spare-subnet'}] )
az2_pvtsubnet.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-az2-private-subnet'}] )
az2_pubsubnet.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-az2-public-subnet'}] )
az2_sparesubnet.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-az2-spare-subnet'}] )
intGateway.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-igw'}] )
pubRouteTable.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-rtb'}] )
pvtRouteTable.create_tags( Tags = [{'Key':'Name', 'Value':globalVars['Project']['Value']+'-rtb'}] )

'''
#Creating the security groups
pubSecGrp = ec2.create_security_group( DryRun = False,
                              GroupName='pubSecGrp',
                              Description='Public_Security_Group',
                              VpcId= vpc.id
                            )
pvtSecGrp = ec2.create_security_group( DryRun = False,
                              GroupName='pvtSecGrp',
                              Description='Private_Security_Group',
                              VpcId= vpc.id
                                       )
'''                          
#Tagging the security groups
pubSecGrp.create_tags(Tags=[{'Key': 'Name' ,'Value': globalVars['Project']['Value']+'-public-security-group'}])
pvtSecGrp.create_tags(Tags=[{'Key': 'Name' ,'Value': globalVars['Project']['Value']+'-private-security-group'}])

'''

#Giving the rules for the security groups
ec2Client.authorize_security_group_ingress( GroupId = pubSecGrp.id,
                                            IpProtocol= 'tcp',
                                            FromPort=80,
                                            ToPort=80,
                                            CidrIp='0.0.0.0/0'
                                            )
ec2Client.authorize_security_group_ingress( GroupId = pvtSecGrp.id,
                                            IpPermissions = [{'IpProtocol': 'tcp',
                                                               'FromPort': 80,
                                                               'ToPort': 80,
                                                               'UserIdGroupPairs': [{ 'GroupId':pubSecGrp.id}]
                                                             }]
                                           )
ec2Client.authorize_security_group_ingress( GroupId  = pubSecGrp.id ,
                                        IpProtocol= 'tcp',
                                        FromPort=443,
                                        ToPort=443,
                                        CidrIp='0.0.0.0/0'
                                        )
ec2Client.authorize_security_group_ingress( GroupId  = pubSecGrp.id ,
                                        IpProtocol= 'tcp',
                                        FromPort=22,
                                        ToPort=22,
                                        CidrIp='0.0.0.0/0'
                                        )



""""
def cleanAll(resourcesDict=None):

    intGateway.delete()

    # Delete Subnets
    az1_pvtsubnet.delete()
    az1_pubsubnet.delete()
    az1_sparesubnet.delete()
    az2_pvtsubnet.delete()
    az2_pubsubnet.delete()
    az2_sparesubnet.delete()

    vpc.delete()

"""

