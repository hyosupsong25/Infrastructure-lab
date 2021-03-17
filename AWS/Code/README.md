# Code Description  
### [deleteAMISnapshot.py](https://github.com/hyosupsong25/Infrastructure-lab/blob/main/AWS/Code/deleteAMISnapshot.py)
instance id, day를 입력받아 instance와 연관된 AMI, Snapshot 중 생성된 지 day 이상된 자원 삭제  
* 조건: AMI Name, Snapshot Description에 instance id가 존재

**usage**  
> python deleteAMISnapshot.py -a [Access Key] -s [Secret Key] -r [Region] -i [Instance Id] -d [day] <--dryrun>

-a : instance가 존재하는 계정의 Access Key (required)  
-s : instance가 존재하는 계정의 Secret Key (required)  
-r : 대상 instance의 region (required)  
-i : 삭제하려는 AMI, Snapshot의 원본 instance id (required)  
-d : 삭제하고자 하는 기준 날짜 (required)  
--dryrun : 해당 옵션 셜정 시 dryrun 모드로 코드 수행  