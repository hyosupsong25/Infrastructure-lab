# CloudFormation
템플릿(JSON, YAML)을 통해 리소스를 모델링하고 설정하여 리소스 관리 시간을 줄이도록 도움을 주는 서비스

### Template
AWS 리소스 구축을 위한 블루프린트로 사용되는 JSON 또는 YAML 형식의 텍스트 파일
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: A sample template
Resources:
  MyEC2Instance:
    Type: "AWS::EC2::Instance"
    Properties:
      ImageId: "ami-0ff8a91507f77f867"
      InstanceType: t2.micro
      KeyName: testkey
      BlockDeviceMappings:
        -
          DeviceName: /dev/sdm
          Ebs:
            VolumeType: io1
            Iops: 200
            DeleteOnTermination: false
            VolumeSize: 20
  MyEIP:
    Type: AWS::EC2::EIP
    Properties:
      InstanceId: !Ref MyEC2Instance
```
### Template의 특징
