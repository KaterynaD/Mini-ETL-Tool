#!/usr/bin/python
import boto3
from botocore.client import ClientError
import yaml
"""
RDSUtility.py - 03.19.16 Kate Drogaieva
The class in this module allows to create an RDS database
"""
#---------------------------------------------------------------------------------------------
class RDSUtility(object):
    """
        RDSUtility class can be used to create MySQL instance
        The configuration parameters must be provided in a YAML resource file
    """
    def __str__(self):
        return self.endpoint+":"+str(self.port)
    def __init__(self,resource):
        """
            Init MySQL parameters using resource file in YAML format
        """
        try:
            with open(resource, "r") as f:
                self.res = yaml.load(f)
            self.DBName=self.res["RDS"]["DBName"],
            self.DBInstanceIdentifier=self.res["RDS"]["DBInstanceIdentifier"]
        except KeyError or IOError:
            sys.exit("Wrong MySQL Parameters")
        self.client=boto3.client("rds",self.res["Region"])
        self.endpoint=""
        self.port=""
        self.GetEndpoint()
        return
#---------------------------------------------------------------------------------------------
    def CreateDBSubnetGroup(self,SubnetIds):
        """
            Creates an instance Subnet Group if ["RDS"]["SubnetGroup"]  exists
            in YAML configuration file
            SubnetIds is a list of public or private subnets from a VPC
            return Subgroup name or default if VPC does not exists
        """
        SubnetGroup="default"
        response = self.client.create_db_subnet_group(
                   DBSubnetGroupName=self.res["RDS"]["SubnetGroup"]["Name"],
                   DBSubnetGroupDescription=self.res["RDS"]["SubnetGroup"]["Description"],
                   SubnetIds=SubnetIds)
        SubnetGroup=response["DBSubnetGroup"]["DBSubnetGroupName"]
        return SubnetGroup
#---------------------------------------------------------------------------------------------
    def CreateDBInstance(self,SubnetIds=[],SecurityGroupId=[]):
        """
            Create a new DB instance acoording to the configuration parameters in YAML resource file
            If there is ["RDS"]["SubnetGroup"] in the resource file
            an instance Subnet Group is created first based on SubnetIds (list) from a VPC
            SecurityGroupId (list) can be used to create the cluster in VPC
        """
        SubnetGroup="default"
        try:
            if self.res["RDS"]["SubnetGroup"]:
                try: #test if a group already exists
                    response = self.client.describe_db_subnet_groups(DBSubnetGroupName=self.res["RDS"]["SubnetGroup"]["Name"])
                    SubnetGroup=self.res["RDS"]["SubnetGroup"]["Name"]
                except ClientError: #group does not exist - create
                    SubnetGroup=self.CreateDBSubnetGroup(SubnetIds)
        except KeyError:
            pass
        PubliclyAccessible=True
        if self.res["RDS"]["PubliclyAccessible"]=="False":
            PubliclyAccessible=False
        response = self.client.create_db_instance(
    DBName=self.res["RDS"]["DBName"],
    DBInstanceIdentifier=self.res["RDS"]["DBInstanceIdentifier"],
    AllocatedStorage=int(self.res["RDS"]["AllocatedStorage"]),
    DBInstanceClass=self.res["RDS"]["DBInstanceClass"],
    Engine=self.res["RDS"]["Engine"],
    MasterUsername=self.res["RDS"]["MasterUsername"],
    MasterUserPassword=self.res["RDS"]["MasterUserPassword"],
    VpcSecurityGroupIds=SecurityGroupId,
    Port=int(self.res["RDS"]["Port"]),
    MultiAZ=True,
    DBSubnetGroupName=SubnetGroup,
    EngineVersion=self.res["RDS"]["EngineVersion"],
    LicenseModel=self.res["RDS"]["License"],
    PubliclyAccessible=PubliclyAccessible,
    StorageType="standard",
    BackupRetentionPeriod=0)
#---------------------------------------------------------------------------------------------
    def DeleteDBInstance(self):
        """
            The function deletes the DB Instance and do not create a final snapshot
        """
        response = self.client.delete_db_instance(
            DBInstanceIdentifier=self.DBInstanceIdentifier,
            SkipFinalSnapshot=True
            )
        return
#---------------------------------------------------------------------------------------------
    def DeleteDBSubgroup(self):
        """
            The function deletes the DB Subnet Group if it exists
        """
        try: #to delete a group if  exists
                response = self.client.delete_db_subnet_group(DBSubnetGroupName=self.res["RDS"]["SubnetGroup"]["Name"])
        except (ClientError,KeyError) as e: #group does not exist or not configured in the resource file - pass
            pass
        return
