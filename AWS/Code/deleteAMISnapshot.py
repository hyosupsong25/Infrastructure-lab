from datetime import datetime, timezone
import boto3
import aws_util as aws
import argparse

VERSION = 0.1

parser = argparse.ArgumentParser(description=f"Delete AMIs, Snapshots Related Instance Id ver.{VERSION}")
parser.add_argument("-a", '--accessKey', dest="accessKey", type=str, required=True, help="accessKey of account")
parser.add_argument("-s", '--secretKey', dest="secretKey", type=str, required=True, help="secretKey of account")
parser.add_argument("-i", '--instanceId', dest="instanceId", type=str, required=True, help="Instance Id to delete")
parser.add_argument("-r", '--region', dest="region", type=str, required=True, help="region of instance")
parser.add_argument("-d", '--day', dest="day", type=int, required=True, help="delete ami, snapshot created before this value days")
parser.add_argument('--dryrun', dest="dryrun", action='store_true', help="이 옵션을 사용하면 DryRun 모드 on")
args = parser.parse_args()

# accessKey, secretKey, region를 입력받아 해당 계정의 AMI, Snapshot 을 조회 or 삭제할 수 있는 클래스
class EC2:
    def __init__(self, accessKey, secretKey, region):
        '''
        :param region: 대상 리소스가 존재하는 Region
        '''
        self.__client = boto3.client('ec2', aws_access_key_id=accessKey, aws_secret_access_key=secretKey, region_name=region)
        self.__account = boto3.client('sts', aws_access_key_id=accessKey, aws_secret_access_key=secretKey, region_name=region).get_caller_identity().get('Account')
        #self.__account = account

    # InstanceId를 파라미터로 입력받아 해당 인스턴스의 AMI를 배열에 담아 반환
    def getImagesByInstanceId(self, instanceId):
        '''
        :param instanceId: 인스턴스 Id
        :return: 파라미터로 입력받은 인스턴스 ID를 원본 인스턴스로 하는 AMI 리스트
        '''
        images = [
            {
                'ImageId': image['ImageId'],
                'Name': image['Name'],
                'CreationDate': (
                        datetime.now() - datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')).days
            }
            for image in self.__client.describe_images(Owners=[self.__account])['Images']
        ]
        imagesById = []
        for image in images:
            if instanceId in image['Name']:
                imagesById.append(image)
        return imagesById

    # 해당 계정의 모든 AMI를 배열에 담아 반환
    def getImages(self):
        '''
        :return:해당 계정의 리전에 있는 모든 AMI 리스트
        '''
        images = [
            {
                'ImageId': image['ImageId'],
                'Name': image['Name'],
                'CreationDate': (
                        datetime.now() - datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')).days
            }
            for image in self.__client.describe_images(Owners=[self.__account])['Images']
        ]
        return images

    # 입력된 AMI 리스트 중 생성된 지 day를 넘는 AMI를 삭제
    def getImagesByDay(self, instanceId, day):
        '''
        :param instanceId: AMI의 인스턴스 Id
        :param day: images 리스트 중에 생성된 지 day 초과되는 항목들을 검색
        '''
        images = self.getImagesByInstanceId(instanceId)
        imagesByDay = []
        for image in images:
            if image['CreationDate'] >= day:
                imagesByDay.append(image)
        return imagesByDay

    # 입력된 AMI를 삭제
    def deregisterImage(self, image, dryrun=True):
        '''
        :param image: 삭제할려는 Image(dict)
        :param dryrun: True=DryRun Mode On / False = DryRun Mode Off (Default : True)
        '''
        try:
            self.__client.deregister_image(ImageId=image['ImageId'], DryRun=dryrun)
            print(f"AMI,{image['ImageId']},created before {image['CreationDate']}days")
        except Exception as e:
            print(f"AMI {image['ImageId']} delete is failed")
            raise e

    # 입력된 AMI 리스트를 전부 삭제
    def deregisterImages(self, images, dryrun=True):
        '''
        :param images: 삭제할 AMI 리스트
        :param dryrun: True=DryRun Mode On / False = DryRun Mode Off (Default : True)
        '''
        for image in images:
            self.deregisterImage(image, dryrun)

    # InstanceId를 파라미터로 입력받아 해당 인스턴스의 Snapshot을 배열에 담아 반환
    def getSnapshotsByInstanceId(self, instanceId):
        '''
        :param instanceId: 인스턴스 Id
        :return: 파라미터로 입력받은 인스턴스 ID를 원본 인스턴스로 하는 Snapshot 리스트
        '''
        snapshots = [
            {
                'SnapshotId': snapshot['SnapshotId'],
                'StartTime': (datetime.now(timezone.utc) - snapshot['StartTime']).days,
                'Description': snapshot['Description']
            }
            for snapshot in self.__client.describe_snapshots(OwnerIds=[self.__account])['Snapshots']
        ]
        snapshotsById = []
        for snapshot in snapshots:
            if instanceId in snapshot['Description']:
                snapshotsById.append(snapshot)
        return snapshotsById

    # 해당 계정의 모든 Snapshot을 배열에 담아 반환
    def getSnapshots(self):
        '''
        :return: 해당 계정의 리전에 있는 모든 Snapshot 리스트
        '''
        snapshots = [
            {
                'SnapshotId': snapshot['SnapshotId'],
                'StartTime': (datetime.now(timezone.utc) - snapshot['StartTime']).days
            }
            for snapshot in self.__client.describe_snapshots(OwnerIds=[self.__account])['Snapshots']
        ]
        return snapshots

    # 입력된 Snapshot 리스트 중 생성된 지 day를 넘는 Snapshot을 삭제
    def getSnapshotsByDay(self, instanceId, day):
        '''
        :param instanceId: 인스턴스 Id
        :param day: Snapshot 리스트 중에 생성된 지 day 초과되는 항목 검색
        '''
        snapshots = self.getSnapshotsByInstanceId(instanceId)
        snapshotsByDay = []
        for snapshot in snapshots:
            if snapshot['StartTime'] >= day:
                snapshotsByDay.append(snapshot)
        return snapshotsByDay

    # 입력된 Snapshot 리스트를 전부 삭제
    def deleteSnapshots(self, snapshots, dryrun=True):
        '''
        :param snapshots: 삭제할 Snapshot 리스트
        :param dryrun: True=DryRun Mode On / False = DryRun Mode Off (Default : True)
        '''
        for snapshot in snapshots:
            self.deleteSnapshot(snapshot, dryrun)


    # 입력된 Snapshot을 삭제
    def deleteSnapshot(self, snapshot, dryrun=True):
        '''
        :param snapshot: 삭제할 Snapshot
        :param dryrun:True=DryRun Mode On / False = DryRun Mode Off (Default : True)
        '''
        try:
            self.__client.delete_snapshot(SnapshotId=snapshot['SnapshotId'], DryRun=dryrun)
            print(f"Snapshot,{snapshot['SnapshotId']},created before {snapshot['StartTime']}days")
        except Exception as e:
            print(f"Snapshot {snapshot['SnapshotId']} delete is failed")
            raise e


def main(accessKey, secretKey, region, instanceId, day, dryRun):
    try:
        ec2 = EC2(accessKey=accessKey, secretKey=secretKey, region=region)
    except Exception as e:
        print("ec2 생성 중 에러 발생")
        print(e)
        exit(1)

    images = []
    snapshots = []

    try:
        images = ec2.getImagesByDay(instanceId=instanceId, day=day)
        snapshots = ec2.getSnapshotsByDay(instanceId=instanceId, day=day)
    except Exception as e:
        print(e)
        exit(1)

    print(f"[TOTAL RESULT] {instanceId} : AMI {len(images)}EA, Snapshot{len(snapshots)}EA")
    print("[DETAIL RESULT]")
    # image
    try:
        aws.pprint(images)
        ec2.deregisterImages(images=images, dryrun=dryRun)
    except Exception as e:
        print("AMI 생성 및 삭제 중 에러 발생")
        print(e)
        exit(1)

    # snapshot
    try:
        aws.pprint(snapshots)
        ec2.deleteSnapshots(snapshots=snapshots, dryrun=dryRun)
    except Exception as e:
        print("Snapshot 생성 및 삭제 중 에러 발생")
        print(e)
        exit(1)

if __name__ == "__main__":
    main(args.accessKey, args.secretKey, args.region, args.instanceId, args.dryRun)