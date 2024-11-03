from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, AutoScaling
from diagrams.aws.network import ELB, Route53HostedZone, VPC, PrivateSubnet, PublicSubnet, InternetGateway
from diagrams.aws.database import RDS
from diagrams.aws.integration import SQS
from diagrams.aws.database import ElastiCache
from diagrams.aws.security import ACM, WAF
from diagrams.onprem.client import Users

# Enhanced styling attributes
graph_attr = {
    "fontsize": "45",
    "bgcolor": "#F5F5F5",
    "splines": "spline",
    "pad": "3.0",
    "ranksep": "2.0",
    "nodesep": "2.0"
}

vpc_cluster_attr = {
    "bgcolor": "#E6F3FF",  # Lighter blue for VPC
    "penwidth": "3",
    "fontsize": "20",
    "margin": "30"
}

subnet_cluster_attr = {
    "bgcolor": "#EBF3FA",
    "penwidth": "2",
    "fontsize": "16",
    "margin": "20"
}

with Diagram("Java Application - AWS Migration (Lift & Shift)", 
            show=False, 
            filename="java_aws_migration",
            graph_attr=graph_attr,
            direction="LR"):
            
    # Users and Internet Gateway
    users = Users("End Users")
    igw = InternetGateway("Internet Gateway")
    waf = WAF("WAF")
    cert = ACM("SSL/TLS\nCertificate")

    # VPC Cluster with increased size
    with Cluster("Virtual Private Cloud (VPC)", graph_attr=vpc_cluster_attr):
        
        # Horizontal Public Subnet
        with Cluster("Public Subnet - AZ1 & AZ2", graph_attr=subnet_cluster_attr):
            elb = ELB("Application\nLoad Balancer")
            route53 = Route53HostedZone("Route 53\nPrivate Hosted Zone")

            # Auto Scaling Group in public subnet
            with Cluster("Auto Scaling Group"):
                tomcat_instances = [
                    EC2("Tomcat Instance 1\nAZ-1"),
                    EC2("Tomcat Instance 2\nAZ-2")
                ]

        # Horizontal Private Subnet
        with Cluster("Private Subnet - Backend Services", graph_attr=subnet_cluster_attr):
            # Backend services in a horizontal layout
            with Cluster("Backend Services Layer"):
                memcached = ElastiCache("Memcached\nCluster")
                mysql = RDS("MySQL\nMulti-AZ")
                rabbitmq = SQS("RabbitMQ\nCluster")

        # External connections with user flow
        users >> Edge(label="HTTPS", color="darkgreen") >> igw
        igw >> waf >> cert >> elb
        
        # Load balancer to instances
        elb >> Edge(label="HTTPS", color="darkgreen") >> tomcat_instances

        # DNS resolution
        tomcat_instances >> Edge(
            label="DNS Resolution", 
            style="dashed",
            color="darkblue"
        ) >> route53

        # Backend connections
        for instance in tomcat_instances:
            instance >> Edge(
                label="Security Group", 
                color="darkred",
                style="bold"
            ) >> memcached
            
            instance >> Edge(
                label="Security Group", 
                color="darkred",
                style="bold"
            ) >> mysql
            
            instance >> Edge(
                label="Security Group", 
                color="darkred",
                style="bold"
            ) >> rabbitmq

        # Backend inter-service communications
        memcached - Edge(color="blue", style="dotted") - mysql
        mysql - Edge(color="blue", style="dotted") - rabbitmq

