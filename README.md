# ELB Consul

This Docker container allows you to (de)register EC2 instances belonging to a specific Consul service with an Amazon Elastic Load Balancer (ELB).

## Usage

The `elb-consul` container takes all of its configuration from environment variables.

* `AWS_ACCESS_KEY_ID` ... Your AWS [access key](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
* `AWS_SECRET_ACCESS_KEY` ... Your AWS [secret key](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)
* `AWS_REGION` ... The AWS region that your load balancer is located in
* `ELB_NAME` ... The exact name of your load balancer
* `CONSUL_SERVER` ... The IP:PORT to connect to the Consul server (eg: 172.1.6.1.2:8500)
* `CONSUL_SERVICE` ... The exact name of the Consul service you want to monitor

You could run only one instance of `elb-consul` per `ELB_NAME` / `CONSUL_SERVICE` pair but for high availability purpose, it is recommanded to run two of them.
Internally the Docker image uses a Consul Lock to make sure that only one `elb-consul` will be active at anytime.