#---------------------------------------------------------------------------------------------
    def GetEndpoint(self):
        """
            The function set endpoint and port variable and returns 0 if no errors
            or 1 if the DB is not available
        """
        try:
            response = self.client.describe_db_instances(
            DBInstanceIdentifier=self.DBInstanceIdentifier
            )
            try:
                self.endpoint=response["DBInstances"][0]["Endpoint"]["Address"]
                self.port=response["DBInstances"][0]["Endpoint"]["Port"]
                return 0
            except KeyError:
                return 1
        except ClientError: #Cluster does not exists
            return 1
#---------------------------------------------------------------------------------------------
    def CheckStatus(self):
        """
            The same as GetEndpoint
        """
        return self.GetEndpoint()
#---------------------------------------------------------------------------------------------
    def WaitForCreation(self):
        """
            The function waits while the DB instance is creating It can take significant amount of time
        """
        waiter = self.client.get_waiter("db_instance_available")
        try:
            waiter.wait(DBInstanceIdentifier=self.DBInstanceIdentifier)
            self.GetEndpoint
            #DB Instance is available
            result=0
        except ClientError: #DB Instance does not exists
            result=1
        return result
#---------------------------------------------------------------------------------------------
    def WaitForDeletion(self):
        """
            The function waits while the DB Instance is deleting It can take significant amount of time
        """
        waiter = self.client.get_waiter("db_instance_deleted")
        try:
            waiter.wait(DBInstanceIdentifier=self.DBInstanceIdentifier)
            result=0
        except ClientError: #DB Instance does not exists
            result=1
        return result
#---------------------------------------------------------------------------------------------
#=============================================================================================
#============= Usage example==================================================================
if __name__ == "__main__":
    import sys
    import VPCUtility
    ResourceFile="ProjectResources.yml"
    
    def initVPC():
        MyVPC=VPCUtility.VPCUtility(ResourceFile)
        print MyVPC.VpcName
        if not MyVPC.Vpc:
            print "Creating a new VPC..."
            MyVPC.create_vpc()
            MyVPC.Vpc.modify_attribute(
             EnableDnsHostnames={"Value":True}
              )
        else:
            print "VPC exists"
        return MyVPC
    def init(VPC=None,isPublic=True):
        c=RDSUtility(ResourceFile)
        if not(c.endpoint):
            print "Creating DB instance. It will take several minutes..."
            if not(VPC):
            #Create standalone cluster
                c.CreateDBInstance()
            else:
            #Create Cluster in VPC
                if isPublic:
                    SubnetId=MyVPC.GetPublicSubnets()
                else:
                    SubnetId=MyVPC.GetPrivateSubnets()
                SecurityGroupId=MyVPC.GetSecurityGroupId("RDSAll")
                c.CreateDBInstance(SubnetId,SecurityGroupId)
            c.WaitForCreation()
            c.CheckStatus()
            if c.CheckStatus()==0:
                print "DB Instance is available: %s" %c
            else:
                print "DB Instance is not available..."
        else:
            print "DB Instance is available: %s" %c
        return c

    try:
        ResourceFile=sys.argv[1]
    except:
        ResourceFile ="ProjectResources.yml"

    Action = sys.argv[2]

        
    if Action=="Create":
        c=init()
    elif Action=="CreateVPC":
        MyVPC=initVPC()
    elif Action=="CreateInVPCPublic":
        MyVPC=initVPC()
        c=init(VPC=MyVPC,isPublic=True)
    elif Action=="CreateInVPCPrivate":
        MyVPC=initVPC()
        c=init(VPC=MyVPC,isPublic=False)
    elif Action=="RDSAll":
        MyVPC=initVPC()
        print "Creating RDS SecurityGroup..."
        RDSSecGrp=MyVPC.create_security_group("RDSAll")
        print "Security group created with ID= %s" %RDSSecGrp
    elif Action=="DeleteVPC":
        MyVPC=initVPC()
        print "Deleting VPC..."
        MyVPC.delete_vpc()
    elif Action=="Delete":
        c=init()
        print "Deleting DB Instance. It will take several minutes..."
        c.DeleteDBInstance()
        c.WaitForDeletion()
        c.DeleteDBSubgroup()
    elif Action=="Status":
        c=init()
        if c.CheckStatus()==0:
            print c
        else:
            print "DB Instance is not available..."

